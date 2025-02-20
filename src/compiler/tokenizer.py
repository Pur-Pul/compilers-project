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

def tokenize(source_code: str, file_name: str = "") -> list[Token]:
    one_line_comment_pat = re.compile(r'^(#|//).*')
    multi_line_comment_pat = re.compile(r'^(/\*).*(.*\n)*?.*?(\*/)')
    whitespace_pat = re.compile(r'^\s+')
    identifier_pat= re.compile(r'^(?<!\d)([A-Za-z_][A-Za-z0-9_]*)')
    int_literal_pat = re.compile(r'^(?<![a-zA-Z])\d+(?![a-zA-Z])')
    operator_pat = re.compile(r'^[=!<>]=|^[+\-*/=<>]')
    punctuation_pat = re.compile(r'^[(){},;]')
    linebreak_pat = re.compile('^\n')
    tokens: list[Token] = []

    start = 0
    row = 0
    col = 0
    while(start < len(source_code)):
        whitespace = whitespace_pat.search(source_code[start:])
        one_line_comment = one_line_comment_pat.search(source_code[start:])
        multi_line_comment = multi_line_comment_pat.search(source_code[start:])
        identifier = identifier_pat.search(source_code[start:])
        int_literal = int_literal_pat.search(source_code[start:])
        operator = operator_pat.search(source_code[start:])
        punctuation = punctuation_pat.search(source_code[start:])
        linebreak = linebreak_pat.search(source_code[start:])
        #print(source_code[start:])
        if linebreak:
            #print(start, linebreak)
            row += 1
            col = 0
            start += linebreak.end(0)
        elif whitespace:
            #print(start, whitespace)
            start += whitespace.end(0)
            col += whitespace.end(0)
        elif multi_line_comment:
            #print(start, multi_line_comment)
            linebreak_n = len(re.compile(r'\n').findall(multi_line_comment.group(0)))
            if linebreak_n:
                for i, match in enumerate(re.compile(r'\n').finditer(multi_line_comment.group(0))):
                    row += 1
                    if i == linebreak_n-1:
                        col = multi_line_comment.start(0) + match.end(0)
            else:
                col += multi_line_comment.end(0)
            start += multi_line_comment.end(0)
        elif one_line_comment:
            #print(start, one_line_comment)
            #row += 1
            col += one_line_comment.end(0)
            start += one_line_comment.end(0)
        elif identifier:
            #print(start, identifier)
            tokens.append(Token(text=identifier.group(0),type="identifier",source=Source(file_name,row,col)))
            start += identifier.end(0)
            col += identifier.end(0)
        elif int_literal:
            #print(start, int_literal)
            tokens.append(Token(text=int_literal.group(0),type="int_literal",source=Source(file_name,row,col)))
            start += int_literal.end(0)
            col += int_literal.end(0)
        elif operator:
            #print(start, operator)
            tokens.append(Token(text=operator.group(0),type="operator",source=Source(file_name,row,col)))
            start += operator.end(0)
            col += operator.end(0)
        elif punctuation:
            #print(start, punctuation)
            tokens.append(Token(text=punctuation.group(0),type="punctuation",source=Source(file_name,row,col)))
            start += punctuation.end(0)
            col += punctuation.end(0)
        else:
            start+=1

    return tokens
