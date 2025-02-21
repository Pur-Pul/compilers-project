from compiler.tokenizer import Token, Source, L
import compiler.ast as ast
import compiler.types as types
from typing import Optional

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
    
    def peek_last() -> Token:
        if len(tokens) == 0:
            return Token(
                source=Source("",0,0),
                type="end",
                text="",
            )
        elif pos-1 > 0:
            return tokens[pos-1]
        else:
            return Token(
                source=tokens[0].source,
                type="start",
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
    
    def parse_bool_literal(bool: str) -> ast.Literal:
        token = consume(bool)
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

    def parse_conditional(operator: str) -> ast.Conditional:
        location = consume(operator).source 
        expr = ast.Conditional(
            location,
            operator,
            parse_expression_right_binary(),
            ast.Expression(L)
        )
        if operator == "if":
            consume("then")
            expr.first = parse_expression_right_binary()
            if peek().text == "else":
                consume("else")
                expr.second = parse_expression_right_binary()
        else:
            consume("do")
            expr.first = parse_expression_right_binary()

        return expr

    def parse_list() -> list[ast.Expression]:
        expr = parse_expression_right_binary()
        if peek().text == ',':
            consume(',')
            return [expr] + parse_list()
        return [expr]

    def parse_function(function_name: ast.Identifier) -> ast.FunctionCall:
        consume('(')
        params = parse_list() if peek().text != ')' else []
        consume(')')
        return ast.FunctionCall(
            function_name.location,
            function_name,
            params,
        )
    
    def parse_block(expressions: list[ast.Expression] = [], last: Optional[ast.Expression] = None) -> ast.Block:
        expr: ast.Expression = ast.Literal(L, None)
        
        if peek().type != "end":
            expr = parse_top(False)

        separator = consume(";") if peek().text == ";" else None
        
        if separator is None and expr == ast.Literal(expr.location, None):
            expr = expr if last is None else last
            return ast.Block(expr.location, expressions, expr)

        elif separator is None and peek_last().text == "}":#isinstance(expr, (ast.Block, ast.Conditional)):
            expressions = expressions if last is None else expressions+[last]
            return parse_block(expressions, expr)

        elif separator is None:
            expressions = expressions if last is None else expressions+[last]
            return ast.Block(expr.location, expressions, expr)
        
        else:
            expressions = expressions if last is None else expressions+[last]
            return parse_block(expressions + [expr])
     

    def parse_variable_declaration() -> ast.VariableDeclaration:
        var = consume("var")
        name = parse_identifier()
        var_type = None
        if peek().text == ':':
            consume(':')
            type_identifier = parse_identifier()
            if not type_identifier.name in types.Types:
                raise Exception(f"{type_identifier.location}: Unknown type '{type_identifier.name}'.")
            var_type = types.Types[type_identifier.name]
        return ast.VariableDeclaration(var.source, name, var_type)

    def parse_factor(top: bool = True) -> ast.Expression:
        expr = ast.Expression(L)
        
        match peek().type:
            case "punctuation":
                match peek().text:
                    case "(":
                        expr = parse_parenthesized()
                    case "{":
                        consume("{")
                        expr = parse_block()
                        consume("}")
                    case "}":
                        return ast.Literal(peek().source, None)
            case "identifier":
                if top and peek().text == "var":
                    expr = parse_variable_declaration()
                else:
                    match peek().text:
                        case "if" | "while":
                            expr = parse_conditional(peek().text)
                        case "true" | "false":
                            expr = parse_bool_literal(peek().text)
                        case _:
                            expr = parse_identifier()
                            if peek().text == '(':
                                expr = parse_function(expr)
            case 'int_literal':
                expr = parse_int_literal()       
            case _:
                raise Exception(f'{peek().source}: expected "(", an integer literal or an identifier')
        return expr

    def parse_expression_unary(index: int = 0, top: bool = True) -> ast.Expression:
        if index == len(unary_operators):
            return parse_factor(top)
        while peek().text in unary_operators[index]:
            operator_token = consume()
            right = parse_expression_unary(top = False)
            return ast.UnaryOp(
                operator_token.source,
                operator_token.text,
                right
            )
        return parse_expression_unary(index+1, top)

    def parse_expression_left_binary(index: int = 0, top: bool = True) -> ast.Expression:
        if index == len(left_associative_binary_operators):
            return parse_expression_unary(top=top)

        left = parse_expression_left_binary(index+1, top)
        while peek().text in left_associative_binary_operators[index]:
            operator_token = consume()
            right = parse_expression_left_binary(index+1, False)
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

    def parse_expression_right_binary(top: bool = False) -> ast.Expression:
        left = parse_expression_left_binary(top=top)
        if peek().text == '=':
            return parse_assignment(left)
        else:
            return left
    
    def parse_top(top : bool = True) -> ast.Expression:
        expr = parse_expression_right_binary(top=True)
        if top:
            separator = consume(";") if peek().text == ";" else None
            if separator is not None or (peek_last().text == "}" and peek().type != "end"):
                expr = parse_block([expr])
        return expr
    
    main_expression = parse_top()
    if peek().type != "end":
        raise(Exception(f'{peek().source}: garbage at end of expression.'))
    return main_expression
