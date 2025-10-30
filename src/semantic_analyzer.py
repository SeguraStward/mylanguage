#!/usr/bin/env python3
"""
Analizador Semantico para Alchemist
Este archivo se encarga de revisar que el codigo tenga sentido, tipos correctos 
"""

from typing import Dict, List, Optional 
from dataclasses import dataclass

# importamos todas las clases del parser que necesitamos para trabajar
from .parser import (
    Program, Function, Parameter, Statement, Expression,
    VariableDeclaration, Assignment, ObserveStatement, WhileStatement, 
    ForStatement, ReturnStatement, BreakStatement, ContinueStatement,
    ExpressionStatement, BinaryOperation, UnaryOperation, FunctionCall,
    Variable, Literal, AlternativelyPart, ArrayDeclaration, ArrayAssignment, ArrayAccess
)


@dataclass
class Symbol:
    """clase que representa un simbolo en nuestra tabla, puede ser variable o funcion"""
    name: str
    type: str
    is_function: bool = False
    parameters: Optional[List[Parameter]] = None
    return_type: Optional[str] = None
    is_constant: bool = False  # para constantes, aunque no las usemos aun
    is_array: bool = False  # True si es un array
    array_element_type: Optional[str] = None  # Tipo de elementos del array
    array_size: Optional[int] = None  # Tamaño del array
    line: int = 0


class SymbolTable:
    """tabla donde guardamos todos los simbolos, variables y funciones"""
    
    def __init__(self, parent: Optional['SymbolTable'] = None):
        """
        crea una nueva tabla de simbolos
        el parent es para cuando tenemos funciones dentro de otras (scopes)
        """
        self.symbols: Dict[str, Symbol] = {}
        self.parent = parent  # tabla padre si estamos en un scope anidado
    
    def declare(self, symbol: Symbol) -> None:
        """
        declara un simbolo nuevo en esta tabla
        si ya existe, lanza error porque no podemos tener duplicados
        """
        if symbol.name in self.symbols:
            raise SemanticError(f"El simbolo '{symbol.name}' ya fue declarado", symbol.line)
        self.symbols[symbol.name] = symbol
    
    def lookup(self, name: str) -> Optional[Symbol]:
        """
        busca un simbolo, primero en esta tabla y luego en las tablas padre
        asi podemos acceder a variables de scopes superiores
        """
        if name in self.symbols:
            return self.symbols[name]
        
        # si no esta aca, buscar en el padre
        if self.parent:
            return self.parent.lookup(name)
        
        return None  # no se encontro en ningun lado
    
    def lookup_current_scope(self, name: str) -> Optional[Symbol]:
        """
        busca solo en el scope actual, no en los padres
        util para verificar redeclaraciones
        """
        return self.symbols.get(name)


class SemanticError(Exception):
    """cuando algo esta mal semanticamente, usamos esta excepcion"""
    def __init__(self, message: str, line: int):
        self.message = message
        self.line = line
        super().__init__(f"Error semantico en linea {line}: {message}")


class AlchemistSemanticAnalyzer:
    """la clase principal que se encarga de analizar todo el codigo"""
    
    def __init__(self):
        """inicializa el analizador, crea las tablas y eso"""
        self.global_table = SymbolTable()  # tabla global para funciones
        self.current_table = self.global_table  # tabla actual donde estamos trabajando
        self.current_function: Optional[Function] = None  # funcion que estamos analizando
        self.in_loop = False  # para saber si estamos dentro de un ciclo
        self.errors: List[SemanticError] = []  # lista de errores que vamos encontrando
        
        # debug_mode = False  # por si queremos imprimir cosas
        
        # agregamos las funciones que ya vienen con el lenguaje
        self._agregar_funciones_del_sistema()
    
    def _agregar_funciones_del_sistema(self) -> None:
        """agrega las funciones que ya vienen con Alchemist como Transmute, Absorb, etc"""
        
        # funcion Absorb() que devuelve string (lee entrada)
        simbolo_absorb = Symbol(
            name="Absorb",
            type="Inscription",
            is_function=True,
            parameters=[],
            return_type="Inscription",
            line=0
        )
        self.global_table.declare(simbolo_absorb)
        
        # funcion AbsorbSolid() que devuelve int (lee un entero)
        simbolo_absorbsolid = Symbol(
            name="AbsorbSolid",
            type="Solid",
            is_function=True,
            parameters=[],
            return_type="Solid",
            line=0
        )
        self.global_table.declare(simbolo_absorbsolid)
        
        # funcion Transmute que imprime (acepta cualquier tipo)
        simbolo_transmute = Symbol(
            name="Transmute",
            type="void",
            is_function=True,
            parameters=[Parameter("value", "any")],  # Acepta cualquier tipo
            return_type="void",
            line=0
        )
        self.global_table.declare(simbolo_transmute)
        
        # Funciones tradicionales para compatibilidad
        # funcion read() que devuelve string
        simbolo_read = Symbol(
            name="read",
            type="string",
            is_function=True,
            parameters=[],
            return_type="string",
            line=0
        )
        self.global_table.declare(simbolo_read)
        
        # funcion print(string) que no devuelve nada
        simbolo_print = Symbol(
            name="print",
            type="void",
            is_function=True,
            parameters=[Parameter("message", "string")],
            return_type="void",
            line=0
        )
        self.global_table.declare(simbolo_print)
        
        # funcion write(string) similar a print
        simbolo_write = Symbol(
            name="write",
            type="void",
            is_function=True,
            parameters=[Parameter("message", "string")],
            return_type="void",
            line=0
        )
        self.global_table.declare(simbolo_write)
    
    def analyze(self, arbol_sintactico: Program) -> List[SemanticError]:
        """
        esta es la funcion principal que analiza todo el programa
        recibe el arbol sintactico y devuelve los errores que encuentra
        """
        self.errors = []  # limpiamos errores anteriores
        
        try:
            # primero declaramos todas las funciones para que se puedan llamar entre ellas
            for funcion in arbol_sintactico.functions:
                self._declarar_funcion(funcion)
            
            # verificamos que exista la funcion GateOfTruth, esto es obligatorio
            simbolo_main = self.global_table.lookup("GateOfTruth")
            if not simbolo_main:
                self.errors.append(SemanticError("Se necesita una funcion 'GateOfTruth' para que el programa funcione", 1))
            elif simbolo_main.return_type != "void":
                self.errors.append(SemanticError("La funcion 'GateOfTruth' debe devolver 'void', no otra cosa", 1))
            elif simbolo_main.parameters:
                self.errors.append(SemanticError("La funcion 'GateOfTruth' no puede tener parametros", 1))
            
            # ahora analizamos el contenido de cada funcion
            for funcion in arbol_sintactico.functions:
                self._analizar_funcion(funcion)
                
        except SemanticError as error:
            self.errors.append(error)
        
        return self.errors
    
    def _declarar_funcion(self, funcion: Function) -> None:
        """declara una funcion en la tabla global para que otros la puedan usar"""
        simbolo_funcion = Symbol(
            name=funcion.name,
            type=funcion.return_type,
            is_function=True,
            parameters=funcion.parameters,
            return_type=funcion.return_type,
            line=funcion.line
        )
        
        try:
            self.global_table.declare(simbolo_funcion)
        except SemanticError as error:
            self.errors.append(error)
    
    def _analizar_funcion(self, funcion: Function) -> None:
        """analiza el contenido de una funcion especifica"""
        # creamos una nueva tabla para las variables locales de esta funcion
        tabla_funcion = SymbolTable(self.global_table)
        tabla_anterior = self.current_table
        funcion_anterior = self.current_function
        
        self.current_table = tabla_funcion
        self.current_function = funcion
        
        try:
            # declaramos los parametros como variables locales
            for parametro in funcion.parameters:
                simbolo_param = Symbol(
                    name=parametro.name,
                    type=parametro.type,
                    line=funcion.line
                )
                self.current_table.declare(simbolo_param)
            
            # analizamos todas las declaraciones del cuerpo de la funcion
            for declaracion in funcion.body:
                self._analizar_declaracion(declaracion)
            
            # verificamos que las funciones que no son void tengan return
            if funcion.return_type != "void":
                if not self._tiene_return(funcion.body):
                    self.errors.append(SemanticError(
                        f"La funcion '{funcion.name}' debe tener return porque no es void", 
                        funcion.line
                    ))
                    
        except SemanticError as error:
            self.errors.append(error)
        finally:
            # restauramos el estado anterior
            self.current_table = tabla_anterior
            self.current_function = funcion_anterior
    
    def _tiene_return(self, declaraciones: List[Statement]) -> bool:
        """verifica si una lista de declaraciones tiene al menos un return"""
        for declaracion in declaraciones:
            if isinstance(declaracion, ReturnStatement):
                return True
            # tambien revisamos dentro de los observe por si acaso
            elif isinstance(declaracion, ObserveStatement):
                # debe tener return en todas las ramas para contar como valido
                tiene_then = self._tiene_return(declaracion.then_body)
                tiene_else = False
                if declaracion.inevitably_body:
                    tiene_else = self._tiene_return(declaracion.inevitably_body)
                elif declaracion.alternatively_parts:
                    # revisar los alternatively tambien, todos deben tener return
                    for alt_part in declaracion.alternatively_parts:
                        if self._tiene_return(alt_part.body):
                            tiene_else = True
                            break
                
                if tiene_then and tiene_else:
                    return True
        
        return False
    
    def _analizar_declaracion(self, declaracion: Statement) -> None:
        """
        analiza una declaracion, puede ser variable, asignacion, observe, etc
        """
        if isinstance(declaracion, VariableDeclaration):
            self._analizar_declaracion_variable(declaracion)
        elif isinstance(declaracion, ArrayDeclaration):
            self._analizar_declaracion_array(declaracion)
        elif isinstance(declaracion, Assignment):
            self._analizar_asignacion(declaracion)
        elif isinstance(declaracion, ArrayAssignment):
            self._analizar_asignacion_array(declaracion)
        elif isinstance(declaracion, ObserveStatement):
            self._analizar_observe(declaracion)
        elif isinstance(declaracion, WhileStatement):
            self._analizar_while(declaracion)
        elif isinstance(declaracion, ForStatement):
            self._analizar_for(declaracion)
        elif isinstance(declaracion, ReturnStatement):
            self._analizar_return(declaracion)
        elif isinstance(declaracion, BreakStatement):
            self._analizar_break(declaracion)
        elif isinstance(declaracion, ContinueStatement):
            self._analizar_continue(declaracion)
        elif isinstance(declaracion, ExpressionStatement):
            # solo analizamos la expresion, no hacemos nada mas
            self._analizar_expresion(declaracion.expression)
    
    def _analizar_declaracion_variable(self, declaracion_var: VariableDeclaration) -> None:
        """analiza cuando declaramos una variable nueva como 'Solid x = 5'"""
        # verificar que el tipo sea valido, solo aceptamos estos
        # Tipos alquímicos: Solid (int), Liquid (float), Inscription (string), Principle (bool)
        # También soportamos los tipos tradicionales para compatibilidad
        tipos_validos = ["int", "float", "string", "bool", "Solid", "Liquid", "Inscription", "Principle", "void"]
        if declaracion_var.type not in tipos_validos:
            self.errors.append(SemanticError(
                f"El tipo '{declaracion_var.type}' no existe o no esta soportado", 
                declaracion_var.line
            ))
            return
        
        # si hay valor inicial, verificamos que el tipo coincida
        if declaracion_var.value:
            tipo_valor = self._analizar_expresion(declaracion_var.value)
            if tipo_valor and not self._tipos_compatibles(declaracion_var.type, tipo_valor):
                self.errors.append(SemanticError(
                    f"No puedes asignar un '{tipo_valor}' a una variable '{declaracion_var.type}'",
                    declaracion_var.line
                ))
        
        # crear simbolo para la variable y agregarlo a la tabla
        simbolo_variable = Symbol(
            name=declaracion_var.name,
            type=declaracion_var.type,
            line=declaracion_var.line
        )
        
        try:
            self.current_table.declare(simbolo_variable)
        except SemanticError as error:
            self.errors.append(error)
    
    def _analizar_declaracion_array(self, declaracion_array: ArrayDeclaration) -> None:
        """analiza declaracion de array: AlchemicArray[Solid, 5] numeros"""
        # verificar que el tipo de elemento sea valido
        tipos_validos = ["Solid", "Liquid", "Inscription", "Principle"]
        if declaracion_array.element_type not in tipos_validos:
            self.errors.append(SemanticError(
                f"El tipo de elemento '{declaracion_array.element_type}' no es valido para arrays", 
                declaracion_array.line
            ))
            return
        
        # verificar que el tamaño sea positivo (ya lo hace el parser pero por seguridad)
        if declaracion_array.size <= 0:
            self.errors.append(SemanticError(
                f"El tamaño del array debe ser mayor a 0", 
                declaracion_array.line
            ))
            return
        
        # crear simbolo para el array
        simbolo_array = Symbol(
            name=declaracion_array.name,
            type="array",  # Tipo general "array"
            is_array=True,
            array_element_type=declaracion_array.element_type,
            array_size=declaracion_array.size,
            line=declaracion_array.line
        )
        
        try:
            self.current_table.declare(simbolo_array)
        except SemanticError as error:
            self.errors.append(error)
    
    def _analizar_asignacion_array(self, asignacion: ArrayAssignment) -> None:
        """analiza asignacion a elemento de array: numeros[0] = 10"""
        # verificar que el array existe
        simbolo_array = self.current_table.lookup(asignacion.name)
        if not simbolo_array:
            self.errors.append(SemanticError(
                f"El array '{asignacion.name}' no ha sido declarado", 
                asignacion.line
            ))
            return
        
        # verificar que es realmente un array
        if not simbolo_array.is_array:
            self.errors.append(SemanticError(
                f"'{asignacion.name}' no es un array, no se puede usar []", 
                asignacion.line
            ))
            return
        
        # verificar que el indice sea de tipo Solid (entero)
        tipo_indice = self._analizar_expresion(asignacion.index)
        if tipo_indice and tipo_indice not in ["Solid", "int"]:
            self.errors.append(SemanticError(
                f"El indice del array debe ser Solid (entero), no '{tipo_indice}'", 
                asignacion.line
            ))
        
        # VALIDACION DE RANGO: si el indice es una constante, verificar que este en rango
        from .parser import Literal
        if isinstance(asignacion.index, Literal) and isinstance(asignacion.index.value, int):
            indice_valor = asignacion.index.value
            if indice_valor < 0:
                self.errors.append(SemanticError(
                    f"Indice de array negativo: {indice_valor}. Los indices deben ser >= 0", 
                    asignacion.line
                ))
            elif indice_valor >= simbolo_array.array_size:
                self.errors.append(SemanticError(
                    f"Indice fuera de rango: {indice_valor}. El array '{asignacion.name}' tiene tamaño {simbolo_array.array_size} (indices validos: 0-{simbolo_array.array_size - 1})", 
                    asignacion.line
                ))
        
        # verificar que el valor asignado sea del mismo tipo que los elementos del array
        tipo_valor = self._analizar_expresion(asignacion.value)
        if tipo_valor and not self._tipos_compatibles(simbolo_array.array_element_type, tipo_valor):
            self.errors.append(SemanticError(
                f"No puedes asignar '{tipo_valor}' a un array de '{simbolo_array.array_element_type}'", 
                asignacion.line
            ))
    
    def _analizar_acceso_array(self, acceso: ArrayAccess) -> Optional[str]:
        """analiza acceso a elemento de array: numeros[0]"""
        # verificar que el array existe
        simbolo_array = self.current_table.lookup(acceso.name)
        if not simbolo_array:
            self.errors.append(SemanticError(
                f"El array '{acceso.name}' no ha sido declarado", 
                acceso.line
            ))
            return None
        
        # verificar que es realmente un array
        if not simbolo_array.is_array:
            self.errors.append(SemanticError(
                f"'{acceso.name}' no es un array, no se puede usar []", 
                acceso.line
            ))
            return None
        
        # verificar que el indice sea de tipo Solid (entero)
        tipo_indice = self._analizar_expresion(acceso.index)
        if tipo_indice and tipo_indice not in ["Solid", "int"]:
            self.errors.append(SemanticError(
                f"El indice del array debe ser Solid (entero), no '{tipo_indice}'", 
                acceso.line
            ))
        
        # VALIDACION DE RANGO: si el indice es una constante, verificar que este en rango
        from .parser import Literal
        if isinstance(acceso.index, Literal) and isinstance(acceso.index.value, int):
            indice_valor = acceso.index.value
            if indice_valor < 0:
                self.errors.append(SemanticError(
                    f"Indice de array negativo: {indice_valor}. Los indices deben ser >= 0", 
                    acceso.line
                ))
            elif indice_valor >= simbolo_array.array_size:
                self.errors.append(SemanticError(
                    f"Indice fuera de rango: {indice_valor}. El array '{acceso.name}' tiene tamaño {simbolo_array.array_size} (indices validos: 0-{simbolo_array.array_size - 1})", 
                    acceso.line
                ))
        
        # el tipo del acceso es el tipo de los elementos del array
        return simbolo_array.array_element_type
    
    def _analizar_asignacion(self, asignacion: Assignment) -> None:
        """analiza cuando asignamos un valor a una variable existente"""
        # verificar que la variable ya existe
        simbolo_variable = self.current_table.lookup(asignacion.name)
        if not simbolo_variable:
            self.errors.append(SemanticError(
                f"La variable '{asignacion.name}' no ha sido declarada antes", 
                asignacion.line
            ))
            return
        
        # verificar que no sea una funcion
        if simbolo_variable.is_function:
            self.errors.append(SemanticError(
                f"No puedes asignar algo a '{asignacion.name}' porque es una funcion", 
                asignacion.line
            ))
            return
        
        # analizar el valor que queremos asignar
        tipo_valor = self._analizar_expresion(asignacion.value)
        if tipo_valor and not self._tipos_compatibles(simbolo_variable.type, tipo_valor):
            self.errors.append(SemanticError(
                f"No puedes asignar un '{tipo_valor}' a una variable '{simbolo_variable.type}'",
                asignacion.line
            ))
    
    def _analizar_observe(self, declaracion_observe: ObserveStatement) -> None:
        """analiza una declaracion observe con sus alternatively e inevitably"""
        # la condicion del observe debe ser booleana, sino no tiene sentido
        tipo_condicion = self._analizar_expresion(declaracion_observe.condition)
        if tipo_condicion and tipo_condicion != "bool":
            self.errors.append(SemanticError(
                "La condicion del 'observe' tiene que ser true o false (bool)",
                declaracion_observe.line
            ))
        
        # analizamos el bloque del then (lo que pasa si es true)
        for declaracion in declaracion_observe.then_body:
            self._analizar_declaracion(declaracion)
        
        # analizamos todos los alternatively si los hay
        for parte_alt in declaracion_observe.alternatively_parts:
            tipo_condicion_alt = self._analizar_expresion(parte_alt.condition)
            if tipo_condicion_alt and tipo_condicion_alt != "bool":
                self.errors.append(SemanticError(
                    "La condicion del 'alternatively' tambien tiene que ser bool",
                    declaracion_observe.line
                ))
            for declaracion in parte_alt.body:
                self._analizar_declaracion(declaracion)
        
        # analizamos el inevitably si existe
        if declaracion_observe.inevitably_body:
            for declaracion in declaracion_observe.inevitably_body:
                self._analizar_declaracion(declaracion)
    
    def _analizar_while(self, declaracion_while: WhileStatement) -> None:
        """analiza un ciclo while"""
        # la condicion debe ser booleana
        tipo_condicion = self._analizar_expresion(declaracion_while.condition)
        if tipo_condicion and tipo_condicion != "bool":
            self.errors.append(SemanticError(
                "La condicion del while debe ser bool para que funcione",
                declaracion_while.line
            ))
        
        # marcamos que estamos dentro de un ciclo para break y continue
        estaba_en_ciclo = self.in_loop
        self.in_loop = True
        
        try:
            # analizamos todo lo que esta dentro del while
            for declaracion in declaracion_while.body:
                self._analizar_declaracion(declaracion)
        finally:
            # restauramos el estado anterior
            self.in_loop = estaba_en_ciclo
    
    def _analizar_for(self, declaracion_for: ForStatement) -> None:
        """analiza un ciclo for, es mas complicado porque tiene 3 partes"""
        # creamos un nuevo scope para el for porque puede declarar variables
        tabla_for = SymbolTable(self.current_table)
        tabla_anterior = self.current_table
        self.current_table = tabla_for
        
        try:
            # primera parte: inicializacion (puede ser declaracion de variable)
            if declaracion_for.init:
                self._analizar_declaracion(declaracion_for.init)
            
            # segunda parte: condicion (debe ser bool)
            if declaracion_for.condition:
                tipo_condicion = self._analizar_expresion(declaracion_for.condition)
                if tipo_condicion and tipo_condicion != "bool":
                    self.errors.append(SemanticError(
                        "La condicion del for debe ser bool",
                        declaracion_for.line
                    ))
            
            # tercera parte: actualizacion (normalmente una asignacion)
            if declaracion_for.update:
                self._analizar_declaracion(declaracion_for.update)
            
            # marcamos que estamos en ciclo y analizamos el cuerpo
            estaba_en_ciclo = self.in_loop
            self.in_loop = True
            
            try:
                for declaracion in declaracion_for.body:
                    self._analizar_declaracion(declaracion)
            finally:
                self.in_loop = estaba_en_ciclo
                
        finally:
            # siempre restauramos la tabla anterior
            self.current_table = tabla_anterior
    
    def _analizar_return(self, declaracion_return: ReturnStatement) -> None:
        """analiza una declaracion return"""
        # verificar que estamos dentro de una funcion
        if not self.current_function:
            self.errors.append(SemanticError(
                "No puedes usar 'return' fuera de una funcion", 
                declaracion_return.line
            ))
            return
        
        tipo_esperado = self.current_function.return_type
        
        if declaracion_return.value:
            # hay un valor de retorno
            if tipo_esperado == "void":
                self.errors.append(SemanticError(
                    f"La funcion '{self.current_function.name}' no debe devolver nada (es void)",
                    declaracion_return.line
                ))
            else:
                tipo_valor = self._analizar_expresion(declaracion_return.value)
                if tipo_valor and not self._tipos_compatibles(tipo_esperado, tipo_valor):
                    self.errors.append(SemanticError(
                        f"Estas devolviendo un '{tipo_valor}' pero la funcion debe devolver '{tipo_esperado}'",
                        declaracion_return.line
                    ))
        else:
            # no hay valor de retorno (return vacio)
            if tipo_esperado != "void":
                self.errors.append(SemanticError(
                    f"La funcion '{self.current_function.name}' debe devolver algo de tipo '{tipo_esperado}'",
                    declaracion_return.line
                ))
    
    def _analizar_break(self, declaracion_break: BreakStatement) -> None:
        """analiza una declaracion break"""
        if not self.in_loop:
            self.errors.append(SemanticError(
                "Solo puedes usar 'break' dentro de un ciclo (while o for)", 
                declaracion_break.line
            ))
    
    def _analizar_continue(self, declaracion_continue: ContinueStatement) -> None:
        """analiza una declaracion continue"""
        if not self.in_loop:
            self.errors.append(SemanticError(
                "Solo puedes usar 'continue' dentro de un ciclo (while o for)", 
                declaracion_continue.line
            ))
    
    def _analizar_expresion(self, expresion: Expression) -> Optional[str]:
        """
        analiza una expresion y devuelve su tipo
        esto es importante para verificar que todo tenga sentido
        """
        if isinstance(expresion, Literal):
            # es un literal como 5, "hola", true, etc
            return expresion.type
        
        elif isinstance(expresion, Variable):
            # es una variable, verificamos que exista
            simbolo = self.current_table.lookup(expresion.name)
            if not simbolo:
                self.errors.append(SemanticError(
                    f"La variable '{expresion.name}' no existe", 
                    expresion.line
                ))
                return None
            
            if simbolo.is_function:
                self.errors.append(SemanticError(
                    f"'{expresion.name}' es una funcion, no una variable", 
                    expresion.line
                ))
                return None
            
            return simbolo.type
        
        elif isinstance(expresion, ArrayAccess):
            # acceso a elemento de array: numeros[0]
            return self._analizar_acceso_array(expresion)
        
        elif isinstance(expresion, BinaryOperation):
            # operaciones como +, -, *, ==, etc
            return self._analizar_operacion_binaria(expresion)
        
        elif isinstance(expresion, UnaryOperation):
            # operaciones como -, not
            return self._analizar_operacion_unaria(expresion)
        
        elif isinstance(expresion, FunctionCall):
            # llamadas a funciones
            return self._analizar_llamada_funcion(expresion)
        
        return None  # no sabemos que es
    
    def _analizar_operacion_binaria(self, expresion: BinaryOperation) -> Optional[str]:
        """analiza operaciones con dos operandos como a + b, x == y"""
        tipo_izquierdo = self._analizar_expresion(expresion.left)
        tipo_derecho = self._analizar_expresion(expresion.right)
        
        # si alguno fallo, no podemos continuar
        if not tipo_izquierdo or not tipo_derecho:
            return None
        
        # operadores aritmeticos (+, -, *, /, %)
        if expresion.operator in ["+", "-", "*", "/", "%"]:
            if expresion.operator == "+":
                # el + es especial porque puede sumar numeros o concatenar strings
                if tipo_izquierdo == "string" and tipo_derecho == "string":
                    return "string"
                elif tipo_izquierdo == "string" or tipo_derecho == "string":
                    # permitimos concatenar string con otros tipos (conversion automatica)
                    return "string"
                elif self._es_numerico(tipo_izquierdo) and self._es_numerico(tipo_derecho):
                    return self._obtener_tipo_resultado_numerico(tipo_izquierdo, tipo_derecho)
            else:
                # otros operadores solo funcionan con numeros
                if self._es_numerico(tipo_izquierdo) and self._es_numerico(tipo_derecho):
                    return self._obtener_tipo_resultado_numerico(tipo_izquierdo, tipo_derecho)
            
            # si llegamos aca, los tipos no son compatibles
            self.errors.append(SemanticError(
                f"No puedes usar '{expresion.operator}' con tipos '{tipo_izquierdo}' y '{tipo_derecho}'",
                1  # TODO: pasar la linea real
            ))
            return None
        
        # operadores de comparacion (==, !=, <, >, <=, >=)
        elif expresion.operator in ["==", "!=", "<", ">", "<=", ">="]:
            if self._tipos_compatibles(tipo_izquierdo, tipo_derecho):
                return "bool"
            
            self.errors.append(SemanticError(
                f"No puedes comparar '{tipo_izquierdo}' con '{tipo_derecho}'",
                1  # TODO: pasar linea real
            ))
            return None
        
        # operadores logicos (and, or)
        elif expresion.operator in ["and", "or"]:
            if tipo_izquierdo == "bool" and tipo_derecho == "bool":
                return "bool"
            
            self.errors.append(SemanticError(
                f"'{expresion.operator}' solo funciona con valores bool",
                1  # TODO: pasar linea real
            ))
            return None
        
        return None
    
    def _analizar_operacion_unaria(self, expresion: UnaryOperation) -> Optional[str]:
        """analiza operaciones con un solo operando como -x, not y"""
        tipo_operando = self._analizar_expresion(expresion.operand)
        
        if not tipo_operando:
            return None
        
        if expresion.operator == "not":
            # not solo funciona con bool
            if tipo_operando == "bool":
                return "bool"
            
            self.errors.append(SemanticError(
                f"'not' solo funciona con bool, no con '{tipo_operando}'",
                1  # TODO: pasar linea real
            ))
            return None
        
        elif expresion.operator == "-":
            # menos solo funciona con numeros
            if self._es_numerico(tipo_operando):
                return tipo_operando
            
            self.errors.append(SemanticError(
                f"'-' solo funciona con numeros, no con '{tipo_operando}'",
                1  # TODO: pasar linea real
            ))
            return None
        
        return None
    
    def _analizar_llamada_funcion(self, expresion: FunctionCall) -> Optional[str]:
        """analiza cuando llamamos a una funcion como print('hola') o calcular(5, 3)"""
        simbolo_funcion = self.current_table.lookup(expresion.name)
        
        # verificar que la funcion existe
        if not simbolo_funcion:
            self.errors.append(SemanticError(
                f"La funcion '{expresion.name}' no existe", 
                expresion.line
            ))
            return None
        
        # verificar que sea realmente una funcion
        if not simbolo_funcion.is_function:
            self.errors.append(SemanticError(
                f"'{expresion.name}' no es una funcion", 
                expresion.line
            ))
            return None
        
        # verificar numero de argumentos
        parametros_esperados = len(simbolo_funcion.parameters) if simbolo_funcion.parameters else 0
        argumentos_recibidos = len(expresion.arguments)
        
        if parametros_esperados != argumentos_recibidos:
            self.errors.append(SemanticError(
                f"La funcion '{expresion.name}' necesita {parametros_esperados} argumentos, pero le diste {argumentos_recibidos}",
                expresion.line
            ))
            return simbolo_funcion.return_type
        
        # verificar tipos de argumentos
        if simbolo_funcion.parameters:
            for i, (parametro, argumento) in enumerate(zip(simbolo_funcion.parameters, expresion.arguments)):
                tipo_argumento = self._analizar_expresion(argumento)
                if tipo_argumento and not self._tipos_compatibles(parametro.type, tipo_argumento):
                    self.errors.append(SemanticError(
                        f"Argumento {i+1} de '{expresion.name}': esperaba '{parametro.type}' pero recibio '{tipo_argumento}'",
                        expresion.line
                    ))
        
        return simbolo_funcion.return_type
    
    def _tipos_compatibles(self, tipo_esperado: str, tipo_actual: str) -> bool:
        """
        verifica si dos tipos son compatibles entre si
        Mapea los tipos alquímicos a los tradicionales:
        Solid <-> int, Liquid <-> float, Inscription <-> string, Principle <-> bool
        """
        # Mapeo de tipos alquímicos a tradicionales
        tipo_map = {
            "Solid": "int",
            "Liquid": "float",
            "Inscription": "string",
            "Principle": "bool"
        }
        
        # Normalizar tipos (convertir alquímicos a tradicionales)
        tipo_esperado_norm = tipo_map.get(tipo_esperado, tipo_esperado)
        tipo_actual_norm = tipo_map.get(tipo_actual, tipo_actual)
        
        # Permitir "any" para funciones que aceptan cualquier tipo (como Transmute)
        if tipo_esperado_norm == "any" or tipo_actual_norm == "any":
            return True
        
        return tipo_esperado_norm == tipo_actual_norm
    
    def _es_numerico(self, nombre_tipo: str) -> bool:
        """verifica si un tipo es numerico (int, float, Solid, Liquid)"""
        tipo_map = {
            "Solid": "int",
            "Liquid": "float"
        }
        tipo_norm = tipo_map.get(nombre_tipo, nombre_tipo)
        return tipo_norm in ["int", "float"]
    
    def _obtener_tipo_resultado_numerico(self, tipo_izquierdo: str, tipo_derecho: str) -> str:
        """
        decide que tipo devolver cuando operamos con numeros
        si uno es float/Liquid, el resultado es float
        si ambos son int/Solid, el resultado es int
        """
        tipo_map = {
            "Solid": "int",
            "Liquid": "float"
        }
        tipo_izq_norm = tipo_map.get(tipo_izquierdo, tipo_izquierdo)
        tipo_der_norm = tipo_map.get(tipo_derecho, tipo_derecho)
        
        if tipo_izq_norm == "float" or tipo_der_norm == "float":
            # Devolver el tipo original si era alquímico
            if tipo_izquierdo == "Liquid" or tipo_derecho == "Liquid":
                return "Liquid"
            return "float"
        # Devolver el tipo original si era alquímico
        if tipo_izquierdo == "Solid" or tipo_derecho == "Solid":
            return "Solid"
        return "int"


def main():
    """funcion para probar el analizador semantico"""
    from .lexer import AlchemistLexer
    from .parser import AlchemistParser
    
    # codigo de prueba que tiene errores a proposito
    codigo_prueba = '''
    func main() -> void {
        int edad = 25
        string nombre = "Juan"
        
        // error: la condicion no es booleana
        if (edad) {
            print("Eres mayor de edad")
        }
        
        // error: variable no declarada
        altura = 1.75
        
        // error: tipos incompatibles
        edad = "treinta"
    }
    
    func calcular(int a, int b) -> int {
        // error: no tiene return y deberia
    }
    
    // error: funcion duplicada
    func calcular(float x) -> float {
        return x * 2.0
    }
    '''
    
    try:
        # analisis lexico
        lexer = AlchemistLexer()
        
        # analisis sintactico  
        parser = AlchemistParser()
        arbol = parser.parse(codigo_prueba)
        
        # analisis semantico
        analizador = AlchemistSemanticAnalyzer()
        errores = analizador.analyze(arbol)
        
        print("🔍 ANALISIS SEMANTICO TERMINADO")
        print("=" * 50)
        
        if errores:
            print(f"❌ Se encontraron {len(errores)} errores:")
            for error in errores:
                print(f"  • {error}")
        else:
            print("✅ Todo bien, no hay errores semanticos!")
            
    except Exception as error:
        print(f"❌ Algo salio mal: {error}")


if __name__ == "__main__":
    main()
