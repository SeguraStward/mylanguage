#!/usr/bin/env python3
"""
Alchemist Parser - Analizador Sintactico
Analiza la estructura sintactica del codigo y genera un AST (Abstract Syntax Tree)
"""

from typing import List, Optional, Any
from dataclasses import dataclass
from abc import ABC

from typing import List, Optional, Any
from dataclasses import dataclass
from abc import ABC

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.lexer import AlchemistLexer, Token, TokenType


# ========================================
# NODOS DEL AST (Abstract Syntax Tree)
# ========================================

class ASTNode(ABC):
    """Clase base para todos los nodos del AST"""
    pass


@dataclass
class Program(ASTNode):
    """Nodo raiz del programa - contiene todas las funciones"""
    functions: List['Function']


@dataclass
class Function(ASTNode):
    """Definicion de funcion"""
    name: str
    parameters: List['Parameter']
    return_type: str
    body: List['Statement']
    line: int


@dataclass
class Parameter(ASTNode):
    """Parametro de funcion"""
    name: str
    type: str


@dataclass
class Statement(ASTNode):
    """Clase base para declaraciones"""
    pass


@dataclass
class ObserveStatement(Statement):
    """Declaracion Observe/Alternatively/Inevitably"""
    condition: 'Expression'
    then_body: List['Statement']
    alternatively_parts: List['AlternativelyPart']
    inevitably_body: Optional[List['Statement']]
    line: int


@dataclass
class AlternativelyPart(ASTNode):
    """Parte Alternatively de un Observe statement"""
    condition: 'Expression'
    body: List['Statement']


@dataclass
class Expression(ASTNode):
    """Clase base para todas las expresiones"""
    pass


# ========================================
# TIPOS DE DECLARACIONES (STATEMENTS)
# ========================================

@dataclass
class VariableDeclaration(Statement):
    """Declaracion de variable: int x = 5"""
    name: str
    type: str
    value: Optional[Expression]
    line: int


@dataclass
class Assignment(Statement):
    """Asignacion: x = 10"""
    name: str
    value: Expression
    line: int


@dataclass
class ArrayDeclaration(Statement):
    """Declaracion de array: AlchemicArray[Solid, 5] numeros"""
    name: str
    element_type: str
    size: int
    line: int


@dataclass
class ArrayAssignment(Statement):
    """Asignacion a elemento de array: numeros[0] = 10"""
    name: str
    index: Expression
    value: Expression
    line: int


@dataclass
class MatrixDeclaration(Statement):
    """Declaracion de matriz: AlchemicMatrix[Solid, 3, 4] matriz"""
    name: str
    element_type: str
    rows: int
    cols: int
    line: int


@dataclass
class MatrixAssignment(Statement):
    """Asignacion a elemento de matriz: matriz[1][2] = 10"""
    name: str
    row_index: Expression
    col_index: Expression
    value: Expression
    line: int


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
    """Declaracion return"""
    value: Optional[Expression]
    line: int


@dataclass
class BreakStatement(Statement):
    """Declaracion break"""
    line: int


@dataclass
class ContinueStatement(Statement):
    """Declaracion continue"""
    line: int


@dataclass
class ExpressionStatement(Statement):
    """Expresion usada como declaracion"""
    expression: Expression
    line: int


# ========================================
# TIPOS DE EXPRESIONES (EXPRESSIONS)
# ========================================

@dataclass
class BinaryOperation(Expression):
    """Operacion binaria: a + b, a == b, etc."""
    left: Expression
    operator: str
    right: Expression


@dataclass
class UnaryOperation(Expression):
    """Operacion unaria: -x, not x"""
    operator: str
    operand: Expression


@dataclass
class FunctionCall(Expression):
    """Llamada a funcion: func(arg1, arg2)"""
    name: str
    arguments: List[Expression]
    line: int


@dataclass
class Variable(Expression):
    """Referencia a variable"""
    name: str
    line: int


@dataclass
class ArrayAccess(Expression):
    """Acceso a elemento de array: numeros[0]"""
    name: str
    index: Expression
    line: int


@dataclass
class MatrixAccess(Expression):
    """Acceso a elemento de matriz: matriz[1][2]"""
    name: str
    row_index: Expression
    col_index: Expression
    line: int


@dataclass
class Literal(Expression):
    """Valor literal: números, cadenas, booleanos"""
    value: Any
    type: str


# ========================================
# EXCEPCIONES DE ANALISIS SINTACTICO
# ========================================

class ParseError(Exception):
    """Excepcion para errores de analisis sintactico"""
    def __init__(self, message: str, line: int, column: int):
        self.message = message
        self.line = line
        self.column = column
        super().__init__(f"Error sintactico en linea {line}, columna {column}: {message}")


# ========================================
# ANALIZADOR SINTaCTICO (PARSER)
# ========================================

class AlchemistParser:
    """Analizador sintactico para Alchemist"""
    
    def __init__(self):
        """Inicializa el parser"""
        self.tokens: List[Token] = []
        self.current = 0
        
    def parse(self, source_code: str) -> Program:
        """
        Analiza el codigo fuente y genera el AST
        
        Args:
            source_code: Codigo fuente a analizar
            
        Returns:
            AST del programa
            
        Raises:
            ParseError: Si encuentra errores sintacticos
        """
        # Generar tokens
        lexer = AlchemistLexer()
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
        
        # Verificar que existe funcion GateOfTruth (funcion principal)
        gateoftruth_found = any(func.name == 'GateOfTruth' for func in functions)
        if not gateoftruth_found:
            raise ParseError("Se requiere una funcion principal 'GateOfTruth'", 1, 1)
        
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
        """Analiza una definicion de funcion"""
        line = self._peek().line
        
        self._consume(TokenType.TRANSMUTATION, "Se esperaba 'Transmutation'")
        
        # Solo aceptar IDENTIFIER para el nombre de funcion
        if self._check(TokenType.IDENTIFIER):
            name_token = self._advance()
        else:
            current_token = self._peek()
            raise ParseError("Se esperaba nombre de funcion", current_token.line, current_token.column)
        
        name = name_token.value
        
        self._consume(TokenType.LPAREN, "Se esperaba '(' despues del nombre de funcion")
        
        # Parametros
        parameters = []
        if not self._check(TokenType.RPAREN):
            parameters.append(self._parse_parameter())
            while self._match(TokenType.COMMA):
                parameters.append(self._parse_parameter())
        
        self._consume(TokenType.RPAREN, "Se esperaba ')' despues de los parametros")
        
        # Tipo de retorno
        self._consume(TokenType.ARROW, "Se esperaba '->' despues de los parametros")
        return_type_token = self._advance()
        
        if return_type_token.type not in [TokenType.SOLID_TYPE, TokenType.LIQUID_TYPE, 
                                        TokenType.INSCRIPTION_TYPE, TokenType.PRINCIPLE_TYPE, TokenType.VOID]:
            raise ParseError("Tipo de retorno invalido", return_type_token.line, return_type_token.column)
        
        return_type = return_type_token.value
        
        # Cuerpo de la funcion
        self._consume(TokenType.LBRACE, "Se esperaba '{' al inicio del cuerpo de funcion")
        body = self._parse_block()
        self._consume(TokenType.RBRACE, "Se esperaba '}' al final del cuerpo de funcion")
        
        return Function(name, parameters, return_type, body, line)
    
    def _parse_parameter(self) -> Parameter:
        """Analiza un parametro de funcion"""
        type_token = self._advance()
        if type_token.type not in [TokenType.SOLID_TYPE, TokenType.LIQUID_TYPE, 
                                 TokenType.INSCRIPTION_TYPE, TokenType.PRINCIPLE_TYPE]:
            raise ParseError("Tipo de parametro invalido", type_token.line, type_token.column)
        
        name_token = self._consume(TokenType.IDENTIFIER, "Se esperaba nombre del parametro")
        
        return Parameter(name_token.value, type_token.value)
    
    def _parse_block(self) -> List[Statement]:
        """Analiza un bloque de declaraciones"""
        statements = []
        
        while not self._check(TokenType.RBRACE) and not self._is_at_end():
            stmt = self._parse_statement()
            statements.append(stmt)
        
        return statements
    
    def _parse_statement(self) -> Statement:
        """Analiza una declaracion"""
        if self._match(TokenType.OBSERVE):
            return self._parse_observe_statement()
        
        if self._match(TokenType.TRANSMUTEUNTIL):
            return self._parse_transmuteuntil_statement()
        
        if self._match(TokenType.ALCHEMICCYCLE):
            return self._parse_alchemiccycle_statement()
        
        if self._match(TokenType.EQUIVALENTEXCHANGE, TokenType.RETURN):
            return self._parse_return_statement()
        
        if self._match(TokenType.BREAK):
            return BreakStatement(self._previous().line)
        
        if self._match(TokenType.CONTINUE):
            return ContinueStatement(self._previous().line)
        
        # Verificar declaracion de array
        if self._match(TokenType.ALCHEMICARRAY):
            return self._parse_array_declaration()
        
        # Verificar declaracion de matriz
        if self._match(TokenType.ALCHEMICMATRIX):
            return self._parse_matrix_declaration()
        
        # Verificar declaracion de variable o asignacion
        if self._check_variable_declaration():
            return self._parse_variable_declaration()
        
        # Verificar asignación a matriz: nombre[fila][col] = valor
        if self._check_matrix_assignment():
            return self._parse_matrix_assignment()
        
        # Verificar asignación a array: nombre[indice] = valor
        if self._check_array_assignment():
            return self._parse_array_assignment()
        
        if self._check_assignment():
            return self._parse_assignment()
        
        # Expresion como declaracion
        return self._parse_expression_statement()
    
    def _check_variable_declaration(self) -> bool:
        """Verifica si la siguiente declaracion es una declaracion de variable"""
        return self._check(TokenType.SOLID_TYPE) or self._check(TokenType.LIQUID_TYPE) or \
               self._check(TokenType.INSCRIPTION_TYPE) or self._check(TokenType.PRINCIPLE_TYPE)
    
    def _check_assignment(self) -> bool:
        """Verifica si la siguiente declaracion es una asignacion"""
        if self.current + 1 < len(self.tokens):
            return (self._check(TokenType.IDENTIFIER) and 
                   self.tokens[self.current + 1].type == TokenType.ASSIGN)
        return False
    
    def _parse_variable_declaration(self) -> VariableDeclaration:
        """Analiza una declaracion de variable"""
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
        """Analiza una asignacion"""
        line = self._peek().line
        
        name_token = self._consume(TokenType.IDENTIFIER, "Se esperaba nombre de variable")
        name = name_token.value
        
        self._consume(TokenType.ASSIGN, "Se esperaba '='")
        value = self._parse_expression()
        
        return Assignment(name, value, line)
    
    def _check_array_assignment(self) -> bool:
        """Verifica si es asignacion a array: nombre[indice] = valor"""
        if self.current + 1 < len(self.tokens):
            return (self._check(TokenType.IDENTIFIER) and 
                   self.tokens[self.current + 1].type == TokenType.LBRACKET)
        return False
    
    def _parse_array_declaration(self) -> 'ArrayDeclaration':
        """Analiza declaracion de array: AlchemicArray[Solid, 5] numeros"""
        line = self._previous().line
        
        # Esperar [
        self._consume(TokenType.LBRACKET, "Se esperaba '[' despues de 'AlchemicArray'")
        
        # Tipo de elementos
        type_token = self._advance()
        if type_token.type not in [TokenType.SOLID_TYPE, TokenType.LIQUID_TYPE, 
                                    TokenType.INSCRIPTION_TYPE, TokenType.PRINCIPLE_TYPE]:
            raise ParseError(f"Tipo de elemento invalido para array: {type_token.value}", 
                           type_token.line, type_token.column)
        element_type = type_token.value
        
        # Esperar ,
        self._consume(TokenType.COMMA, "Se esperaba ',' despues del tipo de elemento")
        
        # Tamaño del array
        size_token = self._consume(TokenType.INTEGER, "Se esperaba tamaño del array (numero entero)")
        size = int(size_token.value)
        
        if size <= 0:
            raise ParseError(f"El tamaño del array debe ser mayor a 0", 
                           size_token.line, size_token.column)
        
        # Esperar ]
        self._consume(TokenType.RBRACKET, "Se esperaba ']' despues del tamaño")
        
        # Nombre del array
        name_token = self._consume(TokenType.IDENTIFIER, "Se esperaba nombre del array")
        name = name_token.value
        
        return ArrayDeclaration(name, element_type, size, line)
    
    def _parse_array_assignment(self) -> 'ArrayAssignment':
        """Analiza asignacion a array: numeros[0] = 10"""
        line = self._peek().line
        
        # Nombre del array
        name_token = self._consume(TokenType.IDENTIFIER, "Se esperaba nombre del array")
        name = name_token.value
        
        # [
        self._consume(TokenType.LBRACKET, "Se esperaba '['")
        
        # Indice
        index = self._parse_expression()
        
        # ]
        self._consume(TokenType.RBRACKET, "Se esperaba ']'")
        
        # =
        self._consume(TokenType.ASSIGN, "Se esperaba '='")
        
        # Valor
        value = self._parse_expression()
        
        return ArrayAssignment(name, index, value, line)
    
    def _check_matrix_assignment(self) -> bool:
        """Verifica si es asignacion a matriz: nombre[fila][col] = valor"""
        if self.current + 3 < len(self.tokens):
            return (self._check(TokenType.IDENTIFIER) and 
                   self.tokens[self.current + 1].type == TokenType.LBRACKET and
                   self._has_double_bracket())
        return False
    
    def _has_double_bracket(self) -> bool:
        """Verifica si hay doble corchete [x][y]"""
        bracket_count = 0
        i = self.current + 1
        while i < len(self.tokens) and bracket_count < 2:
            if self.tokens[i].type == TokenType.LBRACKET:
                bracket_count += 1
            elif self.tokens[i].type == TokenType.RBRACKET:
                # Verificar si hay otro [ después del ]
                if bracket_count == 1 and i + 1 < len(self.tokens):
                    if self.tokens[i + 1].type == TokenType.LBRACKET:
                        return True
                    return False
            i += 1
        return False
    
    def _parse_matrix_declaration(self) -> 'MatrixDeclaration':
        """Analiza declaracion de matriz: AlchemicMatrix[Solid, 3, 4] matriz"""
        line = self._previous().line
        
        # Esperar [
        self._consume(TokenType.LBRACKET, "Se esperaba '[' despues de 'AlchemicMatrix'")
        
        # Tipo de elementos
        type_token = self._advance()
        if type_token.type not in [TokenType.SOLID_TYPE, TokenType.LIQUID_TYPE, 
                                    TokenType.INSCRIPTION_TYPE, TokenType.PRINCIPLE_TYPE]:
            raise ParseError(f"Tipo de elemento invalido para matriz: {type_token.value}", 
                           type_token.line, type_token.column)
        element_type = type_token.value
        
        # Esperar ,
        self._consume(TokenType.COMMA, "Se esperaba ',' despues del tipo de elemento")
        
        # Número de filas
        rows_token = self._consume(TokenType.INTEGER, "Se esperaba numero de filas (numero entero)")
        rows = int(rows_token.value)
        
        if rows <= 0:
            raise ParseError(f"El numero de filas debe ser mayor a 0", 
                           rows_token.line, rows_token.column)
        
        # Esperar ,
        self._consume(TokenType.COMMA, "Se esperaba ',' despues del numero de filas")
        
        # Número de columnas
        cols_token = self._consume(TokenType.INTEGER, "Se esperaba numero de columnas (numero entero)")
        cols = int(cols_token.value)
        
        if cols <= 0:
            raise ParseError(f"El numero de columnas debe ser mayor a 0", 
                           cols_token.line, cols_token.column)
        
        # Esperar ]
        self._consume(TokenType.RBRACKET, "Se esperaba ']' despues del numero de columnas")
        
        # Nombre de la matriz
        name_token = self._consume(TokenType.IDENTIFIER, "Se esperaba nombre de la matriz")
        name = name_token.value
        
        return MatrixDeclaration(name, element_type, rows, cols, line)
    
    def _parse_matrix_assignment(self) -> 'MatrixAssignment':
        """Analiza asignacion a matriz: matriz[1][2] = 10"""
        line = self._peek().line
        
        # Nombre de la matriz
        name_token = self._consume(TokenType.IDENTIFIER, "Se esperaba nombre de la matriz")
        name = name_token.value
        
        # [
        self._consume(TokenType.LBRACKET, "Se esperaba '['")
        
        # Índice de fila
        row_index = self._parse_expression()
        
        # ]
        self._consume(TokenType.RBRACKET, "Se esperaba ']'")
        
        # [
        self._consume(TokenType.LBRACKET, "Se esperaba segundo '['")
        
        # Índice de columna
        col_index = self._parse_expression()
        
        # ]
        self._consume(TokenType.RBRACKET, "Se esperaba segundo ']'")
        
        # =
        self._consume(TokenType.ASSIGN, "Se esperaba '='")
        
        # Valor
        value = self._parse_expression()
        
        return MatrixAssignment(name, row_index, col_index, value, line)
    
    def _parse_observe_statement(self) -> ObserveStatement:
        """Analiza una declaracion Observe"""
        line = self._previous().line
        
        self._consume(TokenType.LPAREN, "Se esperaba '(' despues de 'Observe'")
        condition = self._parse_expression()
        self._consume(TokenType.RPAREN, "Se esperaba ')' despues de la condicion")
        
        self._consume(TokenType.LBRACE, "Se esperaba '{' despues de la condicion")
        then_body = self._parse_block()
        self._consume(TokenType.RBRACE, "Se esperaba '}' despues del bloque Observe")
        
        # Manejo de Alternatively
        alternatively_parts = []
        while self._match(TokenType.ALTERNATIVELY):
            self._consume(TokenType.LPAREN, "Se esperaba '(' despues de 'Alternatively'")
            alternatively_condition = self._parse_expression()
            self._consume(TokenType.RPAREN, "Se esperaba ')' despues de la condicion Alternatively")
            
            self._consume(TokenType.LBRACE, "Se esperaba '{' despues de la condicion Alternatively")
            alternatively_body = self._parse_block()
            self._consume(TokenType.RBRACE, "Se esperaba '}' despues del bloque Alternatively")
            
            alternatively_parts.append(AlternativelyPart(alternatively_condition, alternatively_body))
        
        # Manejo de Inevitably
        inevitably_body = None
        if self._match(TokenType.INEVITABLY):
            self._consume(TokenType.LBRACE, "Se esperaba '{' despues de 'Inevitably'")
            inevitably_body = self._parse_block()
            self._consume(TokenType.RBRACE, "Se esperaba '}' despues del bloque Inevitably")
        
        return ObserveStatement(condition, then_body, alternatively_parts, inevitably_body, line)
    
    def _parse_transmuteuntil_statement(self) -> WhileStatement:
        """Analiza una declaracion TransmuteUntil"""
        line = self._previous().line
        
        self._consume(TokenType.LPAREN, "Se esperaba '(' despues de 'TransmuteUntil'")
        condition = self._parse_expression()
        self._consume(TokenType.RPAREN, "Se esperaba ')' despues de la condicion")
        
        self._consume(TokenType.LBRACE, "Se esperaba '{' despues de la condicion")
        body = self._parse_block()
        self._consume(TokenType.RBRACE, "Se esperaba '}' despues del bloque TransmuteUntil")
        
        return WhileStatement(condition, body, line)
    
    def _parse_alchemiccycle_statement(self) -> ForStatement:
        """Analiza una declaracion AlchemicCycle"""
        line = self._previous().line
        
        self._consume(TokenType.LPAREN, "Se esperaba '(' despues de 'AlchemicCycle'")
        
        # Inicializacion
        init = None
        if not self._check(TokenType.SEMICOLON):
            if self._check_variable_declaration():
                init = self._parse_variable_declaration()
            else:
                init = self._parse_expression_statement()
        self._consume(TokenType.SEMICOLON, "Se esperaba ';' despues de la inicializacion")
        
        # Condicion
        condition = None
        if not self._check(TokenType.SEMICOLON):
            condition = self._parse_expression()
        self._consume(TokenType.SEMICOLON, "Se esperaba ';' despues de la condicion")
        
        # Actualizacion
        update = None
        if not self._check(TokenType.RPAREN):
            if self._check_assignment():
                update = self._parse_assignment()
            else:
                update = self._parse_expression_statement()
        
        self._consume(TokenType.RPAREN, "Se esperaba ')' despues del for")
        
        self._consume(TokenType.LBRACE, "Se esperaba '{' despues del for")
        body = self._parse_block()
        self._consume(TokenType.RBRACE, "Se esperaba '}' despues del bloque for")
        
        return ForStatement(init, condition, update, body, line)
    
    def _parse_return_statement(self) -> ReturnStatement:
        """Analiza una declaracion return"""
        line = self._previous().line
        
        value = None
        if not self._check(TokenType.RBRACE) and not self._is_at_end():
            value = self._parse_expression()
        
        return ReturnStatement(value, line)
    
    def _parse_expression_statement(self) -> ExpressionStatement:
        """Analiza una expresion como declaracion"""
        line = self._peek().line
        expr = self._parse_expression()
        return ExpressionStatement(expr, line)
    
    
    # analisis de expresiones 
    
    def _parse_expression(self) -> Expression:
        """Analiza una expresion (precedencia mas baja: OR)"""
        return self._parse_or()
    
    def _parse_or(self) -> Expression:
        """Analiza expresiones OR logicas"""
        expr = self._parse_and()
        
        while self._match(TokenType.OR):
            operator = self._previous().value
            right = self._parse_and()
            expr = BinaryOperation(expr, operator, right)
        
        return expr
    
    def _parse_and(self) -> Expression:
        """Analiza expresiones AND logicas"""
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
        """Analiza expresiones de comparacion"""
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
        """Analiza expresiones de multiplicacion y division"""
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
        """Analiza llamadas a funcion y acceso a arrays/matrices"""
        expr = self._parse_primary()
        
        # Acceso a array/matriz: nombre[indice] o nombre[fila][col]
        if self._match(TokenType.LBRACKET):
            if isinstance(expr, Variable):
                first_index = self._parse_expression()
                self._consume(TokenType.RBRACKET, "Se esperaba ']' despues del indice")
                
                # Verificar si es matriz (doble corchete)
                if self._match(TokenType.LBRACKET):
                    second_index = self._parse_expression()
                    self._consume(TokenType.RBRACKET, "Se esperaba ']' despues del segundo indice")
                    return MatrixAccess(expr.name, first_index, second_index, expr.line)
                else:
                    # Es acceso a array simple
                    return ArrayAccess(expr.name, first_index, expr.line)
            else:
                raise ParseError("Solo se puede acceder a arrays/matrices con []", 
                               self._previous().line, self._previous().column)
        
        # Llamada a función: nombre(args)
        if self._match(TokenType.LPAREN):
            # Es una llamada a funcion
            if isinstance(expr, Variable):
                arguments = []
                if not self._check(TokenType.RPAREN):
                    arguments.append(self._parse_expression())
                    while self._match(TokenType.COMMA):
                        arguments.append(self._parse_expression())
                
                self._consume(TokenType.RPAREN, "Se esperaba ')' despues de los argumentos")
                return FunctionCall(expr.name, arguments, expr.line)
            else:
                raise ParseError("Solo se pueden llamar funciones", self._previous().line, self._previous().column)
        
        return expr
    
    def _parse_primary(self) -> Expression:
        """Analiza expresiones primarias"""
        if self._match(TokenType.ACCEPTED):
            return Literal(True, "Principle")
        
        if self._match(TokenType.REJECTED):
            return Literal(False, "Principle")
        
        if self._match(TokenType.EMPTINESS):
            return Literal(None, "Emptiness")
        
        if self._match(TokenType.INTEGER):
            value = int(self._previous().value)
            return Literal(value, "Solid")
        
        if self._match(TokenType.FLOAT):
            value = float(self._previous().value)
            return Literal(value, "Liquid")
        
        if self._match(TokenType.STRING):
            # Remover comillas
            value = self._previous().value[1:-1]
            return Literal(value, "Inscription")
        
        # Manejar Transmute como función especial
        if self._match(TokenType.TRANSMUTE):
            name = self._previous().value
            line = self._previous().line
            return Variable(name, line)
        
        # Manejar TransmuteLine como función especial
        if self._match(TokenType.TRANSMUTELINE):
            name = self._previous().value
            line = self._previous().line
            return Variable(name, line)
        
        # Manejar Absorb como función especial  
        if self._match(TokenType.ABSORB):
            name = self._previous().value
            line = self._previous().line
            return Variable(name, line)
            
        # Manejar AbsorbSolid como función especial
        if self._match(TokenType.ABSORBSOLID):
            name = self._previous().value
            line = self._previous().line
            return Variable(name, line)
        
        # Manejar AbsorbLiquid como función especial
        if self._match(TokenType.ABSORBLIQUID):
            name = self._previous().value
            line = self._previous().line
            return Variable(name, line)
        
        # Manejar AbsorbPrinciple como función especial
        if self._match(TokenType.ABSORBPRINCIPLE):
            name = self._previous().value
            line = self._previous().line
            return Variable(name, line)
        
        if self._match(TokenType.IDENTIFIER):
            name = self._previous().value
            line = self._previous().line
            return Variable(name, line)
        
        if self._match(TokenType.LPAREN):
            expr = self._parse_expression()
            self._consume(TokenType.RPAREN, "Se esperaba ')' despues de la expresion")
            return expr
        
        current_token = self._peek()
        raise ParseError(f"Expresion inesperada: '{current_token.value}'", 
                        current_token.line, current_token.column)


def main():
    """Funcion de prueba del parser con sintaxis Alchemist completa"""
    parser = AlchemistParser()
    
    # Codigo de prueba con sintaxis Alchemist correcta
    test_code = '''
    Transmutation GateOfTruth() -> void {
        Solid edad = 25
        Inscription nombre = "Edward Elric"
        Principle isAlchemist = Accepted
        Liquid altura = 1.65
        
        Transmute("=== CIRCULO DE TRANSMUTACION ===")
        Transmute("Nombre: " + nombre)
        Transmute("Edad: " + edad)
        
        Observe (edad >= 18) {
            Transmute("Es mayor de edad")
            Solid poder = calcularPoder(edad)
            Transmute("Poder alquímico: " + poder)
        } Alternatively (edad >= 15) {
            Transmute("Acceso limitado")
        } Inevitably {
            Transmute("Menor de edad")
        }
        
        AlchemicCycle (Solid i = 1; i <= 3; i = i + 1) {
            Transmute("Círculo " + i + " activado")
        }
        
        Solid resultado = calcularPoder(edad)
        EquivalentExchange resultado
    }
    
    Transmutation calcularPoder(Solid years) -> Solid {
        EquivalentExchange years * 25 + 100
    }
    
    Transmutation procesarDatos() -> void {
        Inscription nombre = Absorb("Ingresa tu nombre: ")
        Solid edad = AbsorbSolid("Ingresa tu edad: ")
        
        TransmuteUntil (edad < 18) {
            Transmute("Demasiado joven")
            edad = AbsorbSolid("Ingresa una edad válida: ")
        }
        
        Transmute("Bienvenido " + nombre)
    }
    '''
    
    try:
        ast = parser.parse(test_code)
        print("ANALISIS SINTACTICO ALCHEMIST COMPLETADO")
        print("=" * 60)
        print(f"Programa con {len(ast.functions)} funciones:")
        print()
        
        for i, func in enumerate(ast.functions, 1):
            params = ", ".join(f'{p.type} {p.name}' for p in func.parameters)
            print(f"Función {i}: {func.name}({params}) -> {func.return_type}")
            print(f"   Línea: {func.line}")
            print(f"   Statements: {len(func.body)}")
            
            # Mostrar tipos de statements
            statement_types = {}
            for stmt in func.body:
                stmt_type = type(stmt).__name__
                statement_types[stmt_type] = statement_types.get(stmt_type, 0) + 1
            
            print("   Tipos de declaraciones:")
            for stmt_type, count in statement_types.items():
                print(f"      • {stmt_type}: {count}")
            print()
        
        print("AST GENERADO CORRECTAMENTE CON SINTAXIS ALCHEMIST!")
        
        # Mostrar estructura del AST
        print("\nESTRUCTURA DETALLADA DEL AST:")
        print("=" * 60)
        _print_ast_structure(ast, 0)
        
    except ParseError as e:
        print(f"Error: {e}")


def _print_ast_structure(node, indent=0):
    """Función auxiliar para imprimir la estructura del AST"""
    prefix = "  " * indent
    
    if isinstance(node, Program):
        print(f"{prefix}Program")
        for func in node.functions:
            _print_ast_structure(func, indent + 1)
    
    elif isinstance(node, Function):
        params = ", ".join(f'{p.type} {p.name}' for p in node.parameters)
        print(f"{prefix}Function: {node.name}({params}) -> {node.return_type}")
        for stmt in node.body:
            _print_ast_structure(stmt, indent + 1)
    
    elif isinstance(node, VariableDeclaration):
        print(f"{prefix}VariableDeclaration: {node.type} {node.name}")
        if node.value:
            _print_ast_structure(node.value, indent + 1)
    
    elif isinstance(node, ObserveStatement):
        print(f"{prefix}ObserveStatement")
        print(f"{prefix}  condition:")
        _print_ast_structure(node.condition, indent + 2)
        print(f"{prefix}  then_body:")
        for stmt in node.then_body:
            _print_ast_structure(stmt, indent + 2)
        
        if node.alternatively_parts:
            for i, alt in enumerate(node.alternatively_parts):
                print(f"{prefix}  alternatively_{i}:")
                _print_ast_structure(alt.condition, indent + 2)
                for stmt in alt.body:
                    _print_ast_structure(stmt, indent + 2)
        
        if node.inevitably_body:
            print(f"{prefix}  inevitably:")
            for stmt in node.inevitably_body:
                _print_ast_structure(stmt, indent + 2)
    
    elif isinstance(node, ForStatement):
        print(f"{prefix}AlchemicCycle")
        if node.init:
            print(f"{prefix}  init:")
            _print_ast_structure(node.init, indent + 2)
        if node.condition:
            print(f"{prefix}  condition:")
            _print_ast_structure(node.condition, indent + 2)
        if node.update:
            print(f"{prefix}  update:")
            _print_ast_structure(node.update, indent + 2)
        print(f"{prefix}  body:")
        for stmt in node.body:
            _print_ast_structure(stmt, indent + 2)
    
    elif isinstance(node, WhileStatement):
        print(f"{prefix}TransmuteUntil")
        print(f"{prefix}  condition:")
        _print_ast_structure(node.condition, indent + 2)
        print(f"{prefix}  body:")
        for stmt in node.body:
            _print_ast_structure(stmt, indent + 2)
    
    elif isinstance(node, ReturnStatement):
        print(f"{prefix}EquivalentExchange")
        if node.value:
            _print_ast_structure(node.value, indent + 1)
    
    elif isinstance(node, ExpressionStatement):
        print(f"{prefix}ExpressionStatement")
        _print_ast_structure(node.expression, indent + 1)
    
    elif isinstance(node, FunctionCall):
        print(f"{prefix}FunctionCall: {node.name}(...)")
        for arg in node.arguments:
            _print_ast_structure(arg, indent + 1)
    
    elif isinstance(node, BinaryOperation):
        print(f"{prefix}BinaryOperation: {node.operator}")
        _print_ast_structure(node.left, indent + 1)
        _print_ast_structure(node.right, indent + 1)
    
    elif isinstance(node, Variable):
        print(f"{prefix}Variable: {node.name}")
    
    elif isinstance(node, Literal):
        print(f"{prefix}Literal: {node.value} ({node.type})")
    
    else:
        print(f"{prefix}{type(node).__name__}")


if __name__ == "__main__":
    main()
