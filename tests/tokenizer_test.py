from compiler.tokenizer import tokenize, Token, L

def test_tokenizer_basics() -> None:
    assert tokenize("if  3\nwhile") == [
        Token(text='if', type="identifier", source=L), 
        Token(text='3', type="int_literal", source=L),
        Token(text='while', type="identifier", source=L),
    ]
    assert tokenize("if Token getToken\nelse\nfor token in token_finder\nprint token") == [
        Token(text='if', type="identifier", source=L),
        Token(text='Token', type="identifier", source=L),
        Token(text='getToken', type="identifier", source=L),
        Token(text='else', type="identifier", source=L),
        Token(text='for', type="identifier", source=L),
        Token(text='token', type="identifier", source=L),
        Token(text='in', type="identifier", source=L),
        Token(text='token_finder', type="identifier", source=L),
        Token(text='print', type="identifier", source=L),
        Token(text='token', type="identifier", source=L),
        ]
    assert tokenize('aaa 123 bbb') == [
        Token(text="aaa", type="identifier", source=L),
        Token(text="123", type="int_literal", source=L),
        Token(text="bbb", type="identifier", source=L),
    ]
