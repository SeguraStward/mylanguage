#!/usr/bin/env python3
"""
aurum Compiler - Compilador Principal
Integra todas las fases del proceso de compilación: léxico, sintáctico, semántico y generación de código
"""

from typing import List, Optional, Dict, Any
from dataclasses import dataclass

from .lexer import aurumLexer, LexerError
from .parser import aurumParser, ParseError
from .semantic_analyzer import aurumSemanticAnalyzer, SemanticError
from .code_generator import aurumCodeGenerator, CodeGeneratorError
from .interpreter import aurumInterpreter, RuntimeError


@dataclass
class CompilationResult:
    """Resultado de la compilación"""
    success: bool
    errors: List[str]
    warnings: List[str]
    instructions: Optional[List] = None
    variables: Optional[Dict[str, int]] = None
    functions: Optional[Dict[str, int]] = None
    output_file: Optional[str] = None


@dataclass
class ExecutionResult:
    """Resultado de la ejecución"""
    success: bool
    output: List[str]
    errors: List[str]
    execution_time: float = 0.0


class aurumCompiler:
    """Compilador principal para aurum"""
    
    def __init__(self):
        """Inicializa el compilador"""
        self.lexer = aurumLexer()
        self.parser = aurumParser()
        self.semantic_analyzer = aurumSemanticAnalyzer()
        self.code_generator = aurumCodeGenerator()
        self.interpreter = aurumInterpreter()
        
        # Estado del compilador
        self.verbose = False
        self.debug_mode = False
        self.optimize = True
    
    def set_verbose(self, verbose: bool) -> None:
        """Activa/desactiva modo verboso"""
        self.verbose = verbose
    
    def set_debug(self, debug: bool) -> None:
        """Activa/desactiva modo debug"""
        self.debug_mode = debug
    
    def set_optimization(self, optimize: bool) -> None:
        """Activa/desactiva optimizaciones"""
        self.optimize = optimize
    
    def compile(self, source_code: str, output_file: Optional[str] = None) -> CompilationResult:
        """
        Compila código fuente aurum
        
        Args:
            source_code: Código fuente a compilar
            output_file: Archivo donde guardar el código compilado (opcional)
            
        Returns:
            Resultado de la compilación
        """
        errors = []
        warnings = []
        
        if self.verbose:
            print("🔧 INICIANDO COMPILACIÓN")
            print("=" * 50)
        
        try:
            # FASE 1: ANÁLISIS LÉXICO
            if self.verbose:
                print("📝 Fase 1: Análisis Léxico...")
            
            tokens = self.lexer.tokenize(source_code)
            
            if self.verbose:
                token_count = len([t for t in tokens if t.type.name != 'NEWLINE'])
                print(f"   ✅ {token_count} tokens generados")
            
            if self.debug_mode:
                print("   🔍 Tokens encontrados:")
                for token in tokens[:10]:  # Mostrar solo los primeros 10
                    if token.type.name != 'NEWLINE':
                        print(f"      {token}")
                if len(tokens) > 10:
                    print(f"      ... y {len(tokens) - 10} más")
            
        except LexerError as e:
            errors.append(f"Error léxico: {e}")
            return CompilationResult(False, errors, warnings)
        
        try:
            # FASE 2: ANÁLISIS SINTÁCTICO
            if self.verbose:
                print("🌳 Fase 2: Análisis Sintáctico...")
            
            ast = self.parser.parse(source_code)
            
            if self.verbose:
                print(f"   ✅ AST generado con {len(ast.functions)} funciones")
            
            if self.debug_mode:
                print("   🔍 Funciones encontradas:")
                for func in ast.functions:
                    params = ', '.join(f'{p.type} {p.name}' for p in func.parameters)
                    print(f"      {func.name}({params}) -> {func.return_type}")
            
        except ParseError as e:
            errors.append(f"Error sintáctico: {e}")
            return CompilationResult(False, errors, warnings)
        
        try:
            # FASE 3: ANÁLISIS SEMÁNTICO
            if self.verbose:
                print("🔍 Fase 3: Análisis Semántico...")
            
            # Crear nuevo analizador semántico para cada compilación
            semantic_analyzer = aurumSemanticAnalyzer()
            semantic_errors = semantic_analyzer.analyze(ast)
            
            if semantic_errors:
                for error in semantic_errors:
                    errors.append(f"Error semántico: {error}")
                return CompilationResult(False, errors, warnings)
            
            if self.verbose:
                print("   ✅ Análisis semántico completado sin errores")
            
        except Exception as e:
            errors.append(f"Error en análisis semántico: {e}")
            return CompilationResult(False, errors, warnings)
        
        try:
            # FASE 4: GENERACIÓN DE CÓDIGO
            if self.verbose:
                print("⚙️ Fase 4: Generación de Código...")
            
            instructions = self.code_generator.generate(ast)
            
            if self.verbose:
                print(f"   ✅ {len(instructions)} instrucciones generadas")
                print(f"   📊 {len(self.code_generator.variables)} variables")
                print(f"   📊 {len(self.code_generator.functions)} funciones")
            
            if self.debug_mode:
                print("   🔍 Primeras 10 instrucciones:")
                for i, inst in enumerate(instructions[:10]):
                    print(f"      {i:3d}: {inst}")
                if len(instructions) > 10:
                    print(f"      ... y {len(instructions) - 10} más")
            
            # Guardar código compilado si se especifica archivo
            if output_file:
                self.code_generator.save_to_file(output_file)
                if self.verbose:
                    print(f"   💾 Código guardado en '{output_file}'")
            
        except CodeGeneratorError as e:
            errors.append(f"Error en generación de código: {e}")
            return CompilationResult(False, errors, warnings)
        
        if self.verbose:
            print("🎉 COMPILACIÓN EXITOSA!")
        
        return CompilationResult(
            success=True,
            errors=errors,
            warnings=warnings,
            instructions=instructions,
            variables=self.code_generator.variables,
            functions=self.code_generator.functions,
            output_file=output_file
        )
    
    def execute(self, compilation_result: CompilationResult, 
               input_data: Optional[List[str]] = None) -> ExecutionResult:
        """
        Ejecuta código compilado
        
        Args:
            compilation_result: Resultado de compilación exitosa
            input_data: Datos de entrada para el programa (opcional)
            
        Returns:
            Resultado de la ejecución
        """
        if not compilation_result.success:
            return ExecutionResult(
                success=False,
                output=[],
                errors=["No se puede ejecutar: compilación falló"]
            )
        
        if self.verbose:
            print("\n🚀 INICIANDO EJECUCIÓN")
            print("=" * 50)
        
        try:
            # Cargar programa en el intérprete
            self.interpreter.load_program(
                compilation_result.instructions,
                compilation_result.variables,
                compilation_result.functions
            )
            
            # Establecer entrada si se proporciona
            if input_data:
                self.interpreter.set_input(input_data)
                if self.verbose:
                    print(f"📥 Entrada configurada: {len(input_data)} líneas")
            
            # Ejecutar programa
            import time
            start_time = time.time()
            
            output = self.interpreter.execute()
            
            execution_time = time.time() - start_time
            
            if self.verbose:
                print(f"✅ Ejecución completada en {execution_time:.3f}s")
                print(f"📄 Salida generada: {len(output)} líneas")
            
            return ExecutionResult(
                success=True,
                output=output,
                errors=[],
                execution_time=execution_time
            )
            
        except RuntimeError as e:
            return ExecutionResult(
                success=False,
                output=self.interpreter.get_output(),
                errors=[f"Error de ejecución: {e}"]
            )
        except Exception as e:
            return ExecutionResult(
                success=False,
                output=[],
                errors=[f"Error interno durante ejecución: {e}"]
            )
    
    def compile_and_run(self, source_code: str, 
                       input_data: Optional[List[str]] = None,
                       output_file: Optional[str] = None) -> tuple[CompilationResult, ExecutionResult]:
        """
        Compila y ejecuta código en una sola operación
        
        Args:
            source_code: Código fuente a compilar y ejecutar
            input_data: Datos de entrada para el programa
            output_file: Archivo donde guardar código compilado
            
        Returns:
            Tupla con resultado de compilación y ejecución
        """
        compilation_result = self.compile(source_code, output_file)
        
        if compilation_result.success:
            execution_result = self.execute(compilation_result, input_data)
        else:
            execution_result = ExecutionResult(
                success=False,
                output=[],
                errors=["Ejecución cancelada por errores de compilación"]
            )
        
        return compilation_result, execution_result
    
    def get_language_info(self) -> Dict[str, Any]:
        """
        Retorna información sobre el lenguaje aurum
        
        Returns:
            Diccionario con información del lenguaje
        """
        return {
            "name": "aurum",
            "version": "1.0",
            "description": "Lenguaje de programación educativo con sintaxis similar a Go",
            "features": [
                "Tipado estático con inferencia",
                "Funciones con tipos de retorno",
                "Estructuras de control completas",
                "Operaciones aritméticas y lógicas",
                "Entrada/salida de datos",
                "Sintaxis sin punto y coma"
            ],
            "data_types": {
                "simple": ["int", "float", "string", "bool"],
                "composite": ["array", "list"]
            },
            "keywords": [
                "func", "main", "return", "if", "else", "elif",
                "while", "for", "break", "continue", "and", "or", "not",
                "read", "write", "print", "true", "false"
            ],
            "operators": {
                "arithmetic": ["+", "-", "*", "/", "%"],
                "comparison": ["==", "!=", "<", ">", "<=", ">="],
                "logical": ["and", "or", "not"],
                "assignment": ["="]
            }
        }


def main():
    """Función principal de demostración"""
    # Crear compilador
    compiler = aurumCompiler()
    compiler.set_verbose(True)
    compiler.set_debug(True)
    
    # Código de ejemplo
    example_code = '''
    func main() -> void {
        print("¡Hola, aurum!")
        
        int a = 15
        int b = 25
        int suma = a + b
        
        print("Los números son: " + a + " y " + b)
        print("Su suma es: " + suma)
        
        if (suma > 30) {
            print("La suma es mayor a 30")
        } else {
            print("La suma es menor o igual a 30")
        }
        
        int factorial_5 = factorial(5)
        print("El factorial de 5 es: " + factorial_5)
    }
    
    func factorial(int n) -> int {
        if (n <= 1) {
            return 1
        } else {
            return n * factorial(n - 1)
        }
    }
    '''
    
    print("🌟 DEMOSTRACIÓN DEL COMPILADOR aurum")
    print("=" * 60)
    
    # Compilar y ejecutar
    compilation_result, execution_result = compiler.compile_and_run(
        example_code, 
        output_file="ejemplo.auro"
    )
    
    # Mostrar resultados
    print("\n📊 RESULTADOS DE COMPILACIÓN:")
    print("=" * 40)
    
    if compilation_result.success:
        print("✅ Compilación exitosa")
    else:
        print("❌ Errores de compilación:")
        for error in compilation_result.errors:
            print(f"   • {error}")
    
    print("\n📊 RESULTADOS DE EJECUCIÓN:")
    print("=" * 40)
    
    if execution_result.success:
        print("✅ Ejecución exitosa")
        print(f"⏱️ Tiempo: {execution_result.execution_time:.3f}s")
        
        print("\n📄 SALIDA DEL PROGRAMA:")
        print("-" * 30)
        for line in execution_result.output:
            print(line)
    else:
        print("❌ Errores de ejecución:")
        for error in execution_result.errors:
            print(f"   • {error}")
        
        if execution_result.output:
            print("\n📄 Salida parcial:")
            for line in execution_result.output:
                print(line)
    
    # Mostrar información del lenguaje
    print(f"\n📚 INFORMACIÓN DEL LENGUAJE:")
    print("=" * 40)
    
    info = compiler.get_language_info()
    print(f"Nombre: {info['name']} v{info['version']}")
    print(f"Descripción: {info['description']}")
    print(f"Tipos de datos: {', '.join(info['data_types']['simple'])}")
    print(f"Características principales: {len(info['features'])} implementadas")


if __name__ == "__main__":
    main()
