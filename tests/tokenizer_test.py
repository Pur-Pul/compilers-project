from compiler.tokenizer import tokenize

def test_tokenizer_basics() -> None:
    assert tokenize("if  3\nwhile") == ['if', '3', 'while']
    assert tokenize("else\nfor token in token_finder\nprint token") == ['else', 'for', 'token', 'in', 'token_finder', 'print', 'token']
