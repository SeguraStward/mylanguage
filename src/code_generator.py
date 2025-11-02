#!/usr/bin/env python3
"""
Alchemist Code Generator - Generador de Código
Genera código intermedio y ejecutable a partir del AST validado semánticamente
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import json

from .parser import (
    ASTNode, Program, Function, Parameter, Statement, Expression,
    VariableDeclaration, Assignment, ObserveStatement, WhileStatement, 
    ForStatement, ReturnStatement, BreakStatement, ContinueStatement,
    ExpressionStatement, BinaryOperation, UnaryOperation, FunctionCall,
    Variable, Literal, AlternativelyPart, ArrayDeclaration, ArrayAssignment, ArrayAccess,
    MatrixDeclaration, MatrixAssignment, MatrixAccess
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


class AlchemistCodeGenerator:
    """Generador de código para Alchemist"""
    
    def __init__(self):
        """Inicializa el generador de código"""
        self.instructions: List[Instruction] = []
        self.variables: Dict[str, int] = {}  # nombre -> dirección
        self.functions: Dict[str, int] = {}  # nombre -> dirección
        self.arrays: Dict[str, Dict[str, Any]] = {}  # nombre -> {base_addr, size, element_type}
        self.matrices: Dict[str, Dict[str, Any]] = {}  # nombre -> {base_addr, rows, cols, element_type}
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
        
        # Agregar llamada a GateOfTruth (función principal) al inicio
        main_call = [
            Instruction("CALL", "GateOfTruth", 0),  # Llamar GateOfTruth con 0 argumentos
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
        elif isinstance(stmt, ArrayDeclaration):
            self._generate_array_declaration(stmt)
        elif isinstance(stmt, ArrayAssignment):
            self._generate_array_assignment(stmt)
        elif isinstance(stmt, MatrixDeclaration):
            self._generate_matrix_declaration(stmt)
        elif isinstance(stmt, MatrixAssignment):
            self._generate_matrix_assignment(stmt)
        elif isinstance(stmt, ObserveStatement):
            self._generate_observe_statement(stmt)
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
    
    def _generate_array_declaration(self, stmt: ArrayDeclaration) -> None:
        """Genera código para declaración de array"""
        # Asignar dirección base para el array
        base_addr = self._allocate_variable(stmt.name)
        
        # Guardar metadatos del array
        self.arrays[stmt.name] = {
            'base_addr': base_addr,
            'size': stmt.size,
            'element_type': stmt.element_type
        }
        
        # Reservar espacio para todos los elementos del array
        # Cada elemento del array necesita su propia dirección de memoria
        for i in range(1, stmt.size):
            self._allocate_variable(f"{stmt.name}_elem_{i}")
        
        # Inicializar todos los elementos con valor por defecto
        default_value = self._get_default_value(stmt.element_type)
        for i in range(stmt.size):
            self.instructions.append(Instruction("LOAD_CONST", default_value))
            self.instructions.append(Instruction("STORE", base_addr + i))
    
    def _generate_array_assignment(self, stmt: ArrayAssignment) -> None:
        """Genera código para asignación a elemento de array"""
        if stmt.name not in self.arrays:
            raise Exception(f"Array '{stmt.name}' no declarado")
        
        array_info = self.arrays[stmt.name]
        base_addr = array_info['base_addr']
        array_size = array_info['size']
        
        # Evaluar el índice
        self._generate_expression(stmt.index)
        
        # Evaluar el valor a asignar
        self._generate_expression(stmt.value)
        
        # Almacenar en array[index]
        # El intérprete necesita: índice en stack, valor en stack, dirección base, tamaño
        self.instructions.append(Instruction("STORE_ARRAY", base_addr, array_size, stmt.name))
    
    def _generate_array_access(self, expr: ArrayAccess) -> None:
        """Genera código para acceso a elemento de array"""
        if expr.name not in self.arrays:
            raise Exception(f"Array '{expr.name}' no declarado")
        
        array_info = self.arrays[expr.name]
        base_addr = array_info['base_addr']
        array_size = array_info['size']
        
        # Evaluar el índice
        self._generate_expression(expr.index)
        
        # Cargar valor desde array[index]
        # El intérprete necesita: índice en stack, dirección base, tamaño
        self.instructions.append(Instruction("LOAD_ARRAY", base_addr, array_size, expr.name))
    
    def _generate_matrix_declaration(self, stmt: MatrixDeclaration) -> None:
        """Genera código para declaración de matriz"""
        # Asignar dirección base para la matriz
        base_addr = self._allocate_variable(stmt.name)
        
        # Guardar metadatos de la matriz
        self.matrices[stmt.name] = {
            'base_addr': base_addr,
            'rows': stmt.rows,
            'cols': stmt.cols,
            'element_type': stmt.element_type
        }
        
        # Calcular tamaño total de la matriz
        total_size = stmt.rows * stmt.cols
        
        # Reservar espacio para todos los elementos de la matriz
        for i in range(1, total_size):
            self._allocate_variable(f"{stmt.name}_elem_{i}")
        
        # Inicializar todos los elementos con valor por defecto
        default_value = self._get_default_value(stmt.element_type)
        for i in range(total_size):
            self.instructions.append(Instruction("LOAD_CONST", default_value))
            self.instructions.append(Instruction("STORE", base_addr + i))
    
    def _generate_matrix_assignment(self, stmt: MatrixAssignment) -> None:
        """Genera código para asignación a elemento de matriz"""
        if stmt.name not in self.matrices:
            raise Exception(f"Matriz '{stmt.name}' no declarada")
        
        matrix_info = self.matrices[stmt.name]
        base_addr = matrix_info['base_addr']
        matrix_rows = matrix_info['rows']
        matrix_cols = matrix_info['cols']
        
        # Evaluar el índice de fila
        self._generate_expression(stmt.row_index)
        
        # Evaluar el índice de columna
        self._generate_expression(stmt.col_index)
        
        # Evaluar el valor a asignar
        self._generate_expression(stmt.value)
        
        # Almacenar en matriz[fila][col]
        # El intérprete necesita: índice_fila, índice_col, valor en stack
        # arg1=base_addr, arg2=(rows, cols), arg3=name
        self.instructions.append(Instruction("STORE_MATRIX", base_addr, (matrix_rows, matrix_cols), stmt.name))
    
    def _generate_matrix_access(self, expr: MatrixAccess) -> None:
        """Genera código para acceso a elemento de matriz"""
        if expr.name not in self.matrices:
            raise Exception(f"Matriz '{expr.name}' no declarada")
        
        matrix_info = self.matrices[expr.name]
        base_addr = matrix_info['base_addr']
        matrix_rows = matrix_info['rows']
        matrix_cols = matrix_info['cols']
        
        # Evaluar el índice de fila
        self._generate_expression(expr.row_index)
        
        # Evaluar el índice de columna
        self._generate_expression(expr.col_index)
        
        # Cargar valor desde matriz[fila][col]
        # El intérprete necesita: índice_fila, índice_col en stack
        # arg1=base_addr, arg2=(rows, cols), arg3=name
        self.instructions.append(Instruction("LOAD_MATRIX", base_addr, (matrix_rows, matrix_cols), expr.name))
    
    def _generate_observe_statement(self, stmt: ObserveStatement) -> None:
        """Genera código para declaración observe"""
        end_label = self._generate_label()
        else_label = self._generate_label()
        
        # Evaluar condición
        self._generate_expression(stmt.condition)
        
        # Saltar al alternatively/inevitably si la condición es falsa
        self.instructions.append(Instruction("JUMP_IF_FALSE", else_label))
        
        # Generar código del bloque then
        for s in stmt.then_body:
            self._generate_statement(s)
        
        # Saltar al final
        self.instructions.append(Instruction("JUMP", end_label))
        
        # Manejo de alternatively e inevitably
        current_else_label = else_label
        
        for alt_part in stmt.alternatively_parts:
            # Etiqueta del alternatively actual
            self.instructions.append(Instruction("LABEL", current_else_label))
            
            # Evaluar condición del alternatively
            self._generate_expression(alt_part.condition)
            
            # Nueva etiqueta para el siguiente alternatively/inevitably
            next_else_label = self._generate_label()
            self.instructions.append(Instruction("JUMP_IF_FALSE", next_else_label))
            
            # Generar código del bloque alternatively
            for s in alt_part.body:
                self._generate_statement(s)
            
            # Saltar al final
            self.instructions.append(Instruction("JUMP", end_label))
            
            current_else_label = next_else_label
        
        # Bloque inevitably (si existe)
        self.instructions.append(Instruction("LABEL", current_else_label))
        
        if stmt.inevitably_body:
            for s in stmt.inevitably_body:
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
        
        elif isinstance(expr, ArrayAccess):
            self._generate_array_access(expr)
        
        elif isinstance(expr, MatrixAccess):
            self._generate_matrix_access(expr)
    
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
    from .lexer import AlchemistLexer
    from .parser import AlchemistParser
    from .semantic_analyzer import AlchemistSemanticAnalyzer
    
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
        lexer = AlchemistLexer()
        
        # Análisis sintáctico
        parser = AlchemistParser()
        ast = parser.parse(test_code)
        
        # Análisis semántico
        analyzer = AlchemistSemanticAnalyzer()
        errors = analyzer.analyze(ast)
        
        if errors:
            print("❌ Errores semánticos encontrados:")
            for error in errors:
                print(f"  • {error}")
            return
        
        # Generación de código
        generator = AlchemistCodeGenerator()
        instructions = generator.generate(ast)
        
        # Mostrar código generado
        generator.print_code()
        
        # Guardar a archivo
        generator.save_to_file("output.alch")
        print(f"\n💾 Código guardado en 'output.alch'")
        
    except Exception as e:
        print(f"❌ Error durante la generación: {e}")


if __name__ == "__main__":
    main()
