from compiler import ast, ir
from compiler.symtab import SymTab
from compiler.types import Bool, Int, Type, Unit
from compiler.ir import IRVar, Label, Source
from typing import List

def generate_ir(
    # 'root_types' parameter should map all global names
    # like 'print_int' and '+' to their types.
    root_types: dict[IRVar, Type],
    root_expr: ast.Expression
) -> list[ir.Instruction]:
    var_types: dict[IRVar, Type] = root_types.copy()
    labels: dict[str, list[Label]] = {}

    # 'var_unit' is used when an expression's type is 'Unit'.
    var_unit = IRVar('unit')
    var_types[var_unit] = Unit
    global_var_n = len (var_types)

    def new_var(t: Type) -> IRVar:
        # Create a new unique IR variable and
        # add it to var_types
        reg_name = f"x{len(var_types) - global_var_n + 1}"
        var = IRVar(reg_name)
        var_types[var] = t
        return var
    
    def new_label(loc: Source, name: str) -> Label:
        # create a new Label that can be used as destination for jumps.
        if name in labels:
            labels[name].append(Label(loc, f"{name}{len(labels[name])}"))
        else:
            labels[name] = [Label(loc, name)]
        return labels[name][-1]

    # We collect the IR instructions that we generate
    # into this list.
    ins: list[ir.Instruction] = []

    # This function visits an AST node,
    # appends IR instructions to 'ins',
    # and returns the IR variable where
    # the emitted IR instructions put the result.
    #
    # It uses a symbol table to map local variables
    # (which may be shadowed) to unique IR variables.
    # The symbol table will be updated in the same way as
    # in the interpreter and type checker.
    def visit(st: SymTab[IRVar], expr: ast.Expression) -> IRVar:
        loc = expr.location

        match expr:
            case ast.Literal():
                # Create an IR variable to hold the value,
                # and emit the correct instruction to
                # load the constant value.
                match expr.value:
                    case bool():
                        var = new_var(Bool)
                        ins.append(ir.LoadBoolConst(loc, expr.value, var))
                    case int():
                        var = new_var(Int)
                        ins.append(ir.LoadIntConst(loc, expr.value, var))
                    case None:
                        var = var_unit
                    case _:
                        raise Exception(f"{loc}: unsupported literal: {type(expr.value)}")

                # Return the variable that holds
                # the loaded value.
                return var

            case ast.Identifier():
                # Look up the IR variable that corresponds to
                # the source code variable.
                return st.read(expr.name)

            case ast.VariableDeclaration():
                st.declare(expr.variable.name)
                st.assign(expr.variable.name, new_var(expr.variable.type))
                return visit(st, expr.variable)

            case ast.BinaryOp():
                
                match expr.op:
                    case '=':
                        var_right = visit(st, expr.right)
                        var_left = visit(st, expr.left)
                        ins.append(ir.Copy(loc, var_right, var_left))
                        return var_left if type(expr.left) != ast.VariableDeclaration else var_unit
                    case 'and':
                        l_left = new_label(loc, "left_circut")
                        l_right = new_label(loc, "right_eval")
                        l_end = new_label(loc, "and_end")

                        var_left = visit(st, expr.left)
                        
                        ins.append(ir.CondJump(loc, var_left, l_right, l_left))

                        ins.append(l_right)
                        var_right = visit(st, expr.right)
                        var_result = new_var(expr.type)
                        ins.append(ir.Copy(loc, var_right, var_result))
                        ins.append(ir.Jump(loc, l_end))

                        ins.append(l_left)
                        ins.append(ir.LoadBoolConst(loc, False, var_result))
                        ins.append(ir.Jump(loc, l_end))

                        ins.append(l_end)
                        return var_result
                    case 'or':
                        l_left = new_label(loc, "left_circut")
                        l_right = new_label(loc, "right_eval")
                        l_end = new_label(loc, "or_end")
                        
                        var_left = visit(st, expr.left)
                        
                        ins.append(ir.CondJump(loc, var_left, l_left, l_right))

                        ins.append(l_right)
                        var_right = visit(st, expr.right)
                        var_result = new_var(expr.type)
                        ins.append(ir.Copy(loc, var_right, var_result))
                        ins.append(ir.Jump(loc, l_end))

                        ins.append(l_left)
                        ins.append(ir.LoadBoolConst(loc, True, var_result))
                        ins.append(ir.Jump(loc, l_end))

                        ins.append(l_end)
                        return var_result
                    case _:
                        # Ask the symbol table to return the variable that refers
                        # to the operator to call.
                        var_op = st.read(expr.op)
                        # Recursively emit instructions to calculate the operands.
                        var_left = visit(st, expr.left)
                        var_right = visit(st, expr.right)
                        var_result = new_var(expr.type)
                        # Generate variable to hold the result.
                        
                        # Emit a Call instruction that writes to that variable.
                        ins.append(ir.Call(loc, var_op, [var_left, var_right], var_result))
                        return var_result

            case ast.UnaryOp():
                var_op = st.read(f"unary_{expr.op}")
                var_value = visit(st, expr.right)
                var_result = new_var(expr.type)
                ins.append(ir.Call(loc, var_op, [var_value], var_result))
                return var_result

            case ast.Conditional():
                # Create (but don't emit) some jump targets.
                
                # Recursively emit instructions for
                # evaluating the condition.
                
                if expr.op == "if" and expr.second is None:
                    var_cond = visit(st, expr.condition)
                    l_then = new_label(loc, "if_then")
                    l_end = new_label(loc, "if_end")
                    # Emit a conditional jump instruction
                    # to jump to 'l_then' or 'l_end',
                    # depending on the content of 'var_cond'.
                    ins.append(ir.CondJump(loc, var_cond, l_then, l_end))

                    # Emit the label that marks the beginning of
                    # the "then" branch.
                    ins.append(l_then)
                    # Recursively emit instructions for the "then" branch.
                    visit(st, expr.first)

                    # Emit the label that we jump to
                    # when we don't want to go to the "then" branch.
                    ins.append(l_end)
                    # An if expression doesn't return anything, so we
                    # return a special variable "unit".
                    return var_unit
                elif expr.op == "if" and expr.second is not None:
                    var_cond = visit(st, expr.condition)
                    l_then = new_label(loc, "if_then")
                    l_end = new_label(loc, "if_end")
                    # "if-then-else" case
                    l_else = new_label(loc, "if_else")
                    result = new_var(expr.type)
                    ins.append(ir.CondJump(loc, var_cond, l_then, l_else))
                    ins.append(l_then)
                    ins.append(ir.Copy(loc, visit(st, expr.first), result))
                    ins.append(ir.Jump(loc, l_end))
                    ins.append(l_else)
                    ins.append(ir.Copy(loc, visit(st, expr.second), result))
                    ins.append(l_end)
                    # An if-else expression returns what it evaluates.
                    return result
                else:
                    l_while_start = new_label(loc, "while_start")
                    l_while_body = new_label(loc, "while_body")
                    l_while_end = new_label(loc, "while_end")
                    ins.append(l_while_start)
                    var_cond = visit(st, expr.condition)
                    ins.append(ir.CondJump(loc, var_cond, l_while_body, l_while_end))
                    ins.append(l_while_body)
                    visit(st, expr.first)
                    ins.append(ir.Jump(loc, l_while_start))
                    ins.append(l_while_end)
                    # A while expression doesn't return anything, so we
                    # return a special variable "unit".
                    return var_unit
                

            case ast.FunctionCall():
                var_func = st.read(expr.function.name)
                var_params: List[IRVar] = []
                
                for param in expr.parameters:
                    var_params.append(visit(st, param))

                var_result = new_var(expr.type)
                
                ins.append(ir.Call(loc, var_func, var_params, var_result))
                return var_result

            case ast.Block():
                new_st = SymTab(st)
                for expression in expr.expressions:
                    visit(new_st, expression)
                return visit(new_st, expr.result)

            case _:
                raise Exception(f"{loc}: unknown expression.")

    # Convert 'root_types' into a SymTab
    # that maps all available global names to
    # IR variables of the same name.
    # In the Assembly generator stage, we will give
    # definitions for these globals. For now,
    # they just need to exist.
    root_symtab = SymTab[IRVar](parent=None)
    for v in root_types.keys():
        root_symtab.declare(v.name)
        root_symtab.assign(v.name, v)
    # Start visiting the AST from the root.
    var_final_result = visit(root_symtab, root_expr)
    dest = new_var(Unit)
    if var_types[var_final_result] == Int:
        # Emit a call to 'print_int'
        ins.append(ir.Call(root_expr.location,root_symtab.read('print_int'), [var_final_result], dest))
    elif var_types[var_final_result] == Bool:
        # Emit a call to 'print_bool'
        ins.append(ir.Call(root_expr.location,root_symtab.read('print_bool'), [var_final_result], dest))

    return ins
