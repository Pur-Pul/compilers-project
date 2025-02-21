from typing import Optional, Self

class SymTab[T]:
    parent : Optional[Self] = None
    locals : dict[str, T | None]
    def __init__(self, parent: Optional[Self] = None):
        self.parent = parent
        self.locals = {}

    def declare(self, variable: str) -> None:
        if variable in self.locals:
            raise Exception(f"Local variable '{variable}' is already declared.")
        self.locals[variable] = None

    def assign(self, variable: str, value: T) -> None:
        if variable in self.locals:
            self.locals[variable] = value
        elif self.parent is not None:
            self.parent.assign(variable, value)
        else:
            raise Exception(f"Variable '{variable}' is not declared.")

    def read(self, variable: str) -> T:
        if variable in self.locals:
            value = self.locals[variable]
            if value is None:
                raise Exception(f"Variable '{variable}' has been declared but not defined.") 
            return value
        elif self.parent is not None:
            return self.parent.read(variable)
        else:
            raise Exception(f"Variable '{variable}' is not declared.")
