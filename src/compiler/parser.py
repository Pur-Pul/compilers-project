from compiler.tokenizer import Token, Source
import compiler.ast as ast

def parse(tokens: list[Token]) -> ast.Expression:
    pos = 0

    def peek() -> Token:
        if len(tokens) == 0:
            return Token(
                source=Source("",0,0),
                type="end",
                text="",
            )
        elif pos < len(tokens):
            return tokens[pos]
        else:
            return Token(
                source=tokens[-1].source,
                type="end",
                text="",
            )

    def consume(expected: str | list[str] | None = None) -> Token:
        nonlocal pos
        token = peek()
        if isinstance(expected, str) and token.text != expected:
            raise Exception(f'{token.source}: expected "{expected}"')
        if isinstance(expected, list) and token.text not in expected:
            comma_separated = ", ".join([f'"{e}"' for e in expected])
            raise Exception(f'{token.source}: expected one of: {comma_separated}')
        pos += 1
        return token
    
    def parse_int_literal() -> ast.Literal:
        if peek().type != 'int_literal':
            raise Exception(f'{peek().source}: expected an integer literal')
        token = consume()
        return ast.Literal(int(token.text))
    
    def parse_identifier() -> ast.Identifier:
        if peek().type != 'identifier':
            raise Exception(f'{peek().source}: expected an identifier')
        token = consume()
        return ast.Identifier(token.text)
    
    def parse_parenthesized() -> ast.Expression:
        consume('(')
        expr = parse_expression()
        consume(')')
        return expr

    def parse_factor() -> ast.Expression:
        if peek().text == '(':
            return parse_parenthesized()
        match peek().type:
            case 'int_literal':
                return parse_int_literal()
            case 'identifier':
                return parse_identifier()
            case _:
                raise Exception(f'{peek().source}: expected "(", an integer literal or an identifier')

    def parse_term() -> ast.Expression:
        left = parse_factor()
        while peek().text in ['*', '/']:
            operator_token = consume()
            right = parse_factor()
            left = ast.BinaryOp(
                left,
                operator_token.text,
                right
            )
        return left

    def parse_expression() -> ast.Expression:
        left = parse_term()
        while peek().text in ['+', '-']:
            operator_token = consume()
            right = parse_term()
            left = ast.BinaryOp(
                left,
                operator_token.text,
                right
            )
        return left

    def parse_expression_right() -> ast.Expression:
        left = parse_term()
        if peek().text in ['=']:
            operator_token = consume()
            right = parse_expression_right()
            return ast.BinaryOp(
                left,
                operator_token.text,
                right
            )
        else:
            return left
    
    main_expression = parse_expression()
    if peek().type != "end":
        raise(Exception(f'{peek().source}: garbage at end of expression.'))
    return main_expression
