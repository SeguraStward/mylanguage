#!/usr/bin/env python3
"""
Tutorial específico: Cómo funciona la traducción AST → Bytecode
"""

def explain_ast_to_bytecode():
    """Explica paso a paso la traducción"""
    
    print("🔄 TRADUCCIÓN AST → BYTECODE")
    print("=" * 50)
    
    examples = [
        {
            "title": "1️⃣ LITERAL",
            "code": "42",
            "ast": "Literal(value=42)",
            "bytecode": ["LOAD_CONST 42"],
            "explanation": "Un literal se traduce directamente a LOAD_CONST"
        },
        
        {
            "title": "2️⃣ VARIABLE",
            "code": "x",
            "ast": "Variable(name='x')",
            "bytecode": ["LOAD 0  // Assuming x is at address 0"],
            "explanation": "Una variable se traduce a LOAD con su dirección"
        },
        
        {
            "title": "3️⃣ OPERACIÓN BINARIA",
            "code": "a + b",
            "ast": "BinaryOperation(left=Variable('a'), op='+', right=Variable('b'))",
            "bytecode": [
                "LOAD 0    // Cargar variable 'a'",
                "LOAD 1    // Cargar variable 'b'", 
                "ADD       // Sumar valores del tope de la pila"
            ],
            "explanation": "Se cargan operandos en pila, luego se ejecuta operación"
        },
        
        {
            "title": "4️⃣ ASIGNACIÓN",
            "code": "x = 10",
            "ast": "Assignment(target='x', value=Literal(10))",
            "bytecode": [
                "LOAD_CONST 10  // Cargar valor",
                "STORE 0        // Guardar en dirección de x"
            ],
            "explanation": "Se evalúa la expresión, luego se guarda en memoria"
        },
        
        {
            "title": "5️⃣ DECLARACIÓN DE VARIABLE",
            "code": "int y = 5 + 3",
            "ast": "VariableDeclaration(name='y', value=BinaryOperation(...))",
            "bytecode": [
                "LOAD_CONST 5   // Cargar primer operando",
                "LOAD_CONST 3   // Cargar segundo operando",
                "ADD            // Realizar suma",
                "STORE 1        // Guardar en dirección de y"
            ],
            "explanation": "Se evalúa expresión compleja, se asigna dirección, se guarda"
        },
        
        {
            "title": "6️⃣ LLAMADA A FUNCIÓN",
            "code": "print(x)",
            "ast": "FunctionCall(name='print', args=[Variable('x')])",
            "bytecode": [
                "LOAD 0         // Cargar argumento x",
                "CALL print 1   // Llamar print con 1 argumento"
            ],
            "explanation": "Se cargan argumentos en pila, luego se hace CALL"
        },
        
        {
            "title": "7️⃣ CONDICIONAL",
            "code": "if (x > 5) { ... }",
            "ast": "IfStatement(condition=BinaryOperation(...), then_block=[...])",
            "bytecode": [
                "LOAD 0              // Cargar x",
                "LOAD_CONST 5        // Cargar 5",
                "GT                  // x > 5",
                "JUMP_IF_FALSE L1    // Si falso, saltar",
                "... // código del then",
                "LABEL L1            // Etiqueta de fin"
            ],
            "explanation": "Se evalúa condición, se salta condicionalmente"
        }
    ]
    
    for example in examples:
        print(f"\n{example['title']}")
        print("─" * 30)
        print(f"CÓDIGO: {example['code']}")
        print(f"AST:    {example['ast']}")
        print("BYTECODE:")
        for instr in example['bytecode']:
            print(f"  {instr}")
        print(f"CÓMO:   {example['explanation']}")

def show_vm_architecture():
    """Muestra la arquitectura de la VM"""
    
    print("\n\n🖥️ ARQUITECTURA DE LA MÁQUINA VIRTUAL")
    print("=" * 50)
    
    print("""
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│   INSTRUCTION   │  │      STACK      │  │     MEMORY      │
│    POINTER      │  │   (operandos)   │  │   (variables)   │
│                 │  │                 │  │                 │
│   IP = 5        │  │  [30]  ← top    │  │  [0] = 10 (x)   │
│                 │  │  [20]           │  │  [1] = 20 (y)   │
│                 │  │  [10]           │  │  [2] = 30 (sum) │
│                 │  │                 │  │  [3] = ...      │
└─────────────────┘  └─────────────────┘  └─────────────────┘
         │                     │                     │
         ▼                     ▼                     ▼
┌─────────────────────────────────────────────────────────────┐
│                    INSTRUCCIONES                            │
│  0: CALL main 0                                             │
│  1: HALT                                                    │
│  2: LABEL main                                              │
│  3: ENTER 0                                                 │
│  4: LOAD_CONST 10                                           │
│  5: STORE 0        ← IP apunta aquí                         │
│  6: LOAD_CONST 20                                           │
│  7: STORE 1                                                 │
│  8: ...                                                     │
└─────────────────────────────────────────────────────────────┘

FLUJO DE EJECUCIÓN:
1. IP apunta a la instrucción actual
2. Se decodifica la instrucción
3. Se ejecuta (manipulando stack/memory)
4. IP avanza a la siguiente instrucción
5. Repetir hasta HALT
    """)

if __name__ == "__main__":
    explain_ast_to_bytecode()
    show_vm_architecture()
