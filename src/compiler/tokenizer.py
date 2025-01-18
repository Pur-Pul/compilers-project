import re
from dataclasses import dataclass

@dataclass
class Source:
    file: str
    row: int
    column: int
    def __init__(self, file: str, row: int, column: int):
        self.file = file
        self.row = row
        self.column = column
    def __str__(self) -> str:
        return f"{self.file}:{self.row}:{self.column}"
L = Source('',0,0)
@dataclass
class Token:
    text: str
    type: str
    source: Source
    def __init__(self, text : str, type: str, source: Source):
        self.text = text
        self.type = type
        self.source = source
    def __str__(self) -> str:
        return f"{self.source}:{self.text}"
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Token):
            return NotImplemented
        return self.text == other.text and self.type == other.type and (self.source == other.source or self.source == L or other.source == L)

def tokenize(source_code: str) -> list[Token]:
    pattern = re.compile(r'([A-Za-z_][A-Za-z0-9_]*|[0-9]+)')
    rows = source_code.split('\n')
    tokens: list[Token] = []
    for row_i, row in enumerate(rows):
        for match in pattern.finditer(row):
            col_i = match.start(0)
            type = "identifier"
            if match.group(0).isnumeric():
                type = "int_literal"
            tokens.append(Token(match.group(0), type, Source('', row_i, col_i)))

    return tokens

#tokenize("if  3\nwhile")