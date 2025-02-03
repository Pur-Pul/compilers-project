import pytest
from compiler.parser import parse
from compiler.tokenizer import Token, Source, L
import compiler.ast as ast

def test_parse_one_identifier() -> None:
    tokens = [Token("first", "identifier", L)]
    assert(parse(tokens)) == ast.Identifier("first")

def test_parse_multiple_identifiers_fails() -> None:
    tokens = [Token("first", "identifier", Source("filename",5,5)),Token("second", "identifier", Source("filename",5,11))]
    with pytest.raises(Exception) as e:
        parse(tokens)
    assert(e.value.args[0]) == 'filename:5:11: garbage at end of expression.'

def test_parse_one_int_literal() -> None:
    tokens = [Token("1", "int_literal", L)]
    assert(parse(tokens)) == ast.Literal(1)

def test_parse_multiple_literals_fails() -> None:
    tokens = [Token("1", "int_literal", Source("filename",5,5)),Token("2", "int_literal", Source("filename",5,7))]
    with pytest.raises(Exception) as e:
        parse(tokens)
    assert(e.value.args[0]) == 'filename:5:7: garbage at end of expression.'

def test_parse_plus_minus() -> None:
    operators = ["+", "-"]
    for operator in operators:
        tokens = [
            Token("1", "int_literal", L),
            Token(operator, "operation", L),
            Token("2", "int_literal", L)
        ]
        assert(parse(tokens)) == ast.BinaryOp(
            ast.Literal(1),
            operator,
            ast.Literal(2)
        )

def test_parse_multiplication_division_modulo() -> None:
    operators = ["*", "/", "%"]
    for operator in operators:
        tokens = [
            Token("1", "int_literal", L),
            Token(operator, "operation", L),
            Token("2", "int_literal", L)]
        assert(parse(tokens)) == ast.BinaryOp(
            ast.Literal(1),
            operator,
            ast.Literal(2)
        )

def test_plus_minus_nested() -> None:
    operators = ["+", "-"]
    for operator1 in operators:
        for operator2 in operators:
            tokens = [
                Token("1", "int_literal", L),
                Token(operator1, "operation", L),
                Token("2", "int_literal", L),
                Token(operator2, "operation", L),
                Token("3", "int_literal", L)
            ]
            assert(parse(tokens)) == ast.BinaryOp(
                ast.BinaryOp(
                    ast.Literal(1),
                    operator1,
                    ast.Literal(2)
                ),
                operator2,
                ast.Literal(3)
            )

def test_multiplication_division_modulo_plus_minus_nested() -> None:
    operators1 = ["*", "/", "%"]
    operators2 = ["+", "-"]
    for operator1 in operators1:
        for operator2 in operators2:
            tokens = [
                Token("1", "int_literal", L),
                Token(operator1, "operation", L),
                Token("2", "int_literal", L),
                Token(operator2, "operation", L),
                Token("3", "int_literal", L)
            ]
            assert(parse(tokens)) == ast.BinaryOp(
                ast.BinaryOp(
                    ast.Literal(1),
                    operator1,
                    ast.Literal(2)
                ),
                operator2,
                ast.Literal(3)
                
            )

def test_plus_minus_multiplication_division_modulo_nested() -> None:
    operators1 = ["+", "-"]
    operators2 = ["*", "/", "%"]
    for operator1 in operators1:
        for operator2 in operators2:
            tokens = [
                Token("1", "int_literal", L),
                Token(operator1, "operation", L),
                Token("2", "int_literal", L),
                Token(operator2, "operation", L),
                Token("3", "int_literal", L)
            ]
            assert(parse(tokens)) == ast.BinaryOp(
                ast.Literal(1),
                operator1,
                ast.BinaryOp(
                    ast.Literal(2),
                    operator2,
                    ast.Literal(3)
                )
                
            )

def test_empty_tokens_fails_gracefully() -> None:
    with pytest.raises(Exception) as e:
        parse([])
    assert(e.value.args[0]) == ':0:0: expected "(", an integer literal or an identifier'

def test_if_identifier_then_identifier() -> None:
    tokens = [Token("if", "identifier", L), Token("something", "identifier", L), Token("then", "identifier", L), Token("somethingElse", "identifier", L)]
    assert(parse(tokens)) == ast.IfClause(ast.Identifier("something"),ast.Identifier("somethingElse"))

def test_if_identifier_then_identifier_else_identifier() -> None:
    tokens = [Token("if", "identifier", L), Token("something", "identifier", L), Token("then", "identifier", L), Token("somethingElse", "identifier", L), Token("else", "identifier", L), Token("somethingThird", "identifier", L)]
    assert(parse(tokens)) == ast.IfClause(ast.Identifier("something"),ast.Identifier("somethingElse"),ast.Identifier("somethingThird"))

def test_if_else_nested() -> None:
    tokens = [
        Token("if", "identifier", L),
        Token("something", "identifier", L),
        Token("then", "identifier", L),
            Token("if", "identifier", L),
            Token("somethingElse", "identifier", L),
            Token("then", "identifier", L),
            Token("do", "identifier", L),
            Token("else", "identifier", L),
            Token("doNot", "identifier", L),
        Token("else", "identifier", L),
        Token("dosomething", "identifier", L)
    ]
    assert(parse(tokens)) == ast.IfClause(
        ast.Identifier("something"),
        ast.IfClause(
            ast.Identifier("somethingElse"),
            ast.Identifier("do"),
            ast.Identifier("doNot"),
        ),
        ast.Identifier("dosomething")
    )

def test_if_else_nested_with_operations() -> None:
    tokens = [
        Token("if", "identifier", L),
        Token("5", "int_literal", L),
        Token("-", "operator", L),
        Token("4", "int_literal", L),

        Token("then", "identifier", L),
            Token("if", "identifier", L),
            Token("a", "identifier", L),
            Token("+", "operator", L),
            Token("b", "identifier", L),

            Token("then", "identifier", L),
            Token("1", "int_literal", L),
            Token("+", "operator", L),
            Token("2", "int_literal", L),

            Token("else", "identifier", L),
            Token("5", "int_literal", L),
            Token("*", "operator", L),
            Token("3", "int_literal", L),

        Token("else", "identifier", L),
            Token("if", "identifier", L),
            Token("d", "identifier", L),
            Token("*", "operator", L),
            Token("c", "identifier", L),

            Token("then", "identifier", L),
            Token("6", "int_literal", L),
            Token("-", "operator", L),
            Token("10", "int_literal", L),

            Token("else", "identifier", L),
            Token("8", "int_literal", L),
            Token("/", "operator", L),
            Token("4", "int_literal", L),
    ]
    assert(parse(tokens)) == ast.IfClause(
        ast.BinaryOp(
            ast.Literal(5),
            '-',
            ast.Literal(4)
        ),
        ast.IfClause(
            ast.BinaryOp(
                ast.Identifier('a'),
                '+',
                ast.Identifier('b')
            ),
            ast.BinaryOp(
                ast.Literal(1),
                '+',
                ast.Literal(2)
            ),
            ast.BinaryOp(
                ast.Literal(5),
                '*',
                ast.Literal(3)
            ),
        ),
        ast.IfClause(
            ast.BinaryOp(
                ast.Identifier('d'),
                '*',
                ast.Identifier('c')
            ),
            ast.BinaryOp(
                ast.Literal(6),
                '-',
                ast.Literal(10)
            ),
            ast.BinaryOp(
                ast.Literal(8),
                '/',
                ast.Literal(4)
            ),
        ),
    )

def test_if_else_in_operation() -> None:
    tokens = [
        Token("1", "int_literal", L),
        Token("+", "operator", L),
        Token("if", "identifier", L),
        Token("5", "int_literal", L),
        Token("-", "operator", L),
        Token("4", "int_literal", L),
        Token("then", "identifier", L),
            Token("1", "int_literal", L),
        Token("else", "identfier", L),
            Token("2", "int_literal", L)
    ]
    assert(parse(tokens)) == ast.BinaryOp(
        ast.Literal(1),
        '+',
        ast.IfClause(
            ast.BinaryOp(
                ast.Literal(5),
                '-',
                ast.Literal(4),
            ),
            ast.Literal(1),
            ast.Literal(2)
        )
        
    )

def test_if_with_missing_else_fails_gracefully() -> None:
    tokens = [
        Token("if", "identifier", L),
        Token("something", "identifier", L),
        Token("then", "identifier", L),
        Token("1", "int_literal", L),
        Token("else", "identifier", L),
    ]
    with pytest.raises(Exception) as e:
        parse(tokens)
    assert(e.value.args[0]) == ':0:0: expected "(", an integer literal or an identifier'

    tokens = [
        Token("if", "identifier", L),
        Token("something", "identifier", L),
        Token("then", "identifier", L),
        Token("1", "int_literal", L),
        Token("2", "int_literal", L),
    ]
    with pytest.raises(Exception) as e:
        parse(tokens)
    assert(e.value.args[0]) == ':0:0: garbage at end of expression.'

def test_function_with_identifier() -> None:
    tokens = [
        Token("f", "identifier", L),
        Token("(", "punctuation", L),
        Token("a", "identifier", L),
        Token(")", "punctuation", L)
    ]
    assert(parse(tokens)) == ast.FunctionCall(
        ast.Identifier('f'),
        [ast.Identifier('a')]
    )

def test_function_with_two_identifiers() -> None:
    tokens = [
        Token("f", "identifier", L),
        Token("(", "punctuation", L),
        Token("a", "identifier", L),
        Token(",", "punctuation", L),
        Token("b", "identifier", L),
        Token(")", "punctuation", L)
    ]
    assert(parse(tokens)) == ast.FunctionCall(
        ast.Identifier('f'),
        [
            ast.Identifier('a'),
            ast.Identifier('b')
        ]
    )

def test_function_with_ten_identifiers() -> None:
    tokens = [
        Token("f", "identifier", L),
        Token("(", "punctuation", L),
        Token("a", "identifier", L),
        Token(",", "punctuation", L),
        Token("b", "identifier", L),
        Token(",", "punctuation", L),
        Token("c", "identifier", L),
        Token(",", "punctuation", L),
        Token("d", "identifier", L),
        Token(",", "punctuation", L),
        Token("e", "identifier", L),
        Token(",", "punctuation", L),
        Token("f", "identifier", L),
        Token(",", "punctuation", L),
        Token("g", "identifier", L),
        Token(",", "punctuation", L),
        Token("h", "identifier", L),
        Token(",", "punctuation", L),
        Token("i", "identifier", L),
        Token(",", "punctuation", L),
        Token("j", "identifier", L),
        Token(")", "punctuation", L)
    ]
    assert(parse(tokens)) == ast.FunctionCall(
        ast.Identifier('f'),
        [
            ast.Identifier('a'),
            ast.Identifier('b'),
            ast.Identifier('c'),
            ast.Identifier('d'),
            ast.Identifier('e'),
            ast.Identifier('f'),
            ast.Identifier('g'),
            ast.Identifier('h'),
            ast.Identifier('i'),
            ast.Identifier('j'),
        ]
    )

def test_function_with_identifier_and_operation() -> None:
    tokens = [
        Token("f", "identifier", L),
        Token("(", "punctuation", L),
        Token("a", "identifier", L),
        Token(",", "punctuation", L),
        Token("1", "int_literal", L),
        Token("+", "operator", L),
        Token("2", "int_literal", L),
        Token(")", "punctuation", L)
    ]
    assert(parse(tokens)) == ast.FunctionCall(
        ast.Identifier('f'),
        [
            ast.Identifier('a'),
            ast.BinaryOp(
                ast.Literal(1),
                "+",
                ast.Literal(2)
            )
        ]
    )

def test_function_with_nested_functions() -> None:
    tokens = [
        Token("f", "identifier", L),
        Token("(", "punctuation", L),

        Token("g", "identifier", L),
        Token("(", "punctuation", L),
        Token("1", "int_literal", L),
        Token(",", "punctuation", L),
        Token("2", "int_literal", L),
        Token(")", "punctuation", L),

        Token(",", "punctuation", L),

        Token("h", "identifier", L),
        Token("(", "punctuation", L),
        Token("a", "identifier", L),
        Token(",", "punctuation", L),
        Token("b", "identifier", L),
        Token(")", "punctuation", L),

        Token(")", "punctuation", L)
    ]
    assert(parse(tokens)) == ast.FunctionCall(
        ast.Identifier('f'),
        [
            ast.FunctionCall(
                ast.Identifier('g'),
                [
                    ast.Literal(1),
                    ast.Literal(2)
                ]
            ),
            ast.FunctionCall(
                ast.Identifier('h'),
                [
                    ast.Identifier('a'),
                    ast.Identifier('b')
                ]
            )
        ]
    )

def test_assignment() -> None:
    tokens = [
        Token("a", "identifier", L),
        Token("=", "operator", L),
        Token("b", "identifier", L)
    ]

    assert(parse(tokens)) == ast.Assignment(
        ast.Identifier("a"),
        "=",
        ast.Identifier("b")
    )

def test_nested_assignments() -> None:
    tokens = [
        Token("a", "identifier", L),
        Token("=", "operator", L),
        Token("b", "identifier", L),
        Token("=", "operator", L),
        Token("c", "identifier", L)
    ]

    assert(parse(tokens)) == ast.Assignment(
        ast.Identifier("a"),
        "=",
        ast.Assignment(
            ast.Identifier("b"),
            "=",
            ast.Identifier("c")
        )
    )

def test_nested_assignments_with_operations() -> None:
    tokens = [
        Token("a", "identifier", L),
        Token("=", "operator", L),
        Token("b", "identifier", L),
        Token("+", "operator", L),
        Token("c", "identifier", L),
        Token("=", "operator", L),
        Token("d", "identifier", L)
    ]

    assert(parse(tokens)) == ast.Assignment(
        ast.Identifier("a"),
        "=",
        ast.Assignment(
            ast.BinaryOp(
                ast.Identifier("b"),
                "+",
                ast.Identifier("c")
            ),
            "=",
            ast.Identifier("d")
        )
    )

def test_or() -> None:
    tokens = [
        Token("a", "identifier", L),
        Token("or", "identifier", L),
        Token("b", "identifier", L),
    ]

    assert(parse(tokens)) == ast.BinaryOp(
        ast.Identifier("a"),
        "or",
        ast.Identifier("b")
    )

def test_ors_nested() -> None:
    tokens = [
        Token("a", "identifier", L),
        Token("or", "identifier", L),
        Token("b", "identifier", L),
        Token("or", "identifier", L),
        Token("c", "identifier", L)
    ]

    assert(parse(tokens)) == ast.BinaryOp(
        ast.BinaryOp(
            ast.Identifier("a"),
            "or",
            ast.Identifier("b")
        ),
        "or",
        ast.Identifier("c")
    )

def test_and() ->None:
    tokens = [
        Token("a", "identifier", L),
        Token("and", "identifier", L),
        Token("b", "identifier", L)
    ]

    assert(parse(tokens)) == ast.BinaryOp(
        ast.Identifier("a"),
        "and",
        ast.Identifier("b")
    )

def test_ands_nested() -> None:
    tokens = [
        Token("a", "identifier", L),
        Token("and", "identifier", L),
        Token("b", "identifier", L),
        Token("and", "identifier", L),
        Token("c", "identifier", L)
    ]

    assert(parse(tokens)) == ast.BinaryOp(
        ast.BinaryOp(
            ast.Identifier("a"),
            "and",
            ast.Identifier("b")
        ),
        "and",
        ast.Identifier("c")
    )

def test_and_or_nested() -> None:
    tokens = [
        Token("a", "identifier", L),
        Token("and", "identifier", L),
        Token("b", "identifier", L),
        Token("or", "identifier", L),
        Token("c", "identifier", L)
    ]

    assert(parse(tokens)) == ast.BinaryOp(
        ast.BinaryOp(
            ast.Identifier("a"),
            "and",
            ast.Identifier("b")
        ),
        "or",
        ast.Identifier("c")
    )

def test_or_and_nested() -> None:
    tokens = [
        Token("a", "identifier", L),
        Token("or", "identifier", L),
        Token("b", "identifier", L),
        Token("and", "identifier", L),
        Token("c", "identifier", L)
    ]

    assert(parse(tokens)) == ast.BinaryOp(
        ast.Identifier("a"),
        "or",
        ast.BinaryOp(
            ast.Identifier("b"),
            "and",
            ast.Identifier("c")
        )
    )

def test_equal_and_not_equal() ->None:
    tokens = [
        Token("a", "identifier", L),
        Token("==", "operator", L),
        Token("b", "identifier", L)
    ]

    assert(parse(tokens)) == ast.BinaryOp(
        ast.Identifier("a"),
        "==",
        ast.Identifier("b")
    )

    tokens = [
        Token("a", "identifier", L),
        Token("!=", "operator", L),
        Token("b", "identifier", L)
    ]

    assert(parse(tokens)) == ast.BinaryOp(
        ast.Identifier("a"),
        "!=",
        ast.Identifier("b")
    )

def test_equal_and_not_equal_nested() -> None:
    tokens = [
        Token("a", "identifier", L),
        Token("==", "operator", L),
        Token("b", "identifier", L),
        Token("==", "operator", L),
        Token("c", "identifier", L)
    ]

    assert(parse(tokens)) == ast.BinaryOp(
        ast.BinaryOp(
            ast.Identifier("a"),
            "==",
            ast.Identifier("b")
        ),
        "==",
        ast.Identifier("c")
    )

    tokens = [
        Token("a", "identifier", L),
        Token("==", "operator", L),
        Token("b", "identifier", L),
        Token("!=", "operator", L),
        Token("c", "identifier", L)
    ]

    assert(parse(tokens)) == ast.BinaryOp(
        ast.BinaryOp(
            ast.Identifier("a"),
            "==",
            ast.Identifier("b")
        ),
        "!=",
        ast.Identifier("c")
    )

    tokens = [
        Token("a", "identifier", L),
        Token("!=", "operator", L),
        Token("b", "identifier", L),
        Token("==", "operator", L),
        Token("c", "identifier", L)
    ]

    assert(parse(tokens)) == ast.BinaryOp(
        ast.BinaryOp(
            ast.Identifier("a"),
            "!=",
            ast.Identifier("b")
        ),
        "==",
        ast.Identifier("c")
    )

def test_equal_notequal_and_nested() -> None:
    tokens = [
        Token("a", "identifier", L),
        Token("==", "operator", L),
        Token("b", "identifier", L),
        Token("and", "identifier", L),
        Token("c", "identifier", L)
    ]

    assert(parse(tokens)) == ast.BinaryOp(
        ast.BinaryOp(
            ast.Identifier("a"),
            "==",
            ast.Identifier("b")
        ),
        "and",
        ast.Identifier("c")
    )

    tokens = [
        Token("a", "identifier", L),
        Token("!=", "operator", L),
        Token("b", "identifier", L),
        Token("and", "identifier", L),
        Token("c", "identifier", L)
    ]

    assert(parse(tokens)) == ast.BinaryOp(
        ast.BinaryOp(
            ast.Identifier("a"),
            "!=",
            ast.Identifier("b")
        ),
        "and",
        ast.Identifier("c")
    )

def test_and_equal_not_equal_nested() -> None:
    tokens = [
        Token("a", "identifier", L),
        Token("and", "identifier", L),
        Token("b", "identifier", L),
        Token("==", "operator", L),
        Token("c", "identifier", L)
    ]

    assert(parse(tokens)) == ast.BinaryOp(
        ast.Identifier("a"),
        "and",
        ast.BinaryOp(
            ast.Identifier("b"),
            "==",
            ast.Identifier("c")
        )
    )

    tokens = [
        Token("a", "identifier", L),
        Token("and", "identifier", L),
        Token("b", "identifier", L),
        Token("!=", "operator", L),
        Token("c", "identifier", L)
    ]

    assert(parse(tokens)) == ast.BinaryOp(
        ast.Identifier("a"),
        "and",
        ast.BinaryOp(
            ast.Identifier("b"),
            "!=",
            ast.Identifier("c")
        )
    )

def test_inequalities() -> None:
    inequalities = ["<", "<=", ">", ">="]
    for inequality in inequalities:
        tokens = [
            Token("a", "identifier", L),
            Token(inequality, "operator", L),
            Token("b", "identifier", L)
        ]

        assert(parse(tokens)) == ast.BinaryOp(
            ast.Identifier("a"),
            inequality,
            ast.Identifier("b")
        )

def test_inequalities_nested() -> None:
    inequalities = ["<", "<=", ">", ">="]
    for inequality1 in inequalities:
        for inequality2 in inequalities:
            tokens = [
                Token("a", "identifier", L),
                Token(inequality1, "operator", L),
                Token("b", "identifier", L),
                Token(inequality2, "operator", L),
                Token("c", "identifier", L)
            ]

            assert(parse(tokens)) == ast.BinaryOp(
                ast.BinaryOp(
                    ast.Identifier("a"),
                    inequality1,
                    ast.Identifier("b")
                ),
                inequality2,
                ast.Identifier("c")
            )

def test_inequalities_equal_not_equal_nested() -> None:
    inequalities = ["<", "<=", ">", ">="]
    equalities = ["==", "!="]
    for inequality in inequalities:
        for equality in equalities:
            tokens = [
                Token("a", "identifier", L),
                Token(inequality, "operator", L),
                Token("b", "identifier", L),
                Token(equality, "operator", L),
                Token("c", "identifier", L)
            ]

            assert(parse(tokens)) == ast.BinaryOp(
                ast.BinaryOp(
                    ast.Identifier("a"),
                    inequality,
                    ast.Identifier("b")
                ),
                equality,
                ast.Identifier("c")
            )

def test_equal_not_equal_inequalities_nested() -> None:
    inequalities = ["<", "<=", ">", ">="]
    equalities = ["==", "!="]
    for equality in equalities:
        for inequality in inequalities:
            tokens = [
                Token("a", "identifier", L),
                Token(equality, "operator", L),
                Token("b", "identifier", L),
                Token(inequality, "operator", L),
                Token("c", "identifier", L)
            ]

            assert(parse(tokens)) == ast.BinaryOp(
                ast.Identifier("a"),
                equality,
                ast.BinaryOp(
                    ast.Identifier("b"),
                    inequality,
                    ast.Identifier("c")
                )
            )

def test_plus_minus_inequalities_nested() -> None:
    inequalities = ["<", "<=", ">", ">="]
    plus_minus = ["+", "-"]
    for operator in plus_minus:
        for inequality in inequalities:
            tokens = [
                Token("a", "identifier", L),
                Token(operator, "operator", L),
                Token("b", "identifier", L),
                Token(inequality, "operator", L),
                Token("c", "identifier", L)
            ]

            assert(parse(tokens)) == ast.BinaryOp(
                ast.BinaryOp(
                    ast.Identifier("a"),
                    operator,
                    ast.Identifier("b")
                ),
                inequality,
                ast.Identifier("c")
            )

def test_inequalities_plus_minus_nested() -> None:
    inequalities = ["<", "<=", ">", ">="]
    plus_minus = ["+", "-"]
    for inequality in inequalities:
        for operator in plus_minus:
            tokens = [
                Token("a", "identifier", L),
                Token(inequality, "operator", L),
                Token("b", "identifier", L),
                Token(operator, "operator", L),
                Token("c", "identifier", L)
            ]

            assert(parse(tokens)) == ast.BinaryOp(
                ast.Identifier("a"),
                inequality,
                ast.BinaryOp(
                    ast.Identifier("b"),
                    operator,
                    ast.Identifier("c")
                )
            )

def test_parse_unary() -> None:
    operators = [Token('-', 'operator', L), Token('not', 'identifer', L)]
    for operator in operators:
        tokens = [
            operator,
            Token('a', 'identifier', L)
        ]

        assert(parse(tokens)) == ast.UnaryOp(
            operator.text,
            ast.Identifier('a')
        )

def test_parse_unary_nested() -> None:
    operators = [Token('-', 'operator', L), Token('not', 'identifer', L)]
    for operator1 in operators:
        for operator2 in operators:
            tokens = [
                operator1,
                operator2,
                Token('a', 'identifier', L)
            ]

            assert(parse(tokens)) == ast.UnaryOp(
                operator1.text,
                ast.UnaryOp(
                    operator2.text,
                    ast.Identifier('a')
                )
            )
        
def test_multiplication_division_modulo_unary_nested() -> None:
    operators1 = [Token('*', 'operator', L), Token('/', 'operator', L), Token('%', 'operator', L)]
    operators2 = [Token('-', 'operator', L), Token('not', 'identifer', L)]
    for operator1 in operators1:
        for operator2 in operators2:
            tokens = [
                Token('a', 'identifier', L),
                operator1,
                operator2,
                Token('b', 'identifier', L)
            ]

            assert(parse(tokens)) == ast.BinaryOp(
                ast.Identifier('a'),
                operator1.text,
                ast.UnaryOp(
                    operator2.text,
                    ast.Identifier('b')
                )
            )

def test_unary_multiplication_division_modulo_nested() -> None:
    operators1 = [Token('-', 'operator', L), Token('not', 'identifer', L)]
    operators2 = [Token('*', 'operator', L), Token('/', 'operator', L), Token('%', 'operator', L)]
    for operator1 in operators1:
        for operator2 in operators2:
            tokens = [
                operator1,
                Token('a', 'identifier', L),
                operator2,
                Token('b', 'identifier', L)
            ]

            assert(parse(tokens)) == ast.BinaryOp(
                ast.UnaryOp(
                    operator1.text,
                    ast.Identifier('a')
                ),
                operator2.text,
                ast.Identifier('b'),
            )

def test_unary_expressions_nested() -> None:
    operators = [Token('-', 'operator', L), Token('not', 'identifer', L)]
    expressions = [
        [Token('if', 'identifier', L), Token('a', 'identifier', L), Token('then', 'identifier', L), Token('b', 'identifier', L), Token('else', 'identifier', L), Token('c', 'identifier', L)]
    ]

    for operator in operators:
        for expression in expressions:
            tokens = [operator] + expression
            assert(parse(tokens)) == ast.UnaryOp(
                operator.text,
                ast.IfClause(
                    ast.Identifier(expression[1].text),
                    ast.Identifier(expression[3].text),
                    ast.Identifier(expression[5].text)
                )
            )

def test_expressions_unary_nested() -> None:
    operators = [Token('-', 'operator', L), Token('not', 'identifer', L)]
    expressions = [
        [Token('if', 'identifier', L), Token('a', 'identifier', L), Token('then', 'identifier', L), Token('b', 'identifier', L), Token('else', 'identifier', L), Token('c', 'identifier', L)]
    ]
    for expression in expressions:
        for operator in operators:
            tokens = expression[0:1] + [operator] + expression[1:3] + [operator] + expression[3:5] + [operator] + expression[5:6]
            assert(parse(tokens)) == ast.IfClause(
                    ast.UnaryOp(
                        operator.text,
                        ast.Identifier(expression[1].text),
                    ),
                    ast.UnaryOp(
                        operator.text,
                        ast.Identifier(expression[3].text),
                    ),
                    ast.UnaryOp(
                        operator.text,
                        ast.Identifier(expression[5].text),
                    )
             )

def test_parse_block_with_one_identfier() -> None:
    tokens = [
        Token("{", "punctuation", L),
        Token("a", "identifier", L),
        Token("}", "punctuation", L),
    ]
    assert(parse(tokens)) == ast.Block(
        [],
        ast.Identifier("a")
    )

    tokens = [
        Token("{", "punctuation", L),
        Token("a", "identifier", L),
        Token(";", "punctuation", L),
        Token("}", "punctuation", L),
    ]
    assert(parse(tokens)) == ast.Block(
        [ast.Identifier("a")],
        ast.Literal(None)
    )

def test_parse_block_nested() -> None:
    tokens = [
        Token("{", "punctuation", L),
            Token("a", "identifier", L),
            Token(";", "punctuation", L),
            Token("{", "punctuation", L),
                Token("b", "identifier", L),
                Token(";", "punctuation", L),
            Token("}", "punctuation", L),
            Token(";", "punctuation", L),
            Token("c", "identifier", L),
        Token("}", "punctuation", L)
    ]

    assert(parse(tokens)) == ast.Block(
        [
            ast.Identifier("a"),
            ast.Block(
                [ast.Identifier("b")],
                ast.Literal(None)
            )
        ],
        ast.Identifier("c")
    )

def test_parse_block_expression_nested() -> None:
    expressions = [
        [Token('a', 'identifier', L),Token('+', 'int_literal', L),Token('b', 'identifier', L)],
        [Token('if', 'identifier', L), Token('a', 'identifier', L), Token('then', 'identifier', L), Token('b', 'identifier', L), Token('else', 'identifier', L), Token('c', 'identifier', L)]
    ]
    tokens = [Token("{", "punctuation", L)] + expressions[0] + [Token(";", "punctuation", L)] + expressions[1] + [Token(";", "punctuation", L)] + [Token("}", "punctuation", L)]
    assert(parse(tokens)) == ast.Block(
        [
            ast.BinaryOp(
                ast.Identifier('a'),
                '+',
                ast.Identifier('b')
            ),
            ast.IfClause(
                ast.Identifier('a'),
                ast.Identifier('b'),
                ast.Identifier('c')
            )
        ],
        ast.Literal(None)
    )

def test_expression_parse_block_expression_nested() -> None:
    expressions = [
        [Token('a', 'identifier', L),Token('+', 'int_literal', L),Token('b', 'identifier', L)],
        [Token('if', 'identifier', L), Token('a', 'identifier', L), Token('then', 'identifier', L), Token('b', 'identifier', L), Token('else', 'identifier', L), Token('c', 'identifier', L)]
    ]
    tokens = [Token('z', 'identifier', L), Token('=', 'operator', L)] + [Token("{", "punctuation", L)] + expressions[0] + [Token(";", "punctuation", L)] + expressions[1] + [Token(";", "punctuation", L)] + [Token("}", "punctuation", L)]
    assert(parse(tokens)) == ast.Assignment(
        ast.Identifier('z'),
        '=',
        ast.Block(
            [
                ast.BinaryOp(
                    ast.Identifier('a'),
                    '+',
                    ast.Identifier('b')
                ),
                ast.IfClause(
                    ast.Identifier('a'),
                    ast.Identifier('b'),
                    ast.Identifier('c')
                )
            ],
            ast.Literal(None)
        )
    )

def test_block_missing_semicolon_fails_gracefully() -> None:
    tokens = [
        Token("{", "punctuation", L),
        Token("a", "identifier", L),
        Token("b", "identifier", L),
        Token("}", "punctuation", L)
    ]

    with pytest.raises(Exception) as e:
        parse(tokens)
    assert(e.value.args[0]) == ':0:0: expected "}"'

def test_block_missing_end_bracket_fails_gracefully() -> None:
    tokens = [
        Token("{", "punctuation", L),
        Token("a", "identifier", L),
        Token(";", "punctuation", L),
        Token("b", "identifier", L),
        Token(";", "punctuation", L),
        Token("c", "identifier", L),
    ]

    with pytest.raises(Exception) as e:
        parse(tokens)
    assert(e.value.args[0]) == ':0:0: expected "}"'

def test_var_declaration_possible_in_top() -> None:
    tokens = [
        Token("var", "identifier", L),
        Token("a", "identifier", L),
        Token("=", "operator", L),
        Token("b", "identifier", L)
    ]

    assert(parse(tokens)) == ast.UnaryOp(
        "var",
        ast.Assignment(
            ast.Identifier("a"),
            "=",
            ast.Identifier("b")
        )
    )

def test_var_declaration_possible_in_block() -> None:
    tokens = [
        Token("{", "punctuation", L),
        Token("1", "int_literal", L),
        Token("+", "operator", L),
        Token("2", "int_literal", L),
        Token(";", "punctuation", L),
        Token("var", "identifier", L),
        Token("a", "identifier", L),
        Token("=", "operator", L),
        Token("b", "identifier", L),
        Token("}", "punctuation", L)
    ]

    assert(parse(tokens)) == ast.Block(
        [ast.BinaryOp(
            ast.Literal(1),
            '+',
            ast.Literal(2)
        )],
        ast.UnaryOp(
            "var",
            ast.Assignment(
                ast.Identifier("a"),
                "=",
                ast.Identifier("b")
            )
        )
    )

def test_var_declaration_not_possible_outside_block_or_top() -> None:
    tokens = [
        Token("if", "identifier", L),
        Token("true", "identifier", L),
        Token("then", "identifer", L),
        Token("var", "identifier", L),
        Token("a", "identifier", L),
        Token("=", "operator", L),
        Token("b", "identifier", L)
    ]
    with pytest.raises(Exception) as e:
        parse(tokens)
    assert(e.value.args[0]) == ':0:0: garbage at end of expression.'
    tokens = [
        Token("1", "identifier", L),
        Token("+", "identifier", L),
        Token("var", "identifier", L),
        Token("a", "identifier", L),
        Token("=", "operator", L),
        Token("b", "identifier", L)
    ]
    with pytest.raises(Exception) as e:
        parse(tokens)
    assert(e.value.args[0]) == ':0:0: garbage at end of expression.'
    tokens = [
        Token("not", "identifier", L),
        Token("var", "identifier", L),
        Token("a", "identifier", L),
        Token("=", "operator", L),
        Token("b", "identifier", L)
    ]
    with pytest.raises(Exception) as e:
        parse(tokens)
    assert(e.value.args[0]) == ':0:0: garbage at end of expression.'
    tokens = [
        Token("c", "identifier", L),
        Token("=", "operator", L),
        Token("var", "identifier", L),
        Token("a", "identifier", L),
        Token("=", "operator", L),
        Token("b", "identifier", L)
    ]
    with pytest.raises(Exception) as e:
        parse(tokens)
    assert(e.value.args[0]) == ':0:0: garbage at end of expression.'