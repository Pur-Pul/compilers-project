from compiler.tokenizer import Token, Source
import compiler.ast as ast

def parse(tokens: list[Token]) -> ast.Expression:
    pos = 0
    left_associative_binary_operators = [
        ['or'],
        ['and'],
        ['==', '!='],
        ['<', '<=', '>', '>='],
        ['+', '-'],
        ['*', '/'],
    ]
    right_associative_binary_operators = [
        ['=']
    ]

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
        expr = parse_expression_right(0)
        consume(')')
        return expr

    def parse_if() -> ast.IfClause:
        consume('if')
        condition = parse_expression_right(0)
        consume('then')
        then = parse_expression_right(0)
        if peek().text == 'else':
            consume('else')
            return ast.IfClause(
                condition,
                then,
                parse_expression_right(0)
            )
        else:
            return ast.IfClause(
                condition,
                then
            )
    def parse_list() -> list[ast.Expression]:
        expr = parse_expression_right(0)
        if peek().text == ',':
            consume(',')
            return [expr] + parse_list()
        return [expr]

    def parse_function(function_name: ast.Identifier) -> ast.Expression:
        consume('(')
        params = parse_list()
        consume(')')
        return ast.FunctionCall(
            function_name,
            params
        )

    def parse_factor() -> ast.Expression:
        print(peek().text)
        if peek().text == '(':
            return parse_parenthesized()
        elif peek().text == 'if':
            return parse_if()
        match peek().type:
            case 'int_literal':
                return parse_int_literal()
            case 'identifier':
                identifier = parse_identifier()
                if peek().text == '(':
                    return parse_function(identifier)
                return identifier
            case _:
                raise Exception(f'{peek().source}: expected "(", an integer literal or an identifier')

    def parse_expression(index: int) -> ast.Expression:
        if index == len(left_associative_binary_operators):
            return parse_factor()

        left = parse_expression(index+1)
        while peek().text in left_associative_binary_operators[index]:
            operator_token = consume()
            right = parse_expression(index+1)
            left = ast.BinaryOp(
                left,
                operator_token.text,
                right
            )
        return left

    def parse_expression_right(index: int) -> ast.Expression:
        if index == len(right_associative_binary_operators):
            return parse_expression(0)

        left = parse_expression_right(index+1)
        if peek().text in right_associative_binary_operators[index]:
            operator_token = consume()
            right = parse_expression_right(0)
            return ast.Assignment(
                left,
                operator_token.text,
                right
            )
        else:
            return left
    
    main_expression = parse_expression_right(0)
    if peek().type != "end":
        raise(Exception(f'{peek().source}: garbage at end of expression.'))
    return main_expression
