import compiler.ir as ir
import dataclasses
from typing import Callable

class Locals:
    """Knows the memory location of every local variable."""
    _var_to_location: dict[ir.IRVar, str]
    _stack_used: int

    def __init__(self, variables: list[ir.IRVar]) -> None:
        self._var_to_location = {}
        self._stack_used = 0
        for var in variables:
            self._stack_used += 8
            self._var_to_location.update({var : f"-{self._stack_used}(%rbp)"}) 

    def get_ref(self, v: ir.IRVar) -> str:
        """Returns an Assembly reference like `-24(%rbp)`
        for the memory location that stores the given variable"""
        return self._var_to_location[v]

    def stack_used(self) -> int:
        """Returns the number of bytes of stack space needed for the local variables."""
        return self._stack_used


def get_all_ir_variables(instructions: list[ir.Instruction], ignore_funcs: list[str]) -> list[ir.IRVar]:
    result_list: list[ir.IRVar] = []
    result_set: set[ir.IRVar] = set()

    def add(v: ir.IRVar) -> None:
        if v not in result_set and v.name not in ignore_funcs:
            result_list.append(v)
            result_set.add(v)

    for insn in instructions:
        for field in dataclasses.fields(insn):
            value = getattr(insn, field.name)
            if isinstance(value, ir.IRVar):
                add(value)
            elif isinstance(value, list):
                for v in value:
                    if isinstance(v, ir.IRVar):
                        add(v)
    return result_list

def generate_assembly(instructions: list[ir.Instruction]) -> str:
    lines = []
    def emit(line: str) -> None: lines.append(line)

    def lambdaN(fun: Callable[[str],None], params: list[str]) -> None:
        for param in params:
            fun(param)

    intrinsics: dict[str, Callable[[list[str]], None]] = {
        '+' : lambda args: lambdaN(emit, [f"movq {args[0]}, %rax", f"addq {args[1]}, %rax"]),
        '-' : lambda args: lambdaN(emit, [f"movq {args[1]}, %rax", f"subq {args[0]}, %rax"]),
        '*' : lambda args: lambdaN(emit, [f"movq {args[0]}, %rax", f"imulq {args[1]}, %rax"]),
        '/' : lambda args: lambdaN(emit, [f"movq {args[0]}, %rax", f"cqto", f"idivq {args[1]}"])
    }
    vars = get_all_ir_variables(instructions, list(intrinsics.keys()) + ['==', 'print_int', 'print_bool', 'read_int'])
    locals = Locals(variables=vars)

    arg_reg = [f'%rdi', f'%rsi', f'%rdx', f'%rcx', f'%r8', f'%r9']

    # ... Emit initial declarations and stack setup here ...
    emit(".extern print_int")
    emit(".extern print_bool")
    emit(".extern red_int")
    emit("")
    emit(".section .text")
    emit("")
    emit(".global main")
    emit(".type main, @function")
    emit("main:")
    for var in vars:
        emit(f'# {var.name} in {locals.get_ref(var)}')
    emit("")
    emit(f'pushq %rbp')
    emit(f'movq %rsp, %rbp')
    emit(f'subq ${locals.stack_used()}, %rsp')
    emit("")
    emit("")
    emit(f'.Lmain_start:')
    for insn in instructions:
        emit("")
        emit('# ' + str(insn))
        match insn:
            case ir.Label():
                emit("")
                # ".L" prefix marks the symbol as "private".
                # This makes GDB backtraces look nicer too:
                # https://stackoverflow.com/a/26065570/965979
                emit(f'.L{insn.name}:')
            case ir.LoadIntConst():
                if -2**31 <= insn.value < 2**31:
                    emit(f'movq ${insn.value}, {locals.get_ref(insn.dest)}')
                else:
                    # Due to a quirk of x86-64, we must use
                    # a different instruction for large integers.
                    # It can only write to a register,
                    # not a memory location, so we use %rax
                    # as a temporary.
                    emit(f'movabsq ${insn.value}, %rax')
                    emit(f'movq %rax, {locals.get_ref(insn.dest)}')
            case ir.Jump():
                emit(f'jmp .L{insn.label.name}')
            case ir.LoadBoolConst():
                emit(f'movq ${int(insn.value)}, {locals.get_ref(insn.dest)}')
            case ir.Copy():
                emit(f'movq {locals.get_ref(insn.source)}, %rax')
                emit(f'movq %rax, {locals.get_ref(insn.dest)}')
            case ir.CondJump():
                emit(f'cmpq $0, {locals.get_ref(insn.cond)}')
                emit(f'jne .L{insn.then_label.name}')
                emit(f'jmp .L{insn.else_label.name}')
            case ir.Call():
                if insn.fun.name in intrinsics:
                    args = []
                    for arg in insn.args:
                        args.append(locals.get_ref(arg))
                    intrinsics[insn.fun.name](args)
                    emit(f'movq %rax, {locals.get_ref(insn.dest)}')
                else:
                    alignment = 0
                    pushes = max(0, len(insn.args) - 6)
                    if (locals.stack_used() + pushes) % 16 != 0:
                        emit(f'subq $8, %rsp')
                        alignment = 1
                    #place first 6 arguments in registers
                    for index, arg in enumerate(insn.args):
                        if index < 6:
                            emit(f'movq {locals.get_ref(arg)}, {arg_reg[index]}')
                        else:
                            break
                    #push additional arguments
                    for i in range(pushes):
                        emit(f'pushq {locals.get_ref(insn.args[-(i+1)])}')

                    emit(f'callq {insn.fun.name}')
                    emit(f'movq %rax, {locals.get_ref(insn.dest)}')
                    if pushes+alignment > 0:
                        emit(f'addq ${(pushes+alignment)*8}, %rsp')
    emit("")
    emit('# Return(None)')
    emit(f'movq $0, %rax')
    emit(f'movq %rbp, %rsp')
    emit(f'popq %rbp')
    emit(f'ret')
    return '\n'.join(lines)