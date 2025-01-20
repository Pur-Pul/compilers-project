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
    assert tokenize('aaa 123 bbb Vector3') == [
        Token(text="aaa", type="identifier", source=L),
        Token(text="123", type="int_literal", source=L),
        Token(text="bbb", type="identifier", source=L),
        Token(text="Vector3", type="identifier", source=L),
    ]
def test_tokenizer_operators() -> None:
    assert tokenize('1 + 2 = 3\n3 - 2 = 1\n4 * 5 = 20\n20 / 5 = 4\n5 > 4\n3 < 7\na <= b\nc >= a\nd==8\ne != a\n') == [
        Token(text="1", type="int_literal", source=L),
        Token(text="+", type="operator", source=L),
        Token(text="2", type="int_literal", source=L),
        Token(text="=", type="operator", source=L),
        Token(text="3", type="int_literal", source=L),

        Token(text="3", type="int_literal", source=L),
        Token(text="-", type="operator", source=L),
        Token(text="2", type="int_literal", source=L),
        Token(text="=", type="operator", source=L),
        Token(text="1", type="int_literal", source=L),

        Token(text="4", type="int_literal", source=L),
        Token(text="*", type="operator", source=L),
        Token(text="5", type="int_literal", source=L),
        Token(text="=", type="operator", source=L),
        Token(text="20", type="int_literal", source=L),

        Token(text="20", type="int_literal", source=L),
        Token(text="/", type="operator", source=L),
        Token(text="5", type="int_literal", source=L),
        Token(text="=", type="operator", source=L),
        Token(text="4", type="int_literal", source=L),

        Token(text="5", type="int_literal", source=L),
        Token(text=">", type="operator", source=L),
        Token(text="4", type="int_literal", source=L),

        Token(text="3", type="int_literal", source=L),
        Token(text="<", type="operator", source=L),
        Token(text="7", type="int_literal", source=L),

        Token(text="a", type="identifier", source=L),
        Token(text="<=", type="operator", source=L),
        Token(text="b", type="identifier", source=L),

        Token(text="c", type="identifier", source=L),
        Token(text=">=", type="operator", source=L),
        Token(text="a", type="identifier", source=L),

        Token(text="d", type="identifier", source=L),
        Token(text="==", type="operator", source=L),
        Token(text="8", type="int_literal", source=L),

        Token(text="e", type="identifier", source=L),
        Token(text="!=", type="operator", source=L),
        Token(text="a", type="identifier", source=L),
    ]

def test_tokenizer_one_line_comments() -> None:
    assert tokenize("#hello") == []
    assert tokenize("hello #bye") == [Token(text="hello", type="identifier", source=L)]
    assert tokenize("hello #bye\nhello again") == [
        Token(text="hello", type="identifier", source=L),
        Token(text="hello", type="identifier", source=L),
        Token(text="again", type="identifier", source=L)
    ]

def test_tokenizer_multi_line_comments() -> None:
    assert tokenize("/*hello") == [Token(text="/", type="operator", source=L),Token(text="*", type="operator", source=L),Token(text="hello",type="identifier",source=L)]
    assert tokenize("hello*/") == [Token(text="hello",type="identifier",source=L),Token(text="*", type="operator", source=L),Token(text="/", type="operator", source=L)]
    assert tokenize("/*hello*/") == []
    assert tokenize("/*hello\nthere*/") == []
    assert tokenize("/*hello\nthere*/bye") == [Token(text="bye", type="identifier", source=L)]
    assert tokenize("/*hello\nthere*/bye*/") == [Token(text="bye", type="identifier", source=L),Token(text="*", type="operator", source=L),Token(text="/", type="operator", source=L)]
    assert tokenize("hi/*hello\nthere*/") == [Token(text="hi", type="identifier", source=L)]
    assert tokenize("hi/*hello\nthere*/bye") == [Token(text="hi", type="identifier", source=L),Token(text="bye", type="identifier", source=L)]