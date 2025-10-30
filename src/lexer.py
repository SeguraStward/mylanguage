#!/usr/bin/env python3
"""
Analizador lexico transforma el codigo en tokens para poder
realizar el analisis sintactico
"""

import re
from enum import Enum
from dataclasses import dataclass
from typing import List, Iterator


class TokenType(Enum):
    """Tipos de tokens"""
    # literales
    INTEGER = "INTEGER"
    FLOAT = "FLOAT"
    STRING = "STRING"
    BOOLEAN = "BOOLEAN"
    
    # identificador
    IDENTIFIER = "IDENTIFIER"
    
    # tipos de datos
    SOLID_TYPE = "SOLID_TYPE"
    LIQUID_TYPE = "LIQUID_TYPE"
    INSCRIPTION_TYPE = "INSCRIPTION_TYPE"
    PRINCIPLE_TYPE = "PRINCIPLE_TYPE"
    VOID = "VOID"
    ALCHEMICARRAY = "ALCHEMICARRAY"  # Para arrays
    
    #  control de flujo (nueva sintaxis alquimica)
    OBSERVE = "OBSERVE"
    ALTERNATIVELY = "ALTERNATIVELY"
    INEVITABLY = "INEVITABLY"
    TRANSMUTEUNTIL = "TRANSMUTEUNTIL"
    ALCHEMICCYCLE = "ALCHEMICCYCLE"
    BREAK = "BREAK"
    CONTINUE = "CONTINUE"
    RETURN = "RETURN"
    TRANSMUTATION = "TRANSMUTATION"  # palabra clave para definir funciones (reemplaza "func")
    EQUIVALENTEXCHANGE = "EQUIVALENTEXCHANGE"  # palabra clave para retornar valores (reemplaza "return")
    
    # palabras in/out
    ABSORB = "ABSORB"
    ABSORBSOLID = "ABSORBSOLID"
    TRANSMUTE = "TRANSMUTE"
    
    # valores alquimicos
    SOLID = "SOLID"
    LIQUID = "LIQUID"
    INSCRIPTION = "INSCRIPTION"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"
    
    # Operadores
    PLUS = "PLUS"
    MINUS = "MINUS"
    MULTIPLY = "MULTIPLY"
    DIVIDE = "DIVIDE"
    MODULO = "MODULO"
    
    # comparadores
    EQUAL = "EQUAL"
    NOT_EQUAL = "NOT_EQUAL"
    LESS_THAN = "LESS_THAN"
    GREATER_THAN = "GREATER_THAN"
    LESS_EQUAL = "LESS_EQUAL"
    GREATER_EQUAL = "GREATER_EQUAL"
    
    # logicos
    AND = "AND"
    OR = "OR"
    NOT = "NOT"
    
    # asignacion
    ASSIGN = "ASSIGN"
    
    # delimitadores
    LPAREN = "LPAREN"
    RPAREN = "RPAREN"
    LBRACE = "LBRACE"
    RBRACE = "RBRACE"
    LBRACKET = "LBRACKET"
    RBRACKET = "RBRACKET"
    SEMICOLON = "SEMICOLON"
    COMMA = "COMMA"
    DOT = "DOT"
    ARROW = "ARROW"
    
    # especiales
    NEWLINE = "NEWLINE"
    EOF = "EOF"
    COMMENT = "COMMENT"
    WHITESPACE = "WHITESPACE"


@dataclass
class Token:
    """Representa un token del lenguaje"""
    # info del token ( tipo, valor, linea, columna)
    type: TokenType
    value: str
    line: int
    column: int
    
    def __str__(self):
        return f"Token({self.type.value}, '{self.value}', {self.line}:{self.column})"


class LexerError(Exception):
    """Excepcion para errores del analizador lexico"""
    def __init__(self, message: str, line: int, column: int):
        self.message = message
        self.line = line
        self.column = column
        super().__init__(f"Error lexico en linea {line}, columna {column}: {message}")


class AlchemistLexer:
    """Analizador lexico para Alchemist"""
    
    def __init__(self):
        """Inicializa el lexer con las palabras reservadas y patrones"""
        
        # palabras reservadas del lenguaje (nueva sintaxis alquimica)
        self.keywords = {
            # tipos de datos alquimicos
            'Solid': TokenType.SOLID_TYPE,
            'Liquid': TokenType.LIQUID_TYPE,
            'Inscription': TokenType.INSCRIPTION_TYPE,
            'Principle': TokenType.PRINCIPLE_TYPE,
            'void': TokenType.VOID,
            'AlchemicArray': TokenType.ALCHEMICARRAY,  # Para declarar arrays
            
            # control de flujo alquimico
            'Observe': TokenType.OBSERVE,
            'Alternatively': TokenType.ALTERNATIVELY,
            'Inevitably': TokenType.INEVITABLY,
            'TransmuteUntil': TokenType.TRANSMUTEUNTIL,
            'AlchemicCycle': TokenType.ALCHEMICCYCLE,
            'break': TokenType.BREAK,
            'continue': TokenType.CONTINUE,
            'Transmutation': TokenType.TRANSMUTATION,  # para definir funciones
            'EquivalentExchange': TokenType.EQUIVALENTEXCHANGE,  # para retornar valores
            
            # operadores logicos
            'and': TokenType.AND,
            'or': TokenType.OR,
            'not': TokenType.NOT,
            
            # valores de principio alquimico
            'Accepted': TokenType.ACCEPTED,
            'Rejected': TokenType.REJECTED,
            
            # funciones I/O alquimicas
            'Absorb': TokenType.ABSORB,
            'AbsorbSolid': TokenType.ABSORBSOLID,
            'Transmute': TokenType.TRANSMUTE,
        }
        
        # patrones de expresiones regulares
        self.patterns = [
            # Comentarios
            (r'//.*', TokenType.COMMENT),
            (r'/\*.*?\*/', TokenType.COMMENT),
            
            # Numeros
            (r'\d+\.\d+', TokenType.FLOAT),
            (r'\d+', TokenType.INTEGER),
            
            # Cadenas
            (r'"([^"\\]|\\.)*"', TokenType.STRING),
            (r"'([^'\\]|\\.)*'", TokenType.STRING),
            
            # Operadores de dos caracteres
            (r'->', TokenType.ARROW),
            (r'==', TokenType.EQUAL),
            (r'!=', TokenType.NOT_EQUAL),
            (r'<=', TokenType.LESS_EQUAL),
            (r'>=', TokenType.GREATER_EQUAL),
            
            # Operadores de un caracter
            (r'\+', TokenType.PLUS),
            (r'-', TokenType.MINUS),
            (r'\*', TokenType.MULTIPLY),
            (r'/', TokenType.DIVIDE),
            (r'%', TokenType.MODULO),
            (r'=', TokenType.ASSIGN),
            (r'<', TokenType.LESS_THAN),
            (r'>', TokenType.GREATER_THAN),
            
            # Delimitadores
            (r'\(', TokenType.LPAREN),
            (r'\)', TokenType.RPAREN),
            (r'\{', TokenType.LBRACE),
            (r'\}', TokenType.RBRACE),
            (r'\[', TokenType.LBRACKET),
            (r'\]', TokenType.RBRACKET),
            (r';', TokenType.SEMICOLON),
            (r',', TokenType.COMMA),
            (r'\.', TokenType.DOT),
            
            # Identificadores (deben ir despues de las palabras reservadas)
            (r'[a-zA-Z_][a-zA-Z0-9_]*', TokenType.IDENTIFIER),
            
            # Espacios en blanco y saltos de linea
            (r'\n', TokenType.NEWLINE),
            (r'[ \t]+', TokenType.WHITESPACE),
        ]
        
        # Compilar patrones
        self.compiled_patterns = [(re.compile(pattern), token_type) 
                                 for pattern, token_type in self.patterns]
    
    def tokenize(self, source_code: str) -> List[Token]:
        """
        Convierte el codigo fuente en una lista de tokens
        
        Args:
            source_code: Codigo fuente a analizar
            
        Returns:
            Lista de tokens encontrados
            
        Raises:
            LexerError: Si encuentra un caracter no reconocido
        """
        tokens = []
        lines = source_code.split('\n')


        for line_number, lineContent in enumerate(lines, 1):
            self._tokenize_line(lineContent, line_number, tokens)

         
        tokens.append(Token(TokenType.EOF, '', len(lines), len(lines[-1]) if lines else 0))
        
        return tokens
    
    def _tokenize_line(self, line: str, line_num: int, tokens: List[Token]) -> None:
        """
        Tokeniza una linea especifica del codigo
        
        Args:
            line: Linea de codigo a tokenizar
            line_num: Número de linea actual
            tokens: Lista donde agregar los tokens encontrados
        """
        pos = 0
        
        while pos < len(line):
            match_found = False
            
            # Intentar hacer match con cada patron
            for pattern, token_type in self.compiled_patterns:
                match = pattern.match(line, pos)
                if match:
                    value = match.group(0)
                    
                    # Ignorar espacios en blanco y comentarios en la salida final
                    if token_type not in [TokenType.WHITESPACE, TokenType.COMMENT]:
                        # Verificar si es una palabra reservada
                        if token_type == TokenType.IDENTIFIER and value in self.keywords:
                            token_type = self.keywords[value]
                        
                        token = Token(token_type, value, line_num, pos + 1)
                        tokens.append(token)
                    
                    pos = match.end()
                    match_found = True
                    break
            
            if not match_found:
                # Caracter no reconocido
                raise LexerError(f"Caracter no reconocido: '{line[pos]}'",
                               line_num, pos + 1)
    
    def get_token_iterator(self, source_code: str) -> Iterator[Token]:
        """
        Retorna un iterador de tokens para analisis streaming
        
        Args:
            source_code: Codigo fuente a analizar
            
        Yields:
            Token: Siguiente token en el codigo
        """
        tokens = self.tokenize(source_code)
        for token in tokens:
            yield token


def main():
    """Funcion de prueba"""
    lexer = AlchemistLexer()
    
    test_code = '''
    func main() -> void {
        int edad = 25
        string nombre = "Juan"
        
        if (edad >= 18) {
            print("Eres mayor de edad")
        } else {
            print("Eres menor de edad")
        }
    }
    
    func calcular(int a, int b) -> int {
        return a + b
    }
    '''
    
    try:
        tokens = lexer.tokenize(test_code)
        
        print("ANALISIS LEXICO COMPLETADO")
        print("=" * 50)
        
        for token in tokens:
            if token.type != TokenType.NEWLINE: 
                print(f"{token.line:2d}:{token.column:2d} | {token.type.value:15} | '{token.value}'")
                
        print(f"\nTotal de tokens: {len([t for t in tokens if t.type != TokenType.NEWLINE])}")
        
    except LexerError as e:
        print(f" {e}")


if __name__ == "__main__":
    main()
