#!/usr/bin/env python3
"""
aurum Parser - Analizador Sintáctico
Analiza la estructura sintáctica del código y genera un AST (Abstract Syntax Tree)
"""

from typing import List, Optional, Any
from dataclasses import dataclass
from abc import ABC

from .lexer import Token, TokenType, AurumLexer


# ========================================
# NODOS DEL AST (Abstract Syntax Tree)
# ========================================

class ASTNode(ABC):
    """Clase base para todos los nodos del AST"""
    pass


@dataclass
class Program(ASTNode):
    """Nodo raíz del programa - contiene todas las funciones"""
    functions: List['Function']


@dataclass
class Function(ASTNode):
    """Definición de función"""
    name: str
    parameters: List['Parameter']
    return_type: str
    body: List['Statement']
    line: int


@dataclass
class Parameter(ASTNode):
    """Parámetro de función"""
    name: str
    type: str


@dataclass
class Statement(ASTNode):
    """Clase base para todas las declaraciones"""
    pass


@dataclass
class Expression(ASTNode):
    """Clase base para todas las expresiones"""
    pass


# ========================================
# TIPOS DE DECLARACIONES (STATEMENTS)
# ========================================

@dataclass
class VariableDeclaration(Statement):
    """Declaración de variable: int x = 5"""
    name: str
    type: str
    value: Optional[Expression]
    line: int


@dataclass
class Assignment(Statement):
    """Asignación: x = 10"""
    name: str
    value: Expression
    line: int


@dataclass
class IfStatement(Statement):
    """Declaración if/elif/else"""
    condition: Expression
    then_body: List[Statement]
    elif_parts: List['ElifPart']
    else_body: Optional[List[Statement]]
    line: int


@dataclass
class ElifPart(ASTNode):
    """Parte elif de un if statement"""
    condition: Expression
    body: List[Statement]


@dataclass
class WhileStatement(Statement):
    """Ciclo while"""
    condition: Expression
    body: List[Statement]
    line: int


@dataclass
class ForStatement(Statement):
    """Ciclo for"""
    init: Optional[Statement]
    condition: Optional[Expression]
    update: Optional[Statement]
    body: List[Statement]
    line: int


@dataclass
class ReturnStatement(Statement):
    """Declaración return"""
    value: Optional[Expression]
    line: int


@dataclass
class BreakStatement(Statement):
    """Declaración break"""
    line: int


@dataclass
class ContinueStatement(Statement):
    """Declaración continue"""
    line: int


@dataclass
class ExpressionStatement(Statement):
    """Expresión usada como declaración"""
    expression: Expression
    line: int


# ========================================
# TIPOS DE EXPRESIONES (EXPRESSIONS)
# ========================================

@dataclass
class BinaryOperation(Expression):
    """Operación binaria: a + b, a == b, etc."""
    left: Expression
    operator: str
    right: Expression


@dataclass
class UnaryOperation(Expression):
    """Operación unaria: -x, not x"""
    operator: str
    operand: Expression


@dataclass
class FunctionCall(Expression):
    """Llamada a función: func(arg1, arg2)"""
    name: str
    arguments: List[Expression]
    line: int


@dataclass
class Variable(Expression):
    """Referencia a variable"""
    name: str
    line: int


@dataclass
class Literal(Expression):
    """Valor literal: números, cadenas, booleanos"""
    value: Any
    type: str


# ========================================
# EXCEPCIONES DE ANÁLISIS SINTÁCTICO
# ========================================

class ParseError(Exception):
    """Excepción para errores de análisis sintáctico"""
    def __init__(self, message: str, line: int, column: int):
        self.message = message
        self.line = line
        self.column = column
        super().__init__(f"Error sintáctico en línea {line}, columna {column}: {message}")


# ========================================
# ANALIZADOR SINTÁCTICO (PARSER)
# ========================================

class AurumParser:
    """Analizador sintáctico para aurum"""
    
    def __init__(self):
        """Inicializa el parser"""
        self.tokens: List[Token] = []
        self.current = 0
        
    def parse(self, source_code: str) -> Program:
        """
        Analiza el código fuente y genera el AST
        
        Args:
            source_code: Código fuente a analizar
            
        Returns:
            AST del programa
            
        Raises:
            ParseError: Si encuentra errores sintácticos
        """
        # Generar tokens
        lexer = AurumLexer()
        all_tokens = lexer.tokenize(source_code)
        
        # Filtrar tokens irrelevantes (whitespace, newlines, comments)
        self.tokens = [token for token in all_tokens 
                      if token.type not in [TokenType.WHITESPACE, TokenType.NEWLINE, TokenType.COMMENT]]
        
        self.current = 0
        
        # Parsear programa
        functions = []
        while not self._is_at_end():
            if self._peek().type == TokenType.EOF:
                break
            function = self._parse_function()
            functions.append(function)
        
        # Verificar que existe función main
        main_found = any(func.name == 'main' for func in functions)
        if not main_found:
            raise ParseError("Se requiere una función 'main'", 1, 1)
        
        return Program(functions)
    
    # metodos auxiliares
    # ========================================
    
    def _peek(self) -> Token:
        """Obtiene el token actual sin consumirlo"""
        if self.current >= len(self.tokens):
            return self.tokens[-1]  # EOF token
        return self.tokens[self.current]
    
    def _previous(self) -> Token:
        """Obtiene el token anterior"""
        return self.tokens[self.current - 1]
    
    def _is_at_end(self) -> bool:
        """Verifica si estamos al final de los tokens"""
        return self.current >= len(self.tokens) or self.tokens[self.current].type == TokenType.EOF
    
    def _advance(self) -> Token:
        """Consume y retorna el token actual"""
        if not self._is_at_end():
            self.current += 1
        return self._previous()
    
    def _check(self, token_type: TokenType) -> bool:
        """Verifica si el token actual es del tipo especificado"""
        if self._is_at_end():
            return False
        return self._peek().type == token_type
    
    def _match(self, *token_types: TokenType) -> bool:
        """Verifica si el token actual coincide con alguno de los tipos dados"""
        for token_type in token_types:
            if self._check(token_type):
                self._advance()
                return True
        return False
    
    def _consume(self, token_type: TokenType, message: str) -> Token:
        """Consume un token del tipo especificado o lanza error"""
        if self._check(token_type):
            return self._advance()
        
        current_token = self._peek()
        raise ParseError(message, current_token.line, current_token.column)
    
    # metodos analisis sintactico
    # ========================================
    
    def _parse_function(self) -> Function:
        """Analiza una definición de función"""
        line = self._peek().line
        
        self._consume(TokenType.FUNC, "Se esperaba 'func'")
        
        # Aceptar tanto IDENTIFIER como MAIN para el nombre de función
        if self._check(TokenType.IDENTIFIER):
            name_token = self._advance()
        elif self._check(TokenType.MAIN):
            name_token = self._advance()
        else:
            current_token = self._peek()
            raise ParseError("Se esperaba nombre de función", current_token.line, current_token.column)
        
        name = name_token.value
        
        self._consume(TokenType.LPAREN, "Se esperaba '(' después del nombre de función")
        
        # Parámetros
        parameters = []
        if not self._check(TokenType.RPAREN):
            parameters.append(self._parse_parameter())
            while self._match(TokenType.COMMA):
                parameters.append(self._parse_parameter())
        
        self._consume(TokenType.RPAREN, "Se esperaba ')' después de los parámetros")
        
        # Tipo de retorno
        self._consume(TokenType.ARROW, "Se esperaba '->' después de los parámetros")
        return_type_token = self._advance()
        
        if return_type_token.type not in [TokenType.INT, TokenType.FLOAT_TYPE, 
                                        TokenType.STRING_TYPE, TokenType.BOOL_TYPE, TokenType.VOID]:
            raise ParseError("Tipo de retorno inválido", return_type_token.line, return_type_token.column)
        
        return_type = return_type_token.value
        
        # Cuerpo de la función
        self._consume(TokenType.LBRACE, "Se esperaba '{' al inicio del cuerpo de función")
        body = self._parse_block()
        self._consume(TokenType.RBRACE, "Se esperaba '}' al final del cuerpo de función")
        
        return Function(name, parameters, return_type, body, line)
    
    def _parse_parameter(self) -> Parameter:
        """Analiza un parámetro de función"""
        type_token = self._advance()
        if type_token.type not in [TokenType.INT, TokenType.FLOAT_TYPE, 
                                 TokenType.STRING_TYPE, TokenType.BOOL_TYPE]:
            raise ParseError("Tipo de parámetro inválido", type_token.line, type_token.column)
        
        name_token = self._consume(TokenType.IDENTIFIER, "Se esperaba nombre del parámetro")
        
        return Parameter(name_token.value, type_token.value)
    
    def _parse_block(self) -> List[Statement]:
        """Analiza un bloque de declaraciones"""
        statements = []
        
        while not self._check(TokenType.RBRACE) and not self._is_at_end():
            stmt = self._parse_statement()
            statements.append(stmt)
        
        return statements
    
    def _parse_statement(self) -> Statement:
        """Analiza una declaración"""
        if self._match(TokenType.IF):
            return self._parse_if_statement()
        
        if self._match(TokenType.WHILE):
            return self._parse_while_statement()
        
        if self._match(TokenType.FOR):
            return self._parse_for_statement()
        
        if self._match(TokenType.RETURN):
            return self._parse_return_statement()
        
        if self._match(TokenType.BREAK):
            return BreakStatement(self._previous().line)
        
        if self._match(TokenType.CONTINUE):
            return ContinueStatement(self._previous().line)
        
        # Verificar declaración de variable o asignación
        if self._check_variable_declaration():
            return self._parse_variable_declaration()
        
        if self._check_assignment():
            return self._parse_assignment()
        
        # Expresión como declaración
        return self._parse_expression_statement()
    
    def _check_variable_declaration(self) -> bool:
        """Verifica si la siguiente declaración es una declaración de variable"""
        return self._check(TokenType.INT) or self._check(TokenType.FLOAT_TYPE) or \
               self._check(TokenType.STRING_TYPE) or self._check(TokenType.BOOL_TYPE)
    
    def _check_assignment(self) -> bool:
        """Verifica si la siguiente declaración es una asignación"""
        if self.current + 1 < len(self.tokens):
            return (self._check(TokenType.IDENTIFIER) and 
                   self.tokens[self.current + 1].type == TokenType.ASSIGN)
        return False
    
    def _parse_variable_declaration(self) -> VariableDeclaration:
        """Analiza una declaración de variable"""
        line = self._peek().line
        
        type_token = self._advance()
        type_name = type_token.value
        
        name_token = self._consume(TokenType.IDENTIFIER, "Se esperaba nombre de variable")
        name = name_token.value
        
        value = None
        if self._match(TokenType.ASSIGN):
            value = self._parse_expression()
        
        return VariableDeclaration(name, type_name, value, line)
    
    def _parse_assignment(self) -> Assignment:
        """Analiza una asignación"""
        line = self._peek().line
        
        name_token = self._consume(TokenType.IDENTIFIER, "Se esperaba nombre de variable")
        name = name_token.value
        
        self._consume(TokenType.ASSIGN, "Se esperaba '='")
        value = self._parse_expression()
        
        return Assignment(name, value, line)
    
    def _parse_if_statement(self) -> IfStatement:
        """Analiza una declaración if"""
        line = self._previous().line
        
        self._consume(TokenType.LPAREN, "Se esperaba '(' después de 'if'")
        condition = self._parse_expression()
        self._consume(TokenType.RPAREN, "Se esperaba ')' después de la condición")
        
        self._consume(TokenType.LBRACE, "Se esperaba '{' después de la condición")
        then_body = self._parse_block()
        self._consume(TokenType.RBRACE, "Se esperaba '}' después del bloque if")
        
        # Manejo de elif
        elif_parts = []
        while self._match(TokenType.ELIF):
            self._consume(TokenType.LPAREN, "Se esperaba '(' después de 'elif'")
            elif_condition = self._parse_expression()
            self._consume(TokenType.RPAREN, "Se esperaba ')' después de la condición elif")
            
            self._consume(TokenType.LBRACE, "Se esperaba '{' después de la condición elif")
            elif_body = self._parse_block()
            self._consume(TokenType.RBRACE, "Se esperaba '}' después del bloque elif")
            
            elif_parts.append(ElifPart(elif_condition, elif_body))
        
        # Manejo de else
        else_body = None
        if self._match(TokenType.ELSE):
            self._consume(TokenType.LBRACE, "Se esperaba '{' después de 'else'")
            else_body = self._parse_block()
            self._consume(TokenType.RBRACE, "Se esperaba '}' después del bloque else")
        
        return IfStatement(condition, then_body, elif_parts, else_body, line)
    
    def _parse_while_statement(self) -> WhileStatement:
        """Analiza una declaración while"""
        line = self._previous().line
        
        self._consume(TokenType.LPAREN, "Se esperaba '(' después de 'while'")
        condition = self._parse_expression()
        self._consume(TokenType.RPAREN, "Se esperaba ')' después de la condición")
        
        self._consume(TokenType.LBRACE, "Se esperaba '{' después de la condición")
        body = self._parse_block()
        self._consume(TokenType.RBRACE, "Se esperaba '}' después del bloque while")
        
        return WhileStatement(condition, body, line)
    
    def _parse_for_statement(self) -> ForStatement:
        """Analiza una declaración for"""
        line = self._previous().line
        
        self._consume(TokenType.LPAREN, "Se esperaba '(' después de 'for'")
        
        # Inicialización
        init = None
        if not self._check(TokenType.SEMICOLON):
            if self._check_variable_declaration():
                init = self._parse_variable_declaration()
            else:
                init = self._parse_expression_statement()
        self._consume(TokenType.SEMICOLON, "Se esperaba ';' después de la inicialización")
        
        # Condición
        condition = None
        if not self._check(TokenType.SEMICOLON):
            condition = self._parse_expression()
        self._consume(TokenType.SEMICOLON, "Se esperaba ';' después de la condición")
        
        # Actualización
        update = None
        if not self._check(TokenType.RPAREN):
            if self._check_assignment():
                update = self._parse_assignment()
            else:
                update = self._parse_expression_statement()
        
        self._consume(TokenType.RPAREN, "Se esperaba ')' después del for")
        
        self._consume(TokenType.LBRACE, "Se esperaba '{' después del for")
        body = self._parse_block()
        self._consume(TokenType.RBRACE, "Se esperaba '}' después del bloque for")
        
        return ForStatement(init, condition, update, body, line)
    
    def _parse_return_statement(self) -> ReturnStatement:
        """Analiza una declaración return"""
        line = self._previous().line
        
        value = None
        if not self._check(TokenType.RBRACE) and not self._is_at_end():
            value = self._parse_expression()
        
        return ReturnStatement(value, line)
    
    def _parse_expression_statement(self) -> ExpressionStatement:
        """Analiza una expresión como declaración"""
        line = self._peek().line
        expr = self._parse_expression()
        return ExpressionStatement(expr, line)
    
    
    # analisis de expresiones
    # ========================================
    
    def _parse_expression(self) -> Expression:
        """Analiza una expresión (precedencia más baja: OR)"""
        return self._parse_or()
    
    def _parse_or(self) -> Expression:
        """Analiza expresiones OR lógicas"""
        expr = self._parse_and()
        
        while self._match(TokenType.OR):
            operator = self._previous().value
            right = self._parse_and()
            expr = BinaryOperation(expr, operator, right)
        
        return expr
    
    def _parse_and(self) -> Expression:
        """Analiza expresiones AND lógicas"""
        expr = self._parse_equality()
        
        while self._match(TokenType.AND):
            operator = self._previous().value
            right = self._parse_equality()
            expr = BinaryOperation(expr, operator, right)
        
        return expr
    
    def _parse_equality(self) -> Expression:
        """Analiza expresiones de igualdad"""
        expr = self._parse_comparison()
        
        while self._match(TokenType.EQUAL, TokenType.NOT_EQUAL):
            operator = self._previous().value
            right = self._parse_comparison()
            expr = BinaryOperation(expr, operator, right)
        
        return expr
    
    def _parse_comparison(self) -> Expression:
        """Analiza expresiones de comparación"""
        expr = self._parse_term()
        
        while self._match(TokenType.GREATER_THAN, TokenType.GREATER_EQUAL,
                          TokenType.LESS_THAN, TokenType.LESS_EQUAL):
            operator = self._previous().value
            right = self._parse_term()
            expr = BinaryOperation(expr, operator, right)
        
        return expr
    
    def _parse_term(self) -> Expression:
        """Analiza expresiones de suma y resta"""
        expr = self._parse_factor()
        
        while self._match(TokenType.PLUS, TokenType.MINUS):
            operator = self._previous().value
            right = self._parse_factor()
            expr = BinaryOperation(expr, operator, right)
        
        return expr
    
    def _parse_factor(self) -> Expression:
        """Analiza expresiones de multiplicación y división"""
        expr = self._parse_unary()
        
        while self._match(TokenType.MULTIPLY, TokenType.DIVIDE, TokenType.MODULO):
            operator = self._previous().value
            right = self._parse_unary()
            expr = BinaryOperation(expr, operator, right)
        
        return expr
    
    def _parse_unary(self) -> Expression:
        """Analiza expresiones unarias"""
        if self._match(TokenType.NOT, TokenType.MINUS):
            operator = self._previous().value
            right = self._parse_unary()
            return UnaryOperation(operator, right)
        
        return self._parse_call()
    
    def _parse_call(self) -> Expression:
        """Analiza llamadas a función"""
        expr = self._parse_primary()
        
        if self._match(TokenType.LPAREN):
            # Es una llamada a función
            if isinstance(expr, Variable):
                arguments = []
                if not self._check(TokenType.RPAREN):
                    arguments.append(self._parse_expression())
                    while self._match(TokenType.COMMA):
                        arguments.append(self._parse_expression())
                
                self._consume(TokenType.RPAREN, "Se esperaba ')' después de los argumentos")
                return FunctionCall(expr.name, arguments, expr.line)
            else:
                raise ParseError("Solo se pueden llamar funciones", self._previous().line, self._previous().column)
        
        return expr
    
    def _parse_primary(self) -> Expression:
        """Analiza expresiones primarias"""
        if self._match(TokenType.BOOLEAN):
            value = self._previous().value == "true"
            return Literal(value, "bool")
        
        if self._match(TokenType.INTEGER):
            value = int(self._previous().value)
            return Literal(value, "int")
        
        if self._match(TokenType.FLOAT):
            value = float(self._previous().value)
            return Literal(value, "float")
        
        if self._match(TokenType.STRING):
            # Remover comillas
            value = self._previous().value[1:-1]
            return Literal(value, "string")
        
        if self._match(TokenType.IDENTIFIER):
            name = self._previous().value
            line = self._previous().line
            return Variable(name, line)
        
        if self._match(TokenType.READ):
            # read() es una función especial
            self._consume(TokenType.LPAREN, "Se esperaba '(' después de 'read'")
            self._consume(TokenType.RPAREN, "Se esperaba ')' después de 'read'")
            return FunctionCall("read", [], self._previous().line)
        
        if self._match(TokenType.LPAREN):
            expr = self._parse_expression()
            self._consume(TokenType.RPAREN, "Se esperaba ')' después de la expresión")
            return expr
        
        current_token = self._peek()
        raise ParseError(f"Expresión inesperada: '{current_token.value}'", 
                        current_token.line, current_token.column)


def main():
    """Función de prueba del parser"""
    parser = AurumParser()
    
    # Código de prueba
    test_code = '''
    func main() -> void {
        int edad = 25
        string nombre = "Juan"
        
        if (edad >= 18) {
            print("Eres mayor de edad")
        } else {
            print("Eres menor de edad")
        }
        
        int resultado = calcular(10, 20)
        print("El resultado es: " + resultado)
    }
    
    func calcular(int a, int b) -> int {
        return a + b
    }
    '''
    
    try:
        ast = parser.parse(test_code)
        print("🌳 ANÁLISIS SINTÁCTICO COMPLETADO")
        print("=" * 50)
        print(f"Programa con {len(ast.functions)} funciones:")
        
        for func in ast.functions:
            print(f"  - {func.name}({', '.join(f'{p.type} {p.name}' for p in func.parameters)}) -> {func.return_type}")
        
        print("\n✅ AST generado correctamente!")
        
    except ParseError as e:
        print(f"❌ {e}")


if __name__ == "__main__":
    main()
