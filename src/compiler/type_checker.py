import compiler.ast as ast
from typing import Optional, Self, Callable
from compiler.types import Int, Bool, Type, Unit, FunType, Any

class SymTab:
    parent : Optional[Self] = None
    locals: dict
    def __init__(self, parent: Optional[Self] = None):
        self.parent = parent
        self.locals = {}

    def declare(self, variable: str) -> None:
        self.locals[variable] = Any

    def assign(self, variable: str, value: Type) -> None:
        if variable in self.locals:
            self.locals[variable] = value
        elif self.parent is not None:
            self.parent.assign(variable, value)
        else:
            raise Exception(f"Variable '{variable}' is not declared.")

    def read(self, variable: str) -> Type:
        if variable in self.locals:
            return self.locals[variable]
        elif self.parent is not None:
            return self.parent.read(variable)
        else:
            raise Exception(f"Variable '{variable}' is not declared.")

    def initialize_top(self) -> None:
        builtin_functions: dict[str, Type] = {
            'or': FunType([Bool, Bool], Bool),
            'and': FunType([Bool, Bool], Bool),
            '==': FunType([Any, Any], Bool),
            '!=': FunType([Any, Any], Bool),
            '<': FunType([Int, Int], Bool),
            '<=': FunType([Int, Int], Bool),
            '>': FunType([Int, Int], Bool),
            '>=': FunType([Int, Int], Bool),
            '+': FunType([Int, Int], Int),
            '-': FunType([Int, Int], Int),
            '*': FunType([Int, Int], Int),
            '/': FunType([Int, Int], Int),
            '%': FunType([Int, Int], Int),
            'unary_-': FunType([Int], Int),
            'unary_not': FunType([Bool], Bool),
            'if': FunType([Bool, Any, Any], Any),
            'while': FunType([Bool, Any], Unit),
            'unit': Unit
        }

        for variable, var_type in builtin_functions.items():
            self.declare(variable)
            self.assign(variable, var_type)

def typecheck(node: ast.Expression, sym_tab: Optional[SymTab] = None) -> Type:
    if sym_tab is None:
        sym_tab = SymTab()
        sym_tab.initialize_top()

    match node:
        case ast.Literal():
            if isinstance(node.value, bool):
                return Bool
            elif isinstance(node.value, int):
                return Int
            elif node.value is None:
                return Unit
            else:
                raise Exception(f"Unsupported type '{type(node.value)}' for literal.")

        case ast.Identifier():
            return sym_tab.read(node.name)

        case ast.VariableDeclaration():
            sym_tab.declare(node.variable.name)
            return Any

        case ast.BinaryOp():
            t1 = typecheck(node.left, sym_tab)
            t2 = typecheck(node.right, sym_tab)

            if node.op == '=':
                left: ast.Identifier
                if isinstance(node.left, ast.Identifier):
                    if t1 < t2 or not t1 >= t2:
                        raise Exception(f"Left and right of '{node.op}' are of different types. {t1} != {t2}")
                    else:
                        left = node.left  
                elif isinstance(node.left, ast.VariableDeclaration):
                    left = node.left.variable
                else:
                    raise Exception(f"Unsupported type '{t1}' to the left of '{node.op}'.")
                
                sym_tab.assign(left.name, t2)
                return FunType([t1, t2], t2)

            operation = sym_tab.read(node.op)
            if not isinstance(operation, FunType):
                raise Exception(f"'{node.op}' is not a binary function.")
            if t1 > operation.parameters[0]:
                print(t1, operation.parameters[0])
                raise Exception(f"Unsupported type '{t1}' left of '{node.op}'. {operation}")
            if t2 > operation.parameters[1]:
                raise Exception(f"Unsupported type '{t2}' right of '{node.op}'. {operation}")
            else:
                return operation.value

        case ast.UnaryOp():
            t = typecheck(node.right, sym_tab)
            operation = sym_tab.read(f"unary_{node.op}")
            if not isinstance(operation, FunType):
                raise Exception(f"'{node.op}' is not a unary function.")
            if t is not operation.parameters[0]:
                raise Exception(f"Unsupported type '{t}' for '{node.op}' {str(operation)}.")
            else:
                return operation.value

        case ast.FunctionCall():
            func_t = typecheck(node.function, sym_tab)
            param_t = []
            for param in node.parameters:
                param_t.append(typecheck(param, sym_tab))
            
            if not isinstance(func_t, FunType):
                raise Exception(f"Variable '{node.function.name}' is not a function.")
            
            arg_n = len(func_t.parameters)
            if arg_n != len(param_t):
                raise Exception(f"Function '{node.function.name}' received incorrect number of arguments. Expected {arg_n}, but received {len(param_t)}.")
            
            for i in range(arg_n):
                print(func_t.parameters[i], param_t[i])
                if func_t.parameters[i] < param_t[i] or not func_t.parameters[i] >= param_t[i]:
                    raise Exception(f"Function '{node.function.name}' argument number {i+1} is incorrect type. Expected '{func_t.parameters[i]}', but received '{param_t[i]}'.")
            
            return func_t.value

        case ast.Block():
            local_sym_tab = SymTab(sym_tab)
            for expr in node.expressions:
                typecheck(expr, local_sym_tab)
            return typecheck(node.result, local_sym_tab)

        case ast.Conditional():
            t1 = typecheck(node.condition, sym_tab)
            t2 = typecheck(node.first, sym_tab)
            t3 = None
            if t1 != Bool:
                raise Exception(f"Expected condition to be of type 'Bool', but received '{t1}'.")
            params = [t1, t2]
            if node.second is not None:
                t3 = typecheck(node.second, sym_tab)
                params.append(t3)
            
            arg_n = len(params)
            
            if node.op == 'if':
                if arg_n == 3:
                    if t2 != t3:
                        raise Exception(F"Expected 'if-else' expressions to be same type, but received '{t2} != {t3}'.")
                elif arg_n != 2:
                    raise Exception(f"Conditional '{node.op}' received incorrect number of arguments. Expected 2 or 3, but received {arg_n}.")
                return t2
            elif node.op == 'while':
                if arg_n != 2:
                    raise Exception(f"Conditional '{node.op}' received incorrect number of arguments. Expected 2, but received {arg_n}.")
                return Unit
            else:
                raise Exception(f"'{node.op}' is not a conditional.")

        case _:
            raise Exception(f"Unkown expression {node}")