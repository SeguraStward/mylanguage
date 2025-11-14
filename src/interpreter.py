#!/usr/bin/env python3
"""
Alchemist Interpreter - Intérprete y Máquina Virtual
Ejecuta el código intermedio generado por el compilador
"""

from typing import Dict, List, Any, Optional, Union
import json
from dataclasses import dataclass

from .code_generator import Instruction


@dataclass
class StackFrame:
    """Representa un frame en la pila de llamadas"""
    function_name: str
    return_address: int
    local_vars: Dict[str, Any]
    parameters: List[Any]
    local_memory: List[Any] = None  # Memoria local del frame
    
    def __post_init__(self):
        """Inicializa la memoria local si no se proporciona"""
        if self.local_memory is None:
            self.local_memory = [None] * 1000


class RuntimeError(Exception):
    """Excepción para errores de tiempo de ejecución"""
    def __init__(self, message: str, instruction_pointer: int = -1):
        self.message = message
        self.instruction_pointer = instruction_pointer
        super().__init__(f"Error de ejecución en instrucción {instruction_pointer}: {message}")


class AlchemistInterpreter:
    """Intérprete para Alchemist"""
    
    def __init__(self, max_recursion_depth: int = 1000):
        """Inicializa el intérprete"""
        self.instructions: List[Instruction] = []
        self.memory: List[Any] = [None] * 1000  # Memoria simulada
        self.stack: List[Any] = []  # Pila de operandos
        self.call_stack: List[StackFrame] = []  # Pila de llamadas
        self.instruction_pointer = 0
        self.labels: Dict[str, int] = {}  # Etiquetas -> dirección
        self.variables: Dict[str, int] = {}  # Mapeo variable -> dirección
        self.functions: Dict[str, int] = {}  # Mapeo función -> dirección
        self.output: str = ""  # Salida del programa como string
        self.input_buffer: List[str] = []  # Buffer de entrada
        self.halted = False
        self.max_recursion_depth = max_recursion_depth  # Límite de recursión
    
    def format_value_for_output(self, value):
        """
        Convierte valores de Python a representación del lenguaje Alchemist
        
        Args:
            value: Valor a formatear
            
        Returns:
            str: Representación en formato Alchemist
        """
        if value is None:
            return "Emptiness"
        elif isinstance(value, bool):
            return "Accepted" if value else "Rejected"
        else:
            return str(value)
    
    def _get_active_memory(self) -> List[Any]:
        """
        Retorna la memoria activa (local del frame o global)
        
        Returns:
            La memoria local del frame activo si existe, sino la memoria global
        """
        if self.call_stack:
            return self.call_stack[-1].local_memory
        return self.memory
    
    def load_program(self, instructions: List[Instruction], 
                    variables: Dict[str, int] = None, 
                    functions: Dict[str, int] = None) -> None:
        """
        Carga un programa en el intérprete
        
        Args:
            instructions: Lista de instrucciones a ejecutar
            variables: Mapeo de variables a direcciones de memoria
            functions: Mapeo de funciones a direcciones de instrucciones
        """
        self.instructions = instructions
        self.variables = variables or {}
        self.functions = functions or {}
        
        # Construir tabla de etiquetas
        self._build_label_table()
        
        # Reiniciar estado
        self.memory = [None] * 1000
        self.stack = []
        self.call_stack = []
        self.instruction_pointer = 0
        self.output = []
        self.halted = False
    
    def load_from_file(self, filename: str) -> None:
        """
        Carga un programa desde un archivo JSON
        
        Args:
            filename: Nombre del archivo a cargar
        """
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Convertir instrucciones
        instructions = []
        for inst_data in data['instructions']:
            args = [arg for arg in inst_data['args'] if arg is not None]
            if len(args) == 0:
                instruction = Instruction(inst_data['op'])
            elif len(args) == 1:
                instruction = Instruction(inst_data['op'], args[0])
            elif len(args) == 2:
                instruction = Instruction(inst_data['op'], args[0], args[1])
            else:
                instruction = Instruction(inst_data['op'], args[0], args[1], args[2])
            instructions.append(instruction)
        
        self.load_program(instructions, data['variables'], data['functions'])
    
    def _build_label_table(self) -> None:
        """Construye la tabla de etiquetas"""
        self.labels = {}
        for i, instruction in enumerate(self.instructions):
            if instruction.op == "LABEL":
                self.labels[instruction.arg1] = i
    
    def set_input(self, input_lines: List[str]) -> None:
        """
        Establece la entrada para el programa
        
        Args:
            input_lines: Lista de líneas de entrada
        """
        self.input_buffer = input_lines.copy()
    
    def execute(self) -> str:
        """
        Ejecuta el programa cargado
        
        Returns:
            String con la salida del programa
            
        Raises:
            RuntimeError: Si ocurre un error durante la ejecución
        """
        self.output = ""
        self.halted = False
        self.instruction_pointer = 0
        
        while not self.halted and self.instruction_pointer < len(self.instructions):
            try:
                self._execute_instruction()
            except Exception as e:
                if isinstance(e, RuntimeError):
                    raise e
                else:
                    raise RuntimeError(f"Error interno: {e}", self.instruction_pointer)
        
        return self.output
    
    def _execute_instruction(self) -> None:
        """Ejecuta una instrucción específica"""
        if self.instruction_pointer >= len(self.instructions):
            self.halted = True
            return
        
        instruction = self.instructions[self.instruction_pointer]
        
        # Ejecutar según el tipo de instrucción
        if instruction.op == "LOAD_CONST":
            self._exec_load_const(instruction)
        elif instruction.op == "LOAD":
            self._exec_load(instruction)
        elif instruction.op == "STORE":
            self._exec_store(instruction)
        elif instruction.op == "STORE_PARAM":
            self._exec_store_param(instruction)
        elif instruction.op == "ADD":
            self._exec_add()
        elif instruction.op == "SUB":
            self._exec_sub()
        elif instruction.op == "MUL":
            self._exec_mul()
        elif instruction.op == "DIV":
            self._exec_div()
        elif instruction.op == "MOD":
            self._exec_mod()
        elif instruction.op == "NEG":
            self._exec_neg()
        elif instruction.op == "EQ":
            self._exec_eq()
        elif instruction.op == "NEQ":
            self._exec_neq()
        elif instruction.op == "LT":
            self._exec_lt()
        elif instruction.op == "GT":
            self._exec_gt()
        elif instruction.op == "LEQ":
            self._exec_leq()
        elif instruction.op == "GEQ":
            self._exec_geq()
        elif instruction.op == "AND":
            self._exec_and()
        elif instruction.op == "OR":
            self._exec_or()
        elif instruction.op == "NOT":
            self._exec_not()
        elif instruction.op == "JUMP":
            self._exec_jump(instruction)
        elif instruction.op == "JUMP_IF_FALSE":
            self._exec_jump_if_false(instruction)
        elif instruction.op == "CALL":
            self._exec_call(instruction)
        elif instruction.op == "RETURN":
            self._exec_return()
        elif instruction.op == "RETURN_VALUE":
            self._exec_return_value()
        elif instruction.op == "ENTER":
            self._exec_enter(instruction)
        elif instruction.op == "LEAVE":
            self._exec_leave()
        elif instruction.op == "HALT":
            self._exec_halt()
        elif instruction.op == "POP":
            self._exec_pop()
        elif instruction.op == "STORE_ARRAY":
            self._exec_store_array(instruction)
        elif instruction.op == "LOAD_ARRAY":
            self._exec_load_array(instruction)
        elif instruction.op == "STORE_MATRIX":
            self._exec_store_matrix(instruction)
        elif instruction.op == "LOAD_MATRIX":
            self._exec_load_matrix(instruction)
        elif instruction.op == "LABEL":
            # Las etiquetas no hacen nada en tiempo de ejecución
            self.instruction_pointer += 1
        else:
            raise RuntimeError(f"Instrucción no reconocida: {instruction.op}")
    
    # ========================================
    # INSTRUCCIONES DE CARGA Y ALMACENAMIENTO
    # ========================================
    
    def _exec_load_const(self, instruction: Instruction) -> None:
        """Carga una constante en la pila"""
        self.stack.append(instruction.arg1)
        self.instruction_pointer += 1
    
    def _exec_load(self, instruction: Instruction) -> None:
        """Carga un valor de memoria en la pila"""
        address = instruction.arg1
        active_memory = self._get_active_memory()
        
        if address >= len(active_memory):
            raise RuntimeError(f"Dirección de memoria inválida: {address}")
        
        value = active_memory[address]
        # Permitir None solo si fue explícitamente asignado (Emptiness)
        # Si nunca fue inicializado, active_memory[address] es None de forma implícita
        # Pero necesitamos distinguir entre "nunca inicializado" y "asignado a Emptiness"
        # Por ahora, permitimos None (será validado en tiempo de compilación)
        
        self.stack.append(value)
        self.instruction_pointer += 1
    
    def _exec_store(self, instruction: Instruction) -> None:
        """Almacena el valor del tope de la pila en memoria"""
        if not self.stack:
            raise RuntimeError("Pila vacía para operación STORE")
        
        value = self.stack.pop()
        address = instruction.arg1
        active_memory = self._get_active_memory()
        
        if address >= len(active_memory):
            raise RuntimeError(f"Dirección de memoria inválida: {address}")
        
        active_memory[address] = value
        self.instruction_pointer += 1
    
    def _exec_store_param(self, instruction: Instruction) -> None:
        """Almacena un parámetro en una variable local"""
        param_index = instruction.arg1
        address = instruction.arg2
        
        if not self.call_stack:
            raise RuntimeError("No hay frame de función activo")
        
        frame = self.call_stack[-1]
        if param_index >= len(frame.parameters):
            raise RuntimeError(f"Índice de parámetro inválido: {param_index}")
        
        value = frame.parameters[param_index]
        frame.local_memory[address] = value  # Usar memoria local del frame
        self.instruction_pointer += 1
    
    def _exec_store_array(self, instruction: Instruction) -> None:
        """Almacena un valor en un elemento del array"""
        # La pila contiene: [índice, valor]
        if len(self.stack) < 2:
            raise RuntimeError("Pila insuficiente para operación STORE_ARRAY")
        
        value = self.stack.pop()  # Valor a almacenar
        index = self.stack.pop()  # Índice del array
        base_addr = instruction.arg1  # Dirección base del array
        array_size = instruction.arg2  # Tamaño del array
        array_name = instruction.arg3  # Nombre del array (para mensajes de error)
        
        # Validar que el índice sea un entero
        if not isinstance(index, int):
            raise RuntimeError(f"El índice del array debe ser un entero, se obtuvo: {type(index).__name__}")
        
        # VALIDACION DE RANGO
        if index < 0:
            raise RuntimeError(f"Índice de array negativo: {index}. Los índices deben ser >= 0")
        
        if index >= array_size:
            raise RuntimeError(f"Índice fuera de rango: {index}. El array '{array_name}' tiene tamaño {array_size} (índices válidos: 0-{array_size - 1})")
        
        # Calcular dirección efectiva
        target_addr = base_addr + index
        
        # Validar dirección
        if target_addr >= len(self.memory):
            raise RuntimeError(f"Dirección de memoria inválida: {target_addr}")
        
        # Almacenar valor
        self.memory[target_addr] = value
        self.instruction_pointer += 1
    
    def _exec_load_array(self, instruction: Instruction) -> None:
        """Carga un valor desde un elemento del array"""
        # La pila contiene: [índice]
        if not self.stack:
            raise RuntimeError("Pila vacía para operación LOAD_ARRAY")
        
        index = self.stack.pop()  # Índice del array
        base_addr = instruction.arg1  # Dirección base del array
        array_size = instruction.arg2  # Tamaño del array
        array_name = instruction.arg3  # Nombre del array (para mensajes de error)
        
        # Validar que el índice sea un entero
        if not isinstance(index, int):
            raise RuntimeError(f"El índice del array debe ser un entero, se obtuvo: {type(index).__name__}")
        
        # VALIDACION DE RANGO
        if index < 0:
            raise RuntimeError(f"Índice de array negativo: {index}. Los índices deben ser >= 0")
        
        if index >= array_size:
            raise RuntimeError(f"Índice fuera de rango: {index}. El array '{array_name}' tiene tamaño {array_size} (índices válidos: 0-{array_size - 1})")
        
        # Calcular dirección efectiva
        target_addr = base_addr + index
        
        # Validar dirección
        if target_addr >= len(self.memory):
            raise RuntimeError(f"Dirección de memoria inválida: {target_addr}")
        
        # Cargar valor
        value = self.memory[target_addr]
        if value is None:
            raise RuntimeError(f"Elemento del array no inicializado en índice {index}")
        
        self.stack.append(value)
        self.instruction_pointer += 1
    
    def _exec_store_matrix(self, instruction: Instruction) -> None:
        """Almacena un valor en un elemento de la matriz"""
        # La pila contiene: [índice_fila, índice_col, valor]
        if len(self.stack) < 3:
            raise RuntimeError("Pila insuficiente para operación STORE_MATRIX")
        
        value = self.stack.pop()  # Valor a almacenar
        col_index = self.stack.pop()  # Índice de columna
        row_index = self.stack.pop()  # Índice de fila
        base_addr = instruction.arg1  # Dirección base de la matriz
        matrix_rows, matrix_cols = instruction.arg2  # (filas, columnas) como tupla
        matrix_name = instruction.arg3  # Nombre de la matriz (para mensajes de error)
        
        # Validar que los índices sean enteros
        if not isinstance(row_index, int):
            raise RuntimeError(f"El índice de fila debe ser un entero, se obtuvo: {type(row_index).__name__}")
        
        if not isinstance(col_index, int):
            raise RuntimeError(f"El índice de columna debe ser un entero, se obtuvo: {type(col_index).__name__}")
        
        # VALIDACION DE RANGO para filas
        if row_index < 0:
            raise RuntimeError(f"Índice de fila negativo: {row_index}. Los índices deben ser >= 0")
        
        if row_index >= matrix_rows:
            raise RuntimeError(f"Índice de fila fuera de rango: {row_index}. La matriz '{matrix_name}' tiene {matrix_rows} filas (índices válidos: 0-{matrix_rows - 1})")
        
        # VALIDACION DE RANGO para columnas
        if col_index < 0:
            raise RuntimeError(f"Índice de columna negativo: {col_index}. Los índices deben ser >= 0")
        
        if col_index >= matrix_cols:
            raise RuntimeError(f"Índice de columna fuera de rango: {col_index}. La matriz '{matrix_name}' tiene {matrix_cols} columnas (índices válidos: 0-{matrix_cols - 1})")
        
        # Calcular dirección efectiva (row-major order: dirección = base + fila * cols + col)
        target_addr = base_addr + (row_index * matrix_cols) + col_index
        
        # Validar dirección
        if target_addr >= len(self.memory):
            raise RuntimeError(f"Dirección de memoria inválida: {target_addr}")
        
        # Almacenar valor
        self.memory[target_addr] = value
        self.instruction_pointer += 1
    
    def _exec_load_matrix(self, instruction: Instruction) -> None:
        """Carga un valor desde un elemento de la matriz"""
        # La pila contiene: [índice_fila, índice_col]
        if len(self.stack) < 2:
            raise RuntimeError("Pila insuficiente para operación LOAD_MATRIX")
        
        col_index = self.stack.pop()  # Índice de columna
        row_index = self.stack.pop()  # Índice de fila
        base_addr = instruction.arg1  # Dirección base de la matriz
        matrix_rows, matrix_cols = instruction.arg2  # (filas, columnas) como tupla
        matrix_name = instruction.arg3  # Nombre de la matriz (para mensajes de error)
        
        # Validar que los índices sean enteros
        if not isinstance(row_index, int):
            raise RuntimeError(f"El índice de fila debe ser un entero, se obtuvo: {type(row_index).__name__}")
        
        if not isinstance(col_index, int):
            raise RuntimeError(f"El índice de columna debe ser un entero, se obtuvo: {type(col_index).__name__}")
        
        # VALIDACION DE RANGO para filas
        if row_index < 0:
            raise RuntimeError(f"Índice de fila negativo: {row_index}. Los índices deben ser >= 0")
        
        if row_index >= matrix_rows:
            raise RuntimeError(f"Índice de fila fuera de rango: {row_index}. La matriz '{matrix_name}' tiene {matrix_rows} filas (índices válidos: 0-{matrix_rows - 1})")
        
        # VALIDACION DE RANGO para columnas
        if col_index < 0:
            raise RuntimeError(f"Índice de columna negativo: {col_index}. Los índices deben ser >= 0")
        
        if col_index >= matrix_cols:
            raise RuntimeError(f"Índice de columna fuera de rango: {col_index}. La matriz '{matrix_name}' tiene {matrix_cols} columnas (índices válidos: 0-{matrix_cols - 1})")
        
        # Calcular dirección efectiva (row-major order)
        target_addr = base_addr + (row_index * matrix_cols) + col_index
        
        # Validar dirección
        if target_addr >= len(self.memory):
            raise RuntimeError(f"Dirección de memoria inválida: {target_addr}")
        
        # Cargar valor
        value = self.memory[target_addr]
        if value is None:
            raise RuntimeError(f"Elemento de la matriz no inicializado en posición [{row_index}][{col_index}]")
        
        self.stack.append(value)
        self.instruction_pointer += 1
    
    # ========================================
    # OPERACIONES ARITMÉTICAS
    # ========================================
    
    def _exec_add(self) -> None:
        """Suma los dos valores del tope de la pila"""
        if len(self.stack) < 2:
            raise RuntimeError("Pila insuficiente para operación ADD")
        
        b = self.stack.pop()
        a = self.stack.pop()
        
        # Manejar concatenación de strings
        if isinstance(a, str) or isinstance(b, str):
            result = str(a) + str(b)
        else:
            result = a + b
        
        self.stack.append(result)
        self.instruction_pointer += 1
    
    def _exec_sub(self) -> None:
        """Resta los dos valores del tope de la pila"""
        if len(self.stack) < 2:
            raise RuntimeError("Pila insuficiente para operación SUB")
        
        b = self.stack.pop()
        a = self.stack.pop()
        result = a - b
        
        self.stack.append(result)
        self.instruction_pointer += 1
    
    def _exec_mul(self) -> None:
        """Multiplica los dos valores del tope de la pila"""
        if len(self.stack) < 2:
            raise RuntimeError("Pila insuficiente para operación MUL")
        
        b = self.stack.pop()
        a = self.stack.pop()
        result = a * b
        
        self.stack.append(result)
        self.instruction_pointer += 1
    
    def _exec_div(self) -> None:
        """Divide los dos valores del tope de la pila"""
        if len(self.stack) < 2:
            raise RuntimeError("Pila insuficiente para operación DIV")
        
        b = self.stack.pop()
        a = self.stack.pop()
        
        if b == 0:
            raise RuntimeError("División por cero")
        
        result = a / b
        self.stack.append(result)
        self.instruction_pointer += 1
    
    def _exec_mod(self) -> None:
        """Calcula el módulo de los dos valores del tope de la pila"""
        if len(self.stack) < 2:
            raise RuntimeError("Pila insuficiente para operación MOD")
        
        b = self.stack.pop()
        a = self.stack.pop()
        
        if b == 0:
            raise RuntimeError("División por cero en operación módulo")
        
        result = a % b
        self.stack.append(result)
        self.instruction_pointer += 1
    
    def _exec_neg(self) -> None:
        """Niega el valor del tope de la pila"""
        if not self.stack:
            raise RuntimeError("Pila vacía para operación NEG")
        
        a = self.stack.pop()
        result = -a
        
        self.stack.append(result)
        self.instruction_pointer += 1
    
    # ========================================
    # OPERACIONES DE COMPARACIÓN
    # ========================================
    
    def _exec_eq(self) -> None:
        """Compara igualdad de los dos valores del tope de la pila"""
        if len(self.stack) < 2:
            raise RuntimeError("Pila insuficiente para operación EQ")
        
        b = self.stack.pop()
        a = self.stack.pop()
        result = a == b
        
        self.stack.append(result)
        self.instruction_pointer += 1
    
    def _exec_neq(self) -> None:
        """Compara desigualdad de los dos valores del tope de la pila"""
        if len(self.stack) < 2:
            raise RuntimeError("Pila insuficiente para operación NEQ")
        
        b = self.stack.pop()
        a = self.stack.pop()
        result = a != b
        
        self.stack.append(result)
        self.instruction_pointer += 1
    
    def _exec_lt(self) -> None:
        """Compara menor que entre los dos valores del tope de la pila"""
        if len(self.stack) < 2:
            raise RuntimeError("Pila insuficiente para operación LT")
        
        b = self.stack.pop()
        a = self.stack.pop()
        result = a < b
        
        self.stack.append(result)
        self.instruction_pointer += 1
    
    def _exec_gt(self) -> None:
        """Compara mayor que entre los dos valores del tope de la pila"""
        if len(self.stack) < 2:
            raise RuntimeError("Pila insuficiente para operación GT")
        
        b = self.stack.pop()
        a = self.stack.pop()
        result = a > b
        
        self.stack.append(result)
        self.instruction_pointer += 1
    
    def _exec_leq(self) -> None:
        """Compara menor o igual entre los dos valores del tope de la pila"""
        if len(self.stack) < 2:
            raise RuntimeError("Pila insuficiente para operación LEQ")
        
        b = self.stack.pop()
        a = self.stack.pop()
        result = a <= b
        
        self.stack.append(result)
        self.instruction_pointer += 1
    
    def _exec_geq(self) -> None:
        """Compara mayor o igual entre los dos valores del tope de la pila"""
        if len(self.stack) < 2:
            raise RuntimeError("Pila insuficiente para operación GEQ")
        
        b = self.stack.pop()
        a = self.stack.pop()
        result = a >= b
        
        self.stack.append(result)
        self.instruction_pointer += 1
    
    # ========================================
    # OPERACIONES LÓGICAS
    # ========================================
    
    def _exec_and(self) -> None:
        """AND lógico de los dos valores del tope de la pila"""
        if len(self.stack) < 2:
            raise RuntimeError("Pila insuficiente para operación AND")
        
        b = self.stack.pop()
        a = self.stack.pop()
        result = a and b
        
        self.stack.append(result)
        self.instruction_pointer += 1
    
    def _exec_or(self) -> None:
        """OR lógico de los dos valores del tope de la pila"""
        if len(self.stack) < 2:
            raise RuntimeError("Pila insuficiente para operación OR")
        
        b = self.stack.pop()
        a = self.stack.pop()
        result = a or b
        
        self.stack.append(result)
        self.instruction_pointer += 1
    
    def _exec_not(self) -> None:
        """NOT lógico del valor del tope de la pila"""
        if not self.stack:
            raise RuntimeError("Pila vacía para operación NOT")
        
        a = self.stack.pop()
        result = not a
        
        self.stack.append(result)
        self.instruction_pointer += 1
    
    # ========================================
    # INSTRUCCIONES DE CONTROL DE FLUJO
    # ========================================
    
    def _exec_jump(self, instruction: Instruction) -> None:
        """Salta incondicionalmente a una etiqueta"""
        label = instruction.arg1
        if label not in self.labels:
            raise RuntimeError(f"Etiqueta no encontrada: {label}")
        
        self.instruction_pointer = self.labels[label]
    
    def _exec_jump_if_false(self, instruction: Instruction) -> None:
        """Salta a una etiqueta si el valor del tope de la pila es falso"""
        if not self.stack:
            raise RuntimeError("Pila vacía para operación JUMP_IF_FALSE")
        
        condition = self.stack.pop()
        
        if not condition:
            label = instruction.arg1
            if label not in self.labels:
                raise RuntimeError(f"Etiqueta no encontrada: {label}")
            self.instruction_pointer = self.labels[label]
        else:
            self.instruction_pointer += 1
    
    # ========================================
    # INSTRUCCIONES DE FUNCIONES
    # ========================================
    
    def _exec_call(self, instruction: Instruction) -> None:
        """Llama a una función"""
        function_name = instruction.arg1
        arg_count = instruction.arg2
        
        # Manejar funciones built-in (tradicionales y alquímicas)
        builtin_functions = ["print", "write", "read", "Transmute", "TransmuteLine", "Absorb", "AbsorbSolid", "AbsorbLiquid", "AbsorbPrinciple"]
        if function_name in builtin_functions:
            self._call_builtin_function(function_name, arg_count)
            return
        
        # Validar límite de recursión antes de hacer la llamada
        if len(self.call_stack) >= self.max_recursion_depth:
            raise RuntimeError(
                f"Límite de recursión excedido ({self.max_recursion_depth} llamadas). "
                f"Posible recursión infinita en función '{function_name}'"
            )
        
        # Verificar que la función existe
        if function_name not in self.labels:
            raise RuntimeError(f"Función no encontrada: {function_name}")
        
        # Extraer argumentos de la pila
        arguments = []
        for _ in range(arg_count):
            if not self.stack:
                raise RuntimeError(f"Argumentos insuficientes para función {function_name}")
            arguments.append(self.stack.pop())
        
        # Los argumentos están en orden inverso
        arguments.reverse()
        
        # Crear frame de función
        frame = StackFrame(
            function_name=function_name,
            return_address=self.instruction_pointer + 1,
            local_vars={},
            parameters=arguments
        )
        
        self.call_stack.append(frame)
        
        # Saltar a la función
        self.instruction_pointer = self.labels[function_name]
    
    def _call_builtin_function(self, function_name: str, arg_count: int) -> None:
        """Ejecuta una función built-in del sistema"""
        # Funciones alquímicas
        if function_name == "Transmute":
            # Transmute imprime un valor SIN salto de línea
            if arg_count != 1:
                raise RuntimeError(f"Transmute() espera 1 argumento, se encontraron {arg_count}")
            
            if not self.stack:
                raise RuntimeError("Argumento faltante para Transmute()")
            
            value = self.stack.pop()
            self.output += self.format_value_for_output(value)  # Sin salto de línea
            # Transmute es void, pero ponemos None en la pila para el POP
            self.stack.append(None)
        
        elif function_name == "TransmuteLine":
            # TransmuteLine imprime un valor CON salto de línea
            if arg_count != 1:
                raise RuntimeError(f"TransmuteLine() espera 1 argumento, se encontraron {arg_count}")
            
            if not self.stack:
                raise RuntimeError("Argumento faltante para TransmuteLine()")
            
            value = self.stack.pop()
            self.output += self.format_value_for_output(value) + "\n"  # Con salto de línea
            # TransmuteLine es void, pero ponemos None en la pila para el POP
            self.stack.append(None)
        
        elif function_name == "Absorb":
            # Absorb lee entrada de texto (equivalente alquímico de read)
            # Puede recibir 0 o 1 argumento (prompt opcional)
            if arg_count > 1:
                raise RuntimeError(f"Absorb() espera 0 o 1 argumento, se encontraron {arg_count}")
            
            # Si hay argumento, es el prompt (lo imprimimos pero no lo usamos para input)
            if arg_count == 1:
                if not self.stack:
                    raise RuntimeError("Argumento faltante para Absorb()")
                prompt = self.stack.pop()
                self.output.append(str(prompt))
            
            if self.input_buffer:
                value = self.input_buffer.pop(0)
                self.stack.append(value)
            else:
                self.stack.append("")  # Entrada vacía
        
        elif function_name == "AbsorbSolid":
            # AbsorbSolid lee un entero
            # Puede recibir 0 o 1 argumento (prompt opcional)
            if arg_count > 1:
                raise RuntimeError(f"AbsorbSolid() espera 0 o 1 argumento, se encontraron {arg_count}")
            
            # Si hay argumento, es el prompt
            if arg_count == 1:
                if not self.stack:
                    raise RuntimeError("Argumento faltante para AbsorbSolid()")
                prompt = self.stack.pop()
                self.output.append(str(prompt))
            
            if self.input_buffer:
                value = self.input_buffer.pop(0)
                try:
                    value = int(value)
                except ValueError:
                    raise RuntimeError(f"AbsorbSolid() esperaba un número entero, obtuvo: {value}")
                self.stack.append(value)
            else:
                self.stack.append(0)  # Valor por defecto
        
        elif function_name == "AbsorbLiquid":
            # AbsorbLiquid lee un flotante
            # Puede recibir 0 o 1 argumento (prompt opcional)
            if arg_count > 1:
                raise RuntimeError(f"AbsorbLiquid() espera 0 o 1 argumento, se encontraron {arg_count}")
            
            # Si hay argumento, es el prompt
            if arg_count == 1:
                if not self.stack:
                    raise RuntimeError("Argumento faltante para AbsorbLiquid()")
                prompt = self.stack.pop()
                self.output.append(str(prompt))
            
            if self.input_buffer:
                value = self.input_buffer.pop(0)
                try:
                    value = float(value)
                except ValueError:
                    raise RuntimeError(f"AbsorbLiquid() esperaba un número decimal, obtuvo: {value}")
                self.stack.append(value)
            else:
                self.stack.append(0.0)  # Valor por defecto
        
        elif function_name == "AbsorbPrinciple":
            # AbsorbPrinciple lee un booleano
            # Si recibe texto no vacío -> Accepted (True)
            # Si recibe texto vacío -> Rejected (False)
            # Puede recibir 0 o 1 argumento (prompt opcional)
            if arg_count > 1:
                raise RuntimeError(f"AbsorbPrinciple() espera 0 o 1 argumento, se encontraron {arg_count}")
            
            # Si hay argumento, es el prompt
            if arg_count == 1:
                if not self.stack:
                    raise RuntimeError("Argumento faltante para AbsorbPrinciple()")
                prompt = self.stack.pop()
                self.output.append(str(prompt))
            
            if self.input_buffer:
                value = self.input_buffer.pop(0)
                # Si hay texto (no vacío) -> True (Accepted)
                # Si está vacío -> False (Rejected)
                result = bool(value.strip())
                self.stack.append(result)
            else:
                self.stack.append(False)  # Valor por defecto (Rejected)
        
        # Funciones tradicionales
        elif function_name == "print":
            if arg_count != 1:
                raise RuntimeError(f"print() espera 1 argumento, se encontraron {arg_count}")
            
            if not self.stack:
                raise RuntimeError("Argumento faltante para print()")
            
            value = self.stack.pop()
            self.output.append(str(value))
            # print es void, pero ponemos None en la pila para el POP
            self.stack.append(None)
            
        elif function_name == "write":
            if arg_count != 1:
                raise RuntimeError(f"write() espera 1 argumento, se encontraron {arg_count}")
            
            if not self.stack:
                raise RuntimeError("Argumento faltante para write()")
            
            value = self.stack.pop()
            self.output.append(str(value))
            # write es void, pero ponemos None en la pila para el POP
            self.stack.append(None)
            
        elif function_name == "read":
            if arg_count != 0:
                raise RuntimeError(f"read() no espera argumentos, se encontraron {arg_count}")
            
            if self.input_buffer:
                value = self.input_buffer.pop(0)
                # Intentar convertir a número si es posible
                try:
                    if '.' in value:
                        value = float(value)
                    else:
                        value = int(value)
                except ValueError:
                    pass  # Mantener como string
                
                self.stack.append(value)
            else:
                self.stack.append("")  # Entrada vacía
        
        self.instruction_pointer += 1
    
    def _exec_return(self) -> None:
        """Retorna de una función sin valor"""
        if not self.call_stack:
            # Return en función main - terminar programa
            self.halted = True
            return
        
        frame = self.call_stack.pop()
        
        # Para funciones void, ponemos None en la pila para el POP
        self.stack.append(None)
        
        self.instruction_pointer = frame.return_address
    
    def _exec_return_value(self) -> None:
        """Retorna de una función con valor"""
        if not self.stack:
            raise RuntimeError("Valor de retorno faltante")
        
        return_value = self.stack.pop()
        
        if not self.call_stack:
            # Return en función main - terminar programa
            self.halted = True
            return
        
        frame = self.call_stack.pop()
        
        # Poner el valor de retorno en la pila
        self.stack.append(return_value)
        
        self.instruction_pointer = frame.return_address
    
    def _exec_enter(self, instruction: Instruction) -> None:
        """Entra a una función (reserva espacio para parámetros)"""
        # Esta instrucción es principalmente para compatibilidad
        # El trabajo real se hace en CALL
        self.instruction_pointer += 1
    
    def _exec_leave(self) -> None:
        """Sale de una función (limpia el frame)"""
        # Esta instrucción es principalmente para compatibilidad
        # El trabajo real se hace en RETURN
        self.instruction_pointer += 1
    
    # ========================================
    # OTRAS INSTRUCCIONES
    # ========================================
    
    def _exec_halt(self) -> None:
        """Detiene la ejecución del programa"""
        self.halted = True
    
    def _exec_pop(self) -> None:
        """Remueve el valor del tope de la pila"""
        if not self.stack:
            raise RuntimeError("Pila vacía para operación POP")
        
        self.stack.pop()
        self.instruction_pointer += 1
    
    def get_output(self) -> str:
        """Retorna la salida generada por el programa"""
        return self.output
    
    def get_memory_dump(self) -> Dict[str, Any]:
        """Retorna un dump del estado de la memoria para debugging"""
        return {
            "memory": [val for i, val in enumerate(self.memory) if val is not None],
            "stack": self.stack.copy(),
            "call_stack": [f"{frame.function_name}@{frame.return_address}" for frame in self.call_stack],
            "instruction_pointer": self.instruction_pointer,
            "halted": self.halted
        }


def main():
    """Función de prueba del intérprete"""
    from .lexer import AlchemistLexer
    from .parser import AlchemistParser
    from .semantic_analyzer import AlchemistSemanticAnalyzer
    from .code_generator import AlchemistCodeGenerator
    
    # Código de prueba
    test_code = '''
    func main() -> void {
        int a = 10
        int b = 20
        
        print("Valores iniciales:")
        print("a = " + a)
        print("b = " + b)
        
        int suma = a + b
        print("La suma es: " + suma)
        
        if (suma > 25) {
            print("La suma es mayor a 25")
        } else {
            print("La suma es menor o igual a 25")
        }
    }
    '''
    
    try:
        # Compilación completa
        lexer = AlchemistLexer()
        parser = AlchemistParser()
        analyzer = AlchemistSemanticAnalyzer()
        generator = AlchemistCodeGenerator()
        
        # Análisis
        ast = parser.parse(test_code)
        errors = analyzer.analyze(ast)
        
        if errors:
            print("❌ Errores semánticos:")
            for error in errors:
                print(f"  • {error}")
            return
        
        # Generación de código
        instructions = generator.generate(ast)
        
        print("🚀 EJECUTANDO PROGRAMA")
        print("=" * 50)
        
        # Ejecución
        interpreter = AlchemistInterpreter()
        interpreter.load_program(instructions, generator.variables, generator.functions)
        
        output = interpreter.execute()
        
        print("📄 SALIDA DEL PROGRAMA:")
        print("=" * 30)
        for line in output:
            print(line)
        
        print(f"\n✅ Programa ejecutado correctamente!")
        
    except Exception as e:
        print(f"❌ Error durante la ejecución: {e}")


if __name__ == "__main__":
    main()
