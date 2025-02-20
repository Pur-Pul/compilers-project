from dataclasses import dataclass

@dataclass(frozen=True)
class Type:
    """General type class."""
    def __eq__(self, other: object) -> bool:
        return isinstance(self, type(other)) and isinstance(other, type(self))
    
    def __le__(self, other: object) -> bool:
        return isinstance(self, type(other))
    
    def __lt__(self, other: object) -> bool:
        return self <= other and self != other
    
    def __ge__(self, other: object) -> bool:
        return isinstance(other, type(self))

    def __gr__(self, other: object) -> bool:
        return self >= other and self != other

    def __str__(self) -> str:
        return "Any"

@dataclass(frozen=True)
class TypeInt(Type):
    """Type of a 64 bit signed integer."""
    def __str__(self) -> str:
        return "Int"

@dataclass(frozen=True)
class TypeBool(Type):
    """Type of a boolean value."""
    def __str__(self) -> str:
        return "Bool"

@dataclass(frozen=True)
class TypeUnit(Type):
    """Type of an empty value."""
    def __str__(self) -> str:
        return "Unit"

Any = Type()
Int = TypeInt()
Bool = TypeBool()
Unit = TypeUnit()
Types = {
    'Any':Any,
    'Int':Int,
    'Bool':Bool,
    'Unit':Unit
}

@dataclass(frozen=True)
class FunType(Type):
    """Type of a function"""
    parameters: list[Type]
    value: Type
    
    def __str__(self) -> str:
        string = "("
        for param in self.parameters:
            if len(string) > 1:
                string+=", "
            string += str(param)
        return string + ") => "+ str(self.value)

    def __eq__(self, other: object) -> bool:
        if not (isinstance(self, type(other)) and isinstance(other, type(self))):
            return False
        
        arg_n = len(self.parameters)
        if arg_n != len(other.parameters):
            return False
        
        for i in range(arg_n):
            if self.parameters[i] != other.parameters[i]:
                return False
        
        return self.value == other.value
