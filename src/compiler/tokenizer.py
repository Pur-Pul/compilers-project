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

def byLocation(token: Token) -> int:
    return token.source.row*1000 + token.source.column

def tokenize(source_code: str) -> list[Token]:
    print(source_code)
    one_line_comment_pat = re.compile(r'(#|//).*$')
    multi_line_comment_pat = re.compile(r'(/\*).*(.*\n)*?.*?(\*/)')

    identifier_pat= re.compile(r'(?<!\d)([A-Za-z_][A-Za-z0-9_]*)') #(?!#.*)
    int_literal_pat = re.compile(r'(?<![a-zA-Z])\d+(?![a-zA-Z])')
    operator_pat = re.compile(r'[=!<>]=|[+\-*/=<>]')
    punctuation_pat = re.compile(r'[(){},;]')
    linebreak_pat = re.compile(r'\n')
    tokens: list[Token] = []

    for match in multi_line_comment_pat.finditer(source_code): #find mult-line comments and replace them with equal length whitespace while precerving line breaks.
        length = match.end(0) - match.start(0)
        empty_string = " " * length
        for linebreak in linebreak_pat.finditer(match.group(0)):
            empty_string = "\n".join([empty_string[:linebreak.start(0)],empty_string[linebreak.end(0):]])
        print([source_code[:match.start(0)],source_code[match.end(0):]])
        source_code = empty_string.join([source_code[:match.start(0)],source_code[match.end(0):]])

    rows = source_code.split('\n')
    for row_i, row in enumerate(rows):
        for match in one_line_comment_pat.finditer(row): #find one-line comments and replace them with equal length whitespace.
            length = match.end(0) - match.start(0)
            empty_string = " " * length
            row = empty_string.join([row[:match.start(0)],row[match.end(0):]])
    
        for match in identifier_pat.finditer(row):
            col_i = match.start(0)
            tokens.append(Token(match.group(0), "identifier", Source('', row_i, col_i)))
        for match in int_literal_pat.finditer(row):
            col_i = match.start(0)
            tokens.append(Token(match.group(0), "int_literal", Source('', row_i, col_i)))
        for match in operator_pat.finditer(row):
            col_i = match.start(0)
            tokens.append(Token(match.group(0), "operator", Source('', row_i, col_i)))

        
    tokens.sort(key=byLocation)
    for token in tokens:
        print(token, token.type)
    return tokens
