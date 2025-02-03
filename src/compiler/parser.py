from compiler.tokenizer import Token, Source, L
import compiler.ast as ast

def parse(tokens: list[Token]) -> ast.Expression:
    pos = 0
    left_associative_binary_operators = [
        ['or'],
        ['and'],
        ['==', '!='],
        ['<', '<=', '>', '>='],
        ['+', '-'],
        ['*', '/', '%'],
    ]
    right_associative_binary_operators = [
        ['=']
    ]
    unary_operators = [
        ['-', 'not']
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
        return ast.Literal(token.source, int(token.text))
    
    def parse_bool_literal() -> ast.Literal:
        match [peek().type, peek().text]:
            case ["identifier", "true"]:
                token = consume("true")
            case ["identifier", "false"]:
                token = consume("false")
            case _:
                raise Exception(f'{peek().source}: expected bool "true" or "false"')
        
        return ast.Literal(token.source, token.text == "true")

    def parse_identifier() -> ast.Identifier:
        if peek().type != 'identifier':
            raise Exception(f'{peek().source}: expected an identifier')
        token = consume()
        return ast.Identifier(token.source, token.text)
    
    def parse_parenthesized() -> ast.Expression:
        consume('(')
        expr = parse_expression_right_binary()
        consume(')')
        return expr

    def parse_if() -> ast.Conditional:
        location = consume('if').source
        condition = parse_expression_right_binary()
        consume('then')
        then = parse_expression_right_binary()
        if peek().text == 'else':
            consume('else')
            return ast.Conditional(
                location,
                "if",
                condition,
                then,
                parse_expression_right_binary()
            )
        else:
            return ast.Conditional(
                location,
                "if",
                condition,
                then
            )
    def parse_list() -> list[ast.Expression]:
        expr = parse_expression_right_binary()
        if peek().text == ',':
            consume(',')
            return [expr] + parse_list()
        return [expr]

    def parse_function(function_name: ast.Identifier) -> ast.FunctionCall:
        consume('(')
        params = parse_list()
        consume(')')
        return ast.FunctionCall(
            function_name.location,
            function_name,
            params,
        )
    
    def parse_block(first: bool = True) -> ast.Block:
        if first:
            consume('{')
        if peek().text == '}':
            consume('}')
            return ast.Block(L, [], ast.Literal(L, None))

        expr = parse_top()
        if (isinstance(expr, ast.Block) and expr.result == ast.Literal(expr.location, None)):
            block = parse_block(False)
            block.expressions = expr.expressions + block.expressions
            return block
        elif isinstance(expr, ast.Block) and peek().text == "}":
            consume("}")
            return ast.Block(expr.location, [], expr)
        elif isinstance(expr, ast.Block) or isinstance(expr, ast.Conditional):
            block = parse_block(False)
            block.expressions = [expr] + block.expressions
            return block
        else:
            consume('}')
            return ast.Block(expr.location, [], expr)

    def parse_factor() -> ast.Expression:
        expr = ast.Expression(L)
        match peek().type:
            case "punctuation":
                match peek().text:
                    case "(":
                        expr = parse_parenthesized()
                    case "{":
                        expr = parse_block()
            case "identifier":
                match peek().text:
                    case "if":
                        expr = parse_if()
                    case "true" | "false":
                        expr = parse_bool_literal()
                    case _:
                        expr = parse_identifier()
                        if peek().text == '(':
                            expr = parse_function(expr)
            case 'int_literal':
                expr = parse_int_literal()       
            case _:
                raise Exception(f'{peek().source}: expected "(", an integer literal or an identifier')
        return expr

    def parse_expression_unary(index: int = 0) -> ast.Expression:
        if index == len(unary_operators):
            return parse_factor()
        while peek().text in unary_operators[index]:
            operator_token = consume()
            right = parse_expression_unary()
            return ast.UnaryOp(
                operator_token.source,
                operator_token.text,
                right
            )
        return parse_expression_unary(index+1)

    def parse_expression_left_binary(index: int = 0) -> ast.Expression:
        if index == len(left_associative_binary_operators):
            return parse_expression_unary()

        left = parse_expression_left_binary(index+1)
        while peek().text in left_associative_binary_operators[index]:
            operator_token = consume()
            right = parse_expression_left_binary(index+1)
            left = ast.BinaryOp(
                operator_token.source,
                left,
                operator_token.text,
                right
            )
        return left

    def parse_assignment(left : ast.Expression) -> ast.BinaryOp:
        location = consume("=").source
        right = parse_expression_right_binary()
        return ast.BinaryOp(
            location,
            left,
            "=",
            right
        )

    def parse_expression_right_binary() -> ast.Expression:
        left = parse_expression_left_binary()
        if peek().text == '=':
            return parse_assignment(left)
        else:
            return left
    
    def parse_top() -> ast.Expression:
        expr: ast.Expression = ast.Expression(L)
        if peek().text == "var":
            location = consume("var").source
            left = parse_expression_left_binary()
            expr =  ast.UnaryOp(
                location,
                "var",
                parse_assignment(left)
            )
        else:
            expr = parse_expression_right_binary()
        if peek().text == ";":
            consume(";")
            expr = ast.Block(
                expr.location,
                [expr],
                ast.Literal(L, None)
            )
        return expr
    
    main_expression = parse_top()
    if peek().type != "end":
        raise(Exception(f'{peek().source}: garbage at end of expression.'))
    print(main_expression)
    return main_expression
