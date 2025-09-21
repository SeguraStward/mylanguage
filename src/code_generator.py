#!/usr/bin/env python3
"""
aurum Code Generator - Generador de Código
Genera código intermedio y ejecutable a partir del AST validado semánticamente
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import json

from .parser import (
    ASTNode, Program, Function, Parameter, Statement, Expression,
    VariableDeclaration, Assignment, IfStatement, WhileStatement, 
    ForStatement, ReturnStatement, BreakStatement, ContinueStatement,
    ExpressionStatement, BinaryOperation, UnaryOperation, FunctionCall,
    Variable, Literal, ElifPart
)


@dataclass
class Instruction:
    """Representa una instrucción del código intermedio"""
    op: str  # Operación (LOAD, STORE, ADD, etc.)
    arg1: Any = None
    arg2: Any = None
    arg3: Any = None
    
    def __str__(self):
        args = [str(arg) for arg in [self.arg1, self.arg2, self.arg3] if arg is not None]
        return f"{self.op} {' '.join(args)}" if args else self.op


class CodeGeneratorError(Exception):
    """Excepción para errores en la generación de código"""
    def __init__(self, message: str, line: int = 0):
        self.message = message
        self.line = line
        super().__init__(f"Error en generación de código línea {line}: {message}")


class aurumCodeGenerator:
    """Generador de código para aurum"""
    
    def __init__(self):
        """Inicializa el generador de código"""
        self.instructions: List[Instruction] = []
        self.variables: Dict[str, int] = {}  # nombre -> dirección
        self.functions: Dict[str, int] = {}  # nombre -> dirección
        self.memory_counter = 0
        self.label_counter = 0
        self.current_function: Optional[str] = None
        
        # Pila para manejo de saltos
        self.break_labels: List[str] = []
        self.continue_labels: List[str] = []
    
    def generate(self, ast: Program) -> List[Instruction]:
        """
        Genera código intermedio a partir del AST
        
        Args:
            ast: AST del programa validado semánticamente
            
        Returns:
            Lista de instrucciones del código intermedio
        """
        self.instructions = []
        self.variables = {}
        self.functions = {}
        self.memory_counter = 0
        
        # Generar código para todas las funciones
        for function in ast.functions:
            self._generate_function(function)
        
        # Agregar llamada a main al inicio
        main_call = [
            Instruction("CALL", "main", 0),  # Llamar main con 0 argumentos
            Instruction("HALT")  # Terminar programa
        ]
        
        # Insertar al inicio
        self.instructions = main_call + self.instructions
        
        return self.instructions
    
    def _generate_label(self) -> str:
        """Genera una etiqueta única"""
        label = f"L{self.label_counter}"
        self.label_counter += 1
        return label
    
    def _allocate_variable(self, name: str) -> int:
        """Asigna una dirección de memoria a una variable"""
        if name not in self.variables:
            self.variables[name] = self.memory_counter
            self.memory_counter += 1
        return self.variables[name]
    
    def _generate_function(self, function: Function) -> None:
        """Genera código para una función"""
        # Marcar inicio de función
        self.functions[function.name] = len(self.instructions)
        self.current_function = function.name
        
        # Etiqueta de la función
        self.instructions.append(Instruction("LABEL", function.name))
        
        # Crear frame de función
        self.instructions.append(Instruction("ENTER", len(function.parameters)))
        
        # Asignar parámetros a variables locales
        for i, param in enumerate(function.parameters):
            param_addr = self._allocate_variable(param.name)
            self.instructions.append(Instruction("STORE_PARAM", i, param_addr))
        
        # Generar código del cuerpo
        for stmt in function.body:
            self._generate_statement(stmt)
        
        # Si no hay return explícito y es void, agregar return
        if function.return_type == "void":
            self.instructions.append(Instruction("RETURN"))
        
        # Salir del frame de función
        self.instructions.append(Instruction("LEAVE"))
    
    def _generate_statement(self, stmt: Statement) -> None:
        """Genera código para una declaración"""
        if isinstance(stmt, VariableDeclaration):
            self._generate_variable_declaration(stmt)
        elif isinstance(stmt, Assignment):
            self._generate_assignment(stmt)
        elif isinstance(stmt, IfStatement):
            self._generate_if_statement(stmt)
        elif isinstance(stmt, WhileStatement):
            self._generate_while_statement(stmt)
        elif isinstance(stmt, ForStatement):
            self._generate_for_statement(stmt)
        elif isinstance(stmt, ReturnStatement):
            self._generate_return_statement(stmt)
        elif isinstance(stmt, BreakStatement):
            self._generate_break_statement(stmt)
        elif isinstance(stmt, ContinueStatement):
            self._generate_continue_statement(stmt)
        elif isinstance(stmt, ExpressionStatement):
            self._generate_expression(stmt.expression)
            # Descartar resultado si es una expresión como declaración
            self.instructions.append(Instruction("POP"))
    
    def _generate_variable_declaration(self, stmt: VariableDeclaration) -> None:
        """Genera código para declaración de variable"""
        var_addr = self._allocate_variable(stmt.name)
        
        if stmt.value:
            # Evaluar expresión inicial
            self._generate_expression(stmt.value)
            # Almacenar en la variable
            self.instructions.append(Instruction("STORE", var_addr))
        else:
            # Inicializar con valor por defecto
            default_value = self._get_default_value(stmt.type)
            self.instructions.append(Instruction("LOAD_CONST", default_value))
            self.instructions.append(Instruction("STORE", var_addr))
    
    def _generate_assignment(self, stmt: Assignment) -> None:
        """Genera código para asignación"""
        var_addr = self.variables[stmt.name]
        
        # Evaluar expresión del valor
        self._generate_expression(stmt.value)
        
        # Almacenar en la variable
        self.instructions.append(Instruction("STORE", var_addr))
    
    def _generate_if_statement(self, stmt: IfStatement) -> None:
        """Genera código para declaración if"""
        end_label = self._generate_label()
        else_label = self._generate_label()
        
        # Evaluar condición
        self._generate_expression(stmt.condition)
        
        # Saltar al else si la condición es falsa
        self.instructions.append(Instruction("JUMP_IF_FALSE", else_label))
        
        # Generar código del bloque then
        for s in stmt.then_body:
            self._generate_statement(s)
        
        # Saltar al final
        self.instructions.append(Instruction("JUMP", end_label))
        
        # Manejo de elif y else
        current_else_label = else_label
        
        for elif_part in stmt.elif_parts:
            # Etiqueta del elif actual
            self.instructions.append(Instruction("LABEL", current_else_label))
            
            # Evaluar condición del elif
            self._generate_expression(elif_part.condition)
            
            # Nueva etiqueta para el siguiente elif/else
            next_else_label = self._generate_label()
            self.instructions.append(Instruction("JUMP_IF_FALSE", next_else_label))
            
            # Generar código del bloque elif
            for s in elif_part.body:
                self._generate_statement(s)
            
            # Saltar al final
            self.instructions.append(Instruction("JUMP", end_label))
            
            current_else_label = next_else_label
        
        # Bloque else (si existe)
        self.instructions.append(Instruction("LABEL", current_else_label))
        
        if stmt.else_body:
            for s in stmt.else_body:
                self._generate_statement(s)
        
        # Etiqueta del final
        self.instructions.append(Instruction("LABEL", end_label))
    
    def _generate_while_statement(self, stmt: WhileStatement) -> None:
        """Genera código para ciclo while"""
        start_label = self._generate_label()
        end_label = self._generate_label()
        
        # Guardar etiquetas para break/continue
        self.break_labels.append(end_label)
        self.continue_labels.append(start_label)
        
        # Etiqueta del inicio del ciclo
        self.instructions.append(Instruction("LABEL", start_label))
        
        # Evaluar condición
        self._generate_expression(stmt.condition)
        
        # Saltar al final si la condición es falsa
        self.instructions.append(Instruction("JUMP_IF_FALSE", end_label))
        
        # Generar código del cuerpo
        for s in stmt.body:
            self._generate_statement(s)
        
        # Saltar al inicio
        self.instructions.append(Instruction("JUMP", start_label))
        
        # Etiqueta del final
        self.instructions.append(Instruction("LABEL", end_label))
        
        # Remover etiquetas
        self.break_labels.pop()
        self.continue_labels.pop()
    
    def _generate_for_statement(self, stmt: ForStatement) -> None:
        """Genera código para ciclo for"""
        start_label = self._generate_label()
        update_label = self._generate_label()
        end_label = self._generate_label()
        
        # Guardar etiquetas para break/continue
        self.break_labels.append(end_label)
        self.continue_labels.append(update_label)
        
        # Inicialización
        if stmt.init:
            self._generate_statement(stmt.init)
        
        # Etiqueta del inicio del ciclo
        self.instructions.append(Instruction("LABEL", start_label))
        
        # Evaluar condición
        if stmt.condition:
            self._generate_expression(stmt.condition)
            self.instructions.append(Instruction("JUMP_IF_FALSE", end_label))
        
        # Generar código del cuerpo
        for s in stmt.body:
            self._generate_statement(s)
        
        # Etiqueta para continue (actualización)
        self.instructions.append(Instruction("LABEL", update_label))
        
        # Actualización
        if stmt.update:
            self._generate_statement(stmt.update)
        
        # Saltar al inicio
        self.instructions.append(Instruction("JUMP", start_label))
        
        # Etiqueta del final
        self.instructions.append(Instruction("LABEL", end_label))
        
        # Remover etiquetas
        self.break_labels.pop()
        self.continue_labels.pop()
    
    def _generate_return_statement(self, stmt: ReturnStatement) -> None:
        """Genera código para declaración return"""
        if stmt.value:
            # Evaluar expresión de retorno
            self._generate_expression(stmt.value)
            self.instructions.append(Instruction("RETURN_VALUE"))
        else:
            self.instructions.append(Instruction("RETURN"))
    
    def _generate_break_statement(self, stmt: BreakStatement) -> None:
        """Genera código para declaración break"""
        if self.break_labels:
            self.instructions.append(Instruction("JUMP", self.break_labels[-1]))
        else:
            raise CodeGeneratorError("'break' fuera de ciclo", stmt.line)
    
    def _generate_continue_statement(self, stmt: ContinueStatement) -> None:
        """Genera código para declaración continue"""
        if self.continue_labels:
            self.instructions.append(Instruction("JUMP", self.continue_labels[-1]))
        else:
            raise CodeGeneratorError("'continue' fuera de ciclo", stmt.line)
    
    def _generate_expression(self, expr: Expression) -> None:
        """Genera código para una expresión"""
        if isinstance(expr, Literal):
            self.instructions.append(Instruction("LOAD_CONST", expr.value))
        
        elif isinstance(expr, Variable):
            var_addr = self.variables[expr.name]
            self.instructions.append(Instruction("LOAD", var_addr))
        
        elif isinstance(expr, BinaryOperation):
            self._generate_binary_operation(expr)
        
        elif isinstance(expr, UnaryOperation):
            self._generate_unary_operation(expr)
        
        elif isinstance(expr, FunctionCall):
            self._generate_function_call(expr)
    
    def _generate_binary_operation(self, expr: BinaryOperation) -> None:
        """Genera código para operación binaria"""
        # Generar código para operandos
        self._generate_expression(expr.left)
        self._generate_expression(expr.right)
        
        # Generar instrucción de operación
        op_map = {
            "+": "ADD",
            "-": "SUB",
            "*": "MUL",
            "/": "DIV",
            "%": "MOD",
            "==": "EQ",
            "!=": "NEQ",
            "<": "LT",
            ">": "GT",
            "<=": "LEQ",
            ">=": "GEQ",
            "and": "AND",
            "or": "OR"
        }
        
        if expr.operator in op_map:
            self.instructions.append(Instruction(op_map[expr.operator]))
        else:
            raise CodeGeneratorError(f"Operador no soportado: {expr.operator}")
    
    def _generate_unary_operation(self, expr: UnaryOperation) -> None:
        """Genera código para operación unaria"""
        # Generar código para operando
        self._generate_expression(expr.operand)
        
        # Generar instrucción de operación
        if expr.operator == "-":
            self.instructions.append(Instruction("NEG"))
        elif expr.operator == "not":
            self.instructions.append(Instruction("NOT"))
        else:
            raise CodeGeneratorError(f"Operador unario no soportado: {expr.operator}")
    
    def _generate_function_call(self, expr: FunctionCall) -> None:
        """Genera código para llamada a función"""
        # Generar código para argumentos (en orden inverso)
        for arg in reversed(expr.arguments):
            self._generate_expression(arg)
        
        # Llamada a función
        self.instructions.append(Instruction("CALL", expr.name, len(expr.arguments)))
    
    def _get_default_value(self, type_name: str) -> Any:
        """Obtiene el valor por defecto para un tipo"""
        defaults = {
            "int": 0,
            "float": 0.0,
            "string": "",
            "bool": False
        }
        return defaults.get(type_name, None)
    
    def save_to_file(self, filename: str) -> None:
        """
        Guarda el código intermedio a un archivo
        
        Args:
            filename: Nombre del archivo donde guardar
        """
        code_data = {
            "instructions": [
                {
                    "op": inst.op,
                    "args": [inst.arg1, inst.arg2, inst.arg3]
                }
                for inst in self.instructions
            ],
            "variables": self.variables,
            "functions": self.functions
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(code_data, f, indent=2, ensure_ascii=False)
    
    def print_code(self) -> None:
        """Imprime el código intermedio generado"""
        print("🔧 CÓDIGO INTERMEDIO GENERADO")
        print("=" * 50)
        
        for i, instruction in enumerate(self.instructions):
            print(f"{i:4d}: {instruction}")
        
        print(f"\n📊 Total de instrucciones: {len(self.instructions)}")
        print(f"📊 Variables utilizadas: {len(self.variables)}")
        print(f"📊 Funciones definidas: {len(self.functions)}")


def main():
    """Función de prueba del generador de código"""
    from .lexer import AurumLexer
    from .parser import AurumParser
    from .semantic_analyzer import aurumSemanticAnalyzer
    
    # Código de prueba
    test_code = '''
    func main() -> void {
        int a = 10
        int b = 20
        int suma = a + b
        
        if (suma > 25) {
            print("La suma es mayor a 25")
        } else {
            print("La suma es menor o igual a 25")
        }
        
        int resultado = factorial(5)
        print("El factorial es: " + resultado)
    }
    
    func factorial(int n) -> int {
        if (n <= 1) {
            return 1
        } else {
            return n * factorial(n - 1)
        }
    }
    '''
    
    try:
        # Análisis léxico
        lexer = AurumLexer()
        
        # Análisis sintáctico
        parser = AurumParser()
        ast = parser.parse(test_code)
        
        # Análisis semántico
        analyzer = aurumSemanticAnalyzer()
        errors = analyzer.analyze(ast)
        
        if errors:
            print("❌ Errores semánticos encontrados:")
            for error in errors:
                print(f"  • {error}")
            return
        
        # Generación de código
        generator = aurumCodeGenerator()
        instructions = generator.generate(ast)
        
        # Mostrar código generado
        generator.print_code()
        
        # Guardar a archivo
        generator.save_to_file("output.auro")
        print(f"\n💾 Código guardado en 'output.auro'")
        
    except Exception as e:
        print(f"❌ Error durante la generación: {e}")


if __name__ == "__main__":
    main()
