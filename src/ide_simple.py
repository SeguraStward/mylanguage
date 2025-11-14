#!/usr/bin/env python3
import tkinter as tk
from tkinter import scrolledtext, messagebox, font, simpledialog
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.compiler import AlchemistCompiler

class AlchemistIDESimple:
    # Palabras reservadas para sugerencias
    PALABRAS_RESERVADAS = [
        "GateOfTruth", "Solid", "Liquid", "Inscription", "Principle", "Emptiness",
        "Observe", "Alternatively", "Inevitably", "AlchemicCycle", "TransmuteUntil",
        "Transmute", "TransmuteLine", "Absorb", "AbsorbSolid", "AbsorbLiquid", 
        "AbsorbPrinciple", "Accepted", "Rejected", "Transmutation", "EquivalentExchange",
        "range", "and", "or", "not", "void"
    ]
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Alchemist IDE")
        self.root.geometry("1200x700")
        self.compiler = AlchemistCompiler()
        self.compilation_result = None
        
        # Colores modo oscuro
        self.bg_dark = '#1e1e1e'
        self.fg_light = '#d4d4d4'
        self.editor_bg = '#1e1e1e'
        self.editor_fg = '#d4d4d4'
        self.line_number_bg = '#2d2d2d'
        self.line_number_fg = '#858585'
        self.output_bg = '#1e1e1e'
        self.button_bg = '#2d2d2d'
        self.button_fg = '#d4d4d4'
        self.button_active = '#3e3e3e'
        
        self.setup_ui()

    def setup_ui(self):
        self.root.configure(bg=self.bg_dark)
        
        # Menú superior
        menu_frame = tk.Frame(self.root, bg=self.bg_dark, height=30)
        menu_frame.pack(fill=tk.X, padx=5, pady=5)
        tk.Button(menu_frame, text="Nuevo", command=self.nuevo, bg=self.button_bg, fg=self.button_fg, 
                 activebackground=self.button_active, relief=tk.FLAT, padx=10, font=('Arial', 9)).pack(side=tk.LEFT, padx=2)
        tk.Button(menu_frame, text="Plantillas", command=self.mostrar_plantillas, bg=self.button_bg, fg=self.button_fg,
                 activebackground=self.button_active, relief=tk.FLAT, padx=10, font=('Arial', 9)).pack(side=tk.LEFT, padx=2)
        tk.Button(menu_frame, text="Opciones", command=self.opciones, bg=self.button_bg, fg=self.button_fg,
                 activebackground=self.button_active, relief=tk.FLAT, padx=10, font=('Arial', 9)).pack(side=tk.LEFT, padx=2)
        tk.Button(menu_frame, text="Salir", command=self.salir, bg=self.button_bg, fg=self.button_fg,
                 activebackground=self.button_active, relief=tk.FLAT, padx=10, font=('Arial', 9)).pack(side=tk.LEFT, padx=2)
        
        # Frame principal
        main_frame = tk.Frame(self.root, bg=self.bg_dark)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Panel izquierdo (editor con números de línea)
        left_frame = tk.Frame(main_frame, bg=self.bg_dark, relief=tk.SOLID, bd=1)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        # Frame para números de línea y editor
        editor_container = tk.Frame(left_frame, bg=self.editor_bg)
        editor_container.pack(fill=tk.BOTH, expand=True)
        
        # Text widget para números de línea
        self.line_numbers = tk.Text(editor_container, width=4, font=('Courier', 10), 
                                    bg=self.line_number_bg, fg=self.line_number_fg,
                                    state=tk.DISABLED, relief=tk.FLAT, bd=0, padx=5, pady=5,
                                    takefocus=0, cursor='arrow')
        self.line_numbers.pack(side=tk.LEFT, fill=tk.Y)
        
        # Editor de código
        self.code_editor = scrolledtext.ScrolledText(editor_container, font=('Courier', 10), 
                                                     bg=self.editor_bg, fg=self.editor_fg, 
                                                     wrap=tk.NONE, relief=tk.FLAT, bd=0, 
                                                     padx=5, pady=5, insertbackground=self.editor_fg)
        self.code_editor.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Vincular eventos para actualizar números de línea
        self.code_editor.bind('<KeyRelease>', self.on_code_change)
        self.code_editor.bind('<ButtonRelease>', self.update_line_numbers)
        self.code_editor.bind('<MouseWheel>', self.on_scroll)
        self.code_editor.bind('<Configure>', self.update_line_numbers)
        
        # Sincronizar scroll
        self.code_editor.config(yscrollcommand=self.on_editor_scroll)
        
        # Panel derecho (output)
        right_frame = tk.Frame(main_frame, bg=self.bg_dark, width=400)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, padx=(5, 0))
        right_frame.pack_propagate(False)
        
        tk.Label(right_frame, text="OUTPUT", font=('Arial', 10, 'bold'), 
                bg=self.bg_dark, fg=self.fg_light, anchor='w').pack(fill=tk.X, pady=(0, 5))
        
        output_container = tk.Frame(right_frame, bg=self.output_bg, relief=tk.SOLID, bd=1)
        output_container.pack(fill=tk.BOTH, expand=True)
        
        self.output_text = scrolledtext.ScrolledText(output_container, font=('Courier', 9), 
                                                     bg=self.output_bg, fg=self.fg_light, 
                                                     relief=tk.FLAT, bd=0, padx=5, pady=5, 
                                                     state=tk.DISABLED, insertbackground=self.fg_light)
        self.output_text.pack(fill=tk.BOTH, expand=True)
        
        button_frame = tk.Frame(right_frame, bg=self.bg_dark)
        button_frame.pack(fill=tk.X, pady=(5, 0))
        tk.Button(button_frame, text="COMPILAR", command=self.compilar, bg=self.button_bg, fg=self.button_fg,
                 activebackground=self.button_active, relief=tk.SOLID, bd=1, padx=20, pady=5, 
                 font=('Arial', 9, 'bold')).pack(side=tk.LEFT, padx=(0, 5))
        tk.Button(button_frame, text="EJECUTAR", command=self.ejecutar, bg=self.button_bg, fg=self.button_fg,
                 activebackground=self.button_active, relief=tk.SOLID, bd=1, padx=20, pady=5, 
                 font=('Arial', 9, 'bold')).pack(side=tk.LEFT)
        
        # Inicializar números de línea
        self.update_line_numbers()
    
    def on_editor_scroll(self, *args):
        """Sincronizar scroll de números de línea con editor"""
        self.line_numbers.yview_moveto(args[0])
    
    def on_scroll(self, event):
        """Manejar scroll con rueda del mouse"""
        self.update_line_numbers()
    
    def on_code_change(self, event=None):
        """
        Callback cuando el usuario modifica el código.
        Invalida el resultado de compilación para forzar recompilación.
        """
        # Invalidar resultado de compilación anterior
        if self.compilation_result is not None:
            self.compilation_result = None
        
        # Actualizar números de línea
        self.update_line_numbers(event)
    
    def update_line_numbers(self, event=None):
        """Actualizar números de línea"""
        # Obtener contenido del editor
        line_count = self.code_editor.get('1.0', tk.END).count('\n')
        
        # Generar números de línea
        line_numbers_string = '\n'.join(str(i) for i in range(1, line_count + 1))
        
        # Actualizar widget de números
        self.line_numbers.config(state=tk.NORMAL)
        self.line_numbers.delete('1.0', tk.END)
        self.line_numbers.insert('1.0', line_numbers_string)
        self.line_numbers.config(state=tk.DISABLED)
        
        # Sincronizar posición de scroll
        self.line_numbers.yview_moveto(self.code_editor.yview()[0])
    
    def nuevo(self):
        if messagebox.askyesno("Nuevo", "¿Crear nuevo archivo?"):
            self.code_editor.delete('1.0', tk.END)
            self.clear_output()
            self.update_line_numbers()
            # Invalidar compilación al crear nuevo archivo
            self.compilation_result = None

    def mostrar_plantillas(self):
        """Muestra ventana con plantillas de código para insertar rápidamente"""
        win = tk.Toplevel(self.root)
        win.title("Plantillas de Código")
        win.geometry("700x600")
        win.configure(bg=self.bg_dark)
        win.transient(self.root)
        
        tk.Label(win, text="Plantillas de Código Rápido", font=('Arial', 14, 'bold'), 
                bg=self.bg_dark, fg=self.fg_light).pack(pady=15)
        
        tk.Label(win, text="Haz clic en cualquier plantilla para insertarla en el editor", 
                font=('Arial', 9), bg=self.bg_dark, fg=self.line_number_fg).pack(pady=5)
        
        # Frame con scroll para las plantillas
        canvas = tk.Canvas(win, bg=self.bg_dark, highlightthickness=0)
        scrollbar = tk.Scrollbar(win, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=self.bg_dark)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True, padx=20, pady=10)
        scrollbar.pack(side="right", fill="y")
        
        # Definir plantillas
        plantillas = [
            ("Programa Principal", self.insertar_main),
            ("Condicional Simple", self.insertar_if_simple),
            ("Condicional con Else", self.insertar_if_else),
            ("Ciclo While", self.insertar_while),
            ("Ciclo For", self.insertar_for),
            ("Función con Retorno", self.insertar_funcion),
            ("Función Void", self.insertar_funcion_void),
            ("Array", self.insertar_array),
            ("Matriz", self.insertar_matriz),
            ("Entrada de Datos", self.insertar_input),
            ("Salida de Datos", self.insertar_output),
        ]
        
        for i, (nombre, comando) in enumerate(plantillas):
            btn = tk.Button(scrollable_frame, text=f"📄 {nombre}", command=lambda c=comando, w=win: self.ejecutar_plantilla(c, w),
                          bg=self.button_bg, fg=self.button_fg, activebackground=self.button_active,
                          font=('Arial', 10), relief=tk.SOLID, bd=1, padx=20, pady=10, anchor='w')
            btn.pack(fill=tk.X, pady=5, padx=10)
        
        # Botón cerrar
        tk.Button(win, text="Cerrar", command=win.destroy,
                 bg=self.button_bg, fg=self.button_fg, activebackground=self.button_active,
                 font=('Arial', 10), relief=tk.SOLID, bd=1, padx=20, pady=8).pack(pady=10)

    def ejecutar_plantilla(self, comando, ventana):
        """Ejecuta el comando de plantilla y cierra la ventana"""
        comando()
        ventana.destroy()
        messagebox.showinfo("Plantilla Insertada", "El código ha sido insertado en el editor")

    def opciones(self):
        """Menú principal de opciones"""
        win = tk.Toplevel(self.root)
        win.title("Menú de Ayuda")
        win.geometry("600x500")
        win.configure(bg=self.bg_dark)
        
        tk.Label(win, text="Menú de Ayuda - Alchemist", font=('Arial', 14, 'bold'), 
                bg=self.bg_dark, fg=self.fg_light).pack(pady=15)
        
        button_frame = tk.Frame(win, bg=self.bg_dark)
        button_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        buttons = [
            ("Ejemplos Rapidos", self.mostrar_ejemplos_rapidos),
            ("Palabras Reservadas", self.mostrar_palabras_reservadas),
            ("Sintaxis", self.mostrar_sintaxis),
            ("Semantica", self.mostrar_semantica),
            ("Tipos de Datos", self.mostrar_tipos_datos)
        ]
        
        for text, command in buttons:
            tk.Button(button_frame, text=text, command=command, 
                     bg=self.button_bg, fg=self.button_fg,
                     activebackground=self.button_active, font=('Arial', 11),
                     relief=tk.SOLID, bd=1, padx=20, pady=10).pack(fill=tk.X, pady=5)
    
    def mostrar_ejemplos_rapidos(self):
        """Muestra menú de ejemplos rápidos para insertar"""
        win = tk.Toplevel(self.root)
        win.title("Ejemplos Rapidos")
        win.geometry("700x600")
        win.configure(bg=self.bg_dark)
        
        tk.Label(win, text="Ejemplos Rapidos - Selecciona uno para insertar", 
                font=('Arial', 12, 'bold'), 
                bg=self.bg_dark, fg=self.fg_light).pack(pady=15)
        
        button_frame = tk.Frame(win, bg=self.bg_dark)
        button_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        ejemplos = [
            ("1. Hola Mundo", self.ejemplo_hola_mundo),
            ("2. Calculadora Basica", self.ejemplo_calculadora),
            ("3. Fibonacci", self.ejemplo_fibonacci),
            ("4. Factorial Recursivo", self.ejemplo_factorial),
            ("5. Arrays y Ciclos", self.ejemplo_arrays)
        ]
        
        for text, command in ejemplos:
            btn = tk.Button(button_frame, text=text, command=lambda c=command, w=win: self.ejecutar_ejemplo(c, w), 
                           bg=self.button_bg, fg=self.button_fg,
                           activebackground=self.button_active, font=('Arial', 11),
                           relief=tk.SOLID, bd=1, padx=20, pady=10)
            btn.pack(fill=tk.X, pady=5)
    
    def ejecutar_ejemplo(self, ejemplo_func, ventana):
        """Ejecuta la función de ejemplo y cierra la ventana"""
        ventana.destroy()
        ejemplo_func()
    
    def ejemplo_hola_mundo(self):
        """Ejemplo 1: Hola Mundo básico"""
        codigo = """// Ejemplo 1: Hola Mundo
Transmutation GateOfTruth() -> void {
    TransmuteLine("Hola Mundo")
    TransmuteLine("Bienvenido a Alchemist")
}
"""
        self.insertar_codigo(codigo)
    
    def ejemplo_calculadora(self):
        """Ejemplo 2: Calculadora básica"""
        codigo = """// Ejemplo 2: Calculadora Basica
Transmutation GateOfTruth() -> void {
    Solid a = 10
    Solid b = 3
    
    Transmute("Suma: ")
    TransmuteLine(a + b)
    
    Transmute("Resta: ")
    TransmuteLine(a - b)
    
    Transmute("Multiplicacion: ")
    TransmuteLine(a * b)
    
    Transmute("Division: ")
    TransmuteLine(a / b)
    
    Transmute("Modulo: ")
    TransmuteLine(a % b)
}
"""
        self.insertar_codigo(codigo)
    
    def ejemplo_fibonacci(self):
        """Ejemplo 3: Serie de Fibonacci"""
        codigo = """// Ejemplo 3: Serie de Fibonacci
Transmutation fibonacci(Solid n) -> Solid {
    Observe (n <= 1) {
        EquivalentExchange n
    }
    EquivalentExchange fibonacci(n - 1) + fibonacci(n - 2)
}

Transmutation GateOfTruth() -> void {
    TransmuteLine("Serie de Fibonacci (primeros 10 numeros):")
    
    AlchemicCycle (Solid i = 0; i < 10; i = i + 1) {
        Solid resultado = fibonacci(i)
        Transmute("fib(")
        Transmute(i)
        Transmute(") = ")
        TransmuteLine(resultado)
    }
}
"""
        self.insertar_codigo(codigo)
    
    def ejemplo_factorial(self):
        """Ejemplo 4: Factorial recursivo"""
        codigo = """// Ejemplo 4: Factorial Recursivo
Transmutation factorial(Solid n) -> Solid {
    Observe (n <= 1) {
        EquivalentExchange 1
    }
    EquivalentExchange n * factorial(n - 1)
}

Transmutation GateOfTruth() -> void {
    TransmuteLine("Calculo de Factoriales:")
    
    AlchemicCycle (Solid i = 1; i <= 10; i = i + 1) {
        Solid resultado = factorial(i)
        Transmute("factorial(")
        Transmute(i)
        Transmute(") = ")
        TransmuteLine(resultado)
    }
}
"""
        self.insertar_codigo(codigo)
    
    def ejemplo_arrays(self):
        """Ejemplo 5: Arrays y ciclos"""
        codigo = """// Ejemplo 5: Arrays y Ciclos
Transmutation GateOfTruth() -> void {
    AlchemicArray[Solid, 5] numeros = [10, 20, 30, 40, 50]
    
    TransmuteLine("Elementos del array:")
    AlchemicCycle (Solid i = 0; i < 5; i = i + 1) {
        Transmute("numeros[")
        Transmute(i)
        Transmute("] = ")
        TransmuteLine(numeros[i])
    }
    
    Solid suma = 0
    AlchemicCycle (Solid i = 0; i < 5; i = i + 1) {
        suma = suma + numeros[i]
    }
    
    Transmute("Suma total: ")
    TransmuteLine(suma)
}
"""
        self.insertar_codigo(codigo)
    
    def mostrar_palabras_reservadas(self):
        """Muestra todas las palabras reservadas del lenguaje"""
        win = tk.Toplevel(self.root)
        win.title("Palabras Reservadas")
        win.geometry("700x600")
        win.configure(bg=self.bg_dark)
        
        tk.Label(win, text="Palabras Reservadas de Alchemist", font=('Arial', 12, 'bold'), 
                bg=self.bg_dark, fg=self.fg_light).pack(pady=10)
        
        frame = tk.Frame(win, bg=self.bg_dark)
        frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        txt = tk.Text(frame, font=('Courier', 10), bg=self.editor_bg, fg=self.editor_fg,
                     relief=tk.SOLID, bd=1, padx=10, pady=10, wrap=tk.WORD)
        txt.pack(fill=tk.BOTH, expand=True)
        
        content = """TIPOS DE DATOS:
• Solid          - Entero (int)
• Liquid         - Flotante (float)
• Inscription    - Cadena (string)
• Principle      - Booleano (bool)
• Emptiness      - Valor nulo

ESTRUCTURAS DE CONTROL:
• Observe           - if (condicional simple)
• Alternatively     - else if (condicional múltiple)
• Inevitably        - else (alternativa final)
• AlchemicCycle     - for (ciclo con rango)
• TransmuteUntil    - while (ciclo condicional)

OPERADORES:
• +, -, *, /, %     - Aritméticos
• ==, !=, <, >, <=, >= - Comparación
• and, or, not      - Lógicos

ENTRADA/SALIDA:
• Transmute         - Imprimir sin salto de línea
• TransmuteLine     - Imprimir con salto de línea
• Absorb            - Leer cadena
• AbsorbSolid       - Leer entero
• AbsorbLiquid      - Leer flotante
• AbsorbPrinciple   - Leer booleano

VALORES:
• Accepted       - true
• Rejected       - false

FUNCIONES:
• Transmutation     - Declarar función
• EquivalentExchange - return (retornar valor)
• GateOfTruth()     - Función principal (main)"""
        
        txt.insert('1.0', content)
        txt.config(state=tk.DISABLED)
    
    def mostrar_sintaxis(self):
        """Muestra submenú de sintaxis"""
        win = tk.Toplevel(self.root)
        win.title("Sintaxis")
        win.geometry("600x400")
        win.configure(bg=self.bg_dark)
        
        tk.Label(win, text="Sintaxis del Lenguaje", font=('Arial', 12, 'bold'), 
                bg=self.bg_dark, fg=self.fg_light).pack(pady=15)
        
        button_frame = tk.Frame(win, bg=self.bg_dark)
        button_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        buttons = [
            ("Control (if/else, while, for)", self.mostrar_sintaxis_control),
            ("Funciones", self.mostrar_sintaxis_funciones),
            ("Operaciones", self.mostrar_sintaxis_operaciones)
        ]
        
        for text, command in buttons:
            tk.Button(button_frame, text=text, command=command, 
                     bg=self.button_bg, fg=self.button_fg,
                     activebackground=self.button_active, font=('Arial', 10),
                     relief=tk.SOLID, bd=1, padx=15, pady=8).pack(fill=tk.X, pady=5)
    
    def mostrar_sintaxis_control(self):
        """Muestra sintaxis de estructuras de control"""
        self._mostrar_ayuda_con_codigo(
            "Estructuras de Control",
            """CONDICIONALES (Observe):

Sintaxis:
  Observe (condicion) {
      // codigo si verdadero
  } Alternatively (condicion2) {
      // codigo si condicion2
  } Inevitably {
      // codigo si todas son falsas
  }

CICLO FOR (AlchemicCycle):

Sintaxis:
  AlchemicCycle (Solid i = 0; i < limite; i = i + 1) {
      // codigo que se repite
  }

CICLO WHILE (TransmuteUntil):

Sintaxis:
  TransmuteUntil (condicion) {
      // codigo mientras condicion sea verdadera
  }
""",
            """// Ejemplo: Estructuras de Control
Transmutation GateOfTruth() -> void {
    Solid edad = 20
    
    // Condicional
    Observe (edad < 18) {
        TransmuteLine("Menor de edad")
    } Alternatively (edad < 65) {
        TransmuteLine("Adulto")
    } Inevitably {
        TransmuteLine("Adulto mayor")
    }
    
    // Ciclo for
    TransmuteLine("Contando del 0 al 4:")
    AlchemicCycle (Solid i = 0; i < 5; i = i + 1) {
        TransmuteLine(i)
    }
    
    // Ciclo while
    Solid contador = 0
    TransmuteUntil (contador < 3) {
        TransmuteLine(contador)
        contador = contador + 1
    }
}
"""
        )
    
    def mostrar_sintaxis_funciones(self):
        """Muestra sintaxis de funciones"""
        self._mostrar_ayuda_con_codigo(
            "Funciones",
            """DECLARACIÓN DE FUNCIONES:

Sintaxis:
  Transmutation nombre_funcion(parametros) -> TipoRetorno {
      // codigo de la funcion
      EquivalentExchange valor_retorno
  }

FUNCIÓN PRINCIPAL:

  Transmutation GateOfTruth() -> void {
      // codigo principal del programa
  }

LLAMADA A FUNCIONES:

Sintaxis:
  resultado = nombre_funcion(argumentos)

TIPOS DE FUNCIONES:
• Con retorno: especifica tipo despues de ->
  Ejemplo: -> Solid, -> Liquid, -> Inscription, -> Principle
• Sin retorno (void): usan -> void
""",
            """// Ejemplo: Funciones
Transmutation GateOfTruth() -> void {
    Solid total = suma(5, 3)
    TransmuteLine("La suma es: " + total)
    
    saludar("Alchemist")
    
    Solid area = calcularArea(10, 20)
    TransmuteLine("Area: " + area)
}

Transmutation suma(Solid a, Solid b) -> Solid {
    EquivalentExchange a + b
}

Transmutation saludar(Inscription nombre) -> void {
    TransmuteLine("Hola, " + nombre)
}

Transmutation calcularArea(Solid base, Solid altura) -> Solid {
    EquivalentExchange base * altura
}
"""
        )
    
    def mostrar_sintaxis_operaciones(self):
        """Muestra sintaxis de operaciones"""
        self._mostrar_ayuda_con_codigo(
            "Operaciones",
            """OPERADORES ARITMÉTICOS:
  +    Suma
  -    Resta
  *    Multiplicación
  /    División
  %    Módulo (residuo)

OPERADORES DE COMPARACIÓN:
  ==   Igual a
  !=   Diferente de
  <    Menor que
  >    Mayor que
  <=   Menor o igual
  >=   Mayor o igual

OPERADORES LÓGICOS:
  and  Y lógico (ambos verdaderos)
  or   O lógico (al menos uno verdadero)
  not  Negación lógica
""",
            """// Ejemplo: Operaciones
Transmutation GateOfTruth() -> void {
    Solid a = 10
    Solid b = 3
    
    // Aritmeticas
    TransmuteLine("Suma: " + (a + b))
    TransmuteLine("Resta: " + (a - b))
    TransmuteLine("Multiplicacion: " + (a * b))
    TransmuteLine("Division: " + (a / b))
    TransmuteLine("Modulo: " + (a % b))
    
    // Comparacion
    TransmuteLine("10 == 3: " + (a == b))
    TransmuteLine("10 > 3: " + (a > b))
    TransmuteLine("10 <= 3: " + (a <= b))
    
    // Logicas
    Principle x = Accepted
    Principle y = Rejected
    TransmuteLine("Accepted and Rejected: " + (x and y))
    TransmuteLine("Accepted or Rejected: " + (x or y))
    TransmuteLine("not Accepted: " + (not x))
}
"""
        )
    
    def mostrar_semantica(self):
        """Muestra cómo funciona el lenguaje"""
        self._mostrar_ayuda_con_codigo(
            "Semántica del Lenguaje",
            """ESTRUCTURA DE UN PROGRAMA:

Todo programa debe tener una función principal:
  Transmutation GateOfTruth() -> void {
      // tu codigo aqui
  }

REGLAS IMPORTANTES:

1. LLAVES OBLIGATORIAS:
   • Usa { } para delimitar bloques de codigo
   • Condicionales, ciclos y funciones requieren llaves

2. PUNTO Y COMA:
   • Opcional al final de cada instruccion
   
3. DECLARACIÓN DE VARIABLES:
   • Siempre especifica el tipo: Solid, Liquid, Inscription, Principle
   • Sintaxis: TipoDato nombre = valor

4. COMENTARIOS:
   • Usa // para comentarios de una linea
   • Usa /* */ para comentarios multilinea

5. ARRAYS Y MATRICES:
   • Arrays: AlchemicArray[Tipo, Tamaño] nombre
   • Matrices: AlchemicMatrix[Tipo, Filas, Columnas] nombre

6. PROMOCIÓN DE TIPOS:
   • Solid puede asignarse a Liquid (int a float)
   • Emptiness es compatible con todos los tipos

7. LÍMITE DE RECURSIÓN:
   • Maximo 1000 llamadas recursivas
""",
            """// Ejemplo: Programa Completo
Transmutation GateOfTruth() -> void {
    Solid edad = 25
    Inscription nombre = "Alchemist"
    Principle activo = Accepted
    
    Solid resultado = cuadrado(5)
    TransmuteLine("El cuadrado de 5 es: " + resultado)
    
    Observe (edad >= 18) {
        TransmuteLine(nombre + " es mayor de edad")
    }
    
    AlchemicCycle (Solid i = 1; i <= 3; i = i + 1) {
        TransmuteLine("Iteracion " + i)
    }
}

Transmutation cuadrado(Solid n) -> Solid {
    EquivalentExchange n * n
}
"""
        )
    
    def mostrar_tipos_datos(self):
        """Muestra los tipos de datos disponibles"""
        self._mostrar_ayuda_con_codigo(
            "Tipos de Datos",
            """TIPOS SIMPLES (5):

1. Solid (int)
   • Numeros enteros: 42, -100, 0

2. Liquid (float)
   • Numeros decimales: 3.14, -2.5, 0.0

3. Inscription (string)
   • Cadenas de texto: "Hola", 'Mundo'

4. Principle (bool)
   • Valores booleanos: Accepted (true), Rejected (false)

5. Emptiness (null)
   • Valor nulo/vacio

TIPOS COMPUESTOS (2):

1. Arrays (arreglos unidimensionales)
   • Coleccion de elementos del mismo tipo
   • Sintaxis: AlchemicArray[Tipo, Tamaño] nombre
   • Acceso: nombre[indice]

2. Matrices (arreglos bidimensionales)
   • Tabla de elementos del mismo tipo
   • Sintaxis: AlchemicMatrix[Tipo, Filas, Columnas] nombre
   • Acceso: nombre[fila][columna]
""",
            """// Ejemplo: Tipos de Datos
Transmutation GateOfTruth() -> void {
    // Tipos simples
    Solid entero = 42
    Liquid decimal = 3.14
    Inscription texto = "Alchemist"
    Principle booleano = Accepted
    Liquid nulo = Emptiness
    
    TransmuteLine("Entero: " + entero)
    TransmuteLine("Decimal: " + decimal)
    TransmuteLine("Texto: " + texto)
    TransmuteLine("Booleano: " + booleano)
    
    // Arrays
    AlchemicArray[Solid, 5] numeros
    numeros[0] = 10
    numeros[1] = 20
    numeros[2] = 30
    
    TransmuteLine("Primer numero: " + numeros[0])
    
    // Matrices
    AlchemicMatrix[Solid, 2, 2] matriz
    matriz[0][0] = 1
    matriz[0][1] = 2
    matriz[1][0] = 3
    matriz[1][1] = 4
    
    TransmuteLine("Elemento [1][1]: " + matriz[1][1])
}
"""
        )
    
    def _mostrar_ayuda_con_codigo(self, titulo, explicacion, codigo_ejemplo):
        """Ventana genérica para mostrar ayuda con opción de insertar código"""
        win = tk.Toplevel(self.root)
        win.title(titulo)
        win.geometry("900x700")
        win.configure(bg=self.bg_dark)
        
        tk.Label(win, text=titulo, font=('Arial', 12, 'bold'), 
                bg=self.bg_dark, fg=self.fg_light).pack(pady=10)
        
        # Frame principal dividido en dos columnas
        content_frame = tk.Frame(win, bg=self.bg_dark)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Columna izquierda: Explicación
        left_frame = tk.Frame(content_frame, bg=self.bg_dark)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        tk.Label(left_frame, text="Explicación:", font=('Arial', 10, 'bold'), 
                bg=self.bg_dark, fg=self.fg_light, anchor='w').pack(fill=tk.X)
        
        txt_explicacion = tk.Text(left_frame, font=('Courier', 9), bg=self.editor_bg, 
                                 fg=self.editor_fg, relief=tk.SOLID, bd=1, 
                                 padx=10, pady=10, wrap=tk.WORD)
        txt_explicacion.pack(fill=tk.BOTH, expand=True)
        txt_explicacion.insert('1.0', explicacion)
        txt_explicacion.config(state=tk.DISABLED)
        
        # Columna derecha: Código ejemplo
        right_frame = tk.Frame(content_frame, bg=self.bg_dark)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))
        
        tk.Label(right_frame, text="Código de Ejemplo:", font=('Arial', 10, 'bold'), 
                bg=self.bg_dark, fg=self.fg_light, anchor='w').pack(fill=tk.X)
        
        txt_codigo = tk.Text(right_frame, font=('Courier', 9), bg=self.editor_bg, 
                            fg=self.editor_fg, relief=tk.SOLID, bd=1, 
                            padx=10, pady=10, wrap=tk.NONE)
        txt_codigo.pack(fill=tk.BOTH, expand=True)
        txt_codigo.insert('1.0', codigo_ejemplo)
        txt_codigo.config(state=tk.DISABLED)
        
        # Botón para insertar código
        btn_frame = tk.Frame(win, bg=self.bg_dark)
        btn_frame.pack(fill=tk.X, padx=20, pady=10)
        
        tk.Button(btn_frame, text="✨ Insertar Código de Ejemplo en el Editor", 
                 command=lambda: self.insertar_codigo(codigo_ejemplo, win),
                 bg='#0e639c', fg='white', activebackground='#1177bb',
                 font=('Arial', 10, 'bold'), relief=tk.SOLID, bd=1, 
                 padx=20, pady=10).pack(fill=tk.X)
    
    def insertar_codigo(self, codigo, ventana=None):
        """Inserta código de ejemplo en el editor"""
        if self.code_editor.get('1.0', tk.END).strip():
            if not messagebox.askyesno("Confirmar", 
                "El editor tiene contenido. ¿Desea reemplazarlo con el código de ejemplo?"):
                return
        
        self.code_editor.delete('1.0', tk.END)
        self.code_editor.insert('1.0', codigo)
        self.update_line_numbers()
        self.clear_output()
        
        # Invalidar compilación anterior al insertar nuevo código
        self.compilation_result = None
        
        if ventana:
            ventana.destroy()
        
        messagebox.showinfo("Éxito", "Código insertado en el editor")
        
    def salir(self):
        if messagebox.askyesno("Salir", "¿Seguro?"):
            self.root.quit()
            
    def compilar(self):
        """Compila el código del editor"""
        codigo = self.code_editor.get('1.0', tk.END)
        
        # Validación: código vacío
        if not codigo.strip():
            self.show_output("❌ ERROR: El editor está vacío\n")
            self.show_output("Escribe código Alchemist o usa el menú 'Opciones' para insertar ejemplos\n")
            return
        
        # Validación: debe tener la función principal GateOfTruth
        if "GateOfTruth" not in codigo:
            self.show_output("❌ ERROR: El programa debe tener la función principal 'GateOfTruth'\n")
            self.show_output("Ejemplo:\n")
            self.show_output("  Transmutation GateOfTruth() -> void {\n")
            self.show_output("      // tu código aquí\n")
            self.show_output("  }\n")
            return
            
        self.clear_output()
        self.show_output("=== COMPILANDO ===\n\n")
        
        try:
            # Crear nuevo compilador para cada compilación (evita estado residual)
            self.compiler = AlchemistCompiler()
            self.compilation_result = self.compiler.compile(codigo)
            
            if self.compilation_result.success:
                self.show_output("✅ Compilación exitosa\n")
                self.show_output(f"📦 {len(self.compilation_result.instructions)} instrucciones generadas\n\n")
                self.show_output("👉 Presione EJECUTAR para correr el programa\n")
            else:
                self.show_output("❌ ERRORES DE COMPILACIÓN:\n\n")
                for i, error in enumerate(self.compilation_result.errors, 1):
                    self.show_output(f"  {i}. {error}\n")
                self.show_output(f"\n💡 Total de errores: {len(self.compilation_result.errors)}\n")
                self.compilation_result = None
                
        except SyntaxError as e:
            self.show_output(f"❌ ERROR DE SINTAXIS:\n  {str(e)}\n")
            self.compilation_result = None
        except ValueError as e:
            self.show_output(f"❌ ERROR DE VALOR:\n  {str(e)}\n")
            self.compilation_result = None
        except Exception as e:
            self.show_output(f"❌ ERROR INESPERADO:\n")
            self.show_output(f"  Tipo: {type(e).__name__}\n")
            self.show_output(f"  Mensaje: {str(e)}\n")
            self.show_output(f"\n💡 Si el error persiste, revisa la sintaxis del código\n")
            self.compilation_result = None
            
    def ejecutar(self):
        """Ejecuta el código compilado"""
        # Validación: debe compilar primero
        if not self.compilation_result or not self.compilation_result.success:
            self.show_output("\n❌ ERROR: Debe compilar el código primero\n")
            self.show_output("👉 Presione COMPILAR antes de ejecutar\n")
            return
        
        self.show_output("\n=== EJECUTANDO ===\n\n")
        
        try:
            # Crear callback para entrada interactiva
            def input_callback(prompt, tipo):
                """Muestra un diálogo simple para solicitar entrada"""
                if tipo == "text":
                    return simpledialog.askstring("Entrada", prompt, parent=self.root)
                elif tipo == "int":
                    while True:
                        valor = simpledialog.askstring("Entrada", prompt, parent=self.root)
                        if valor is None:  # Usuario canceló
                            return "0"
                        try:
                            int(valor)
                            return valor
                        except ValueError:
                            messagebox.showerror("Error", f"'{valor}' no es un número entero válido")
                elif tipo == "float":
                    while True:
                        valor = simpledialog.askstring("Entrada", prompt, parent=self.root)
                        if valor is None:  # Usuario canceló
                            return "0.0"
                        try:
                            float(valor)
                            return valor
                        except ValueError:
                            messagebox.showerror("Error", f"'{valor}' no es un número decimal válido")
                elif tipo == "bool":
                    return simpledialog.askstring("Entrada", prompt, parent=self.root)
                else:
                    return simpledialog.askstring("Entrada", prompt, parent=self.root)
            
            result = self.compiler.execute(self.compilation_result, input_callback=input_callback)
            
            if result.success:
                # Mostrar salida del programa
                if result.output:
                    self.show_output(result.output)
                else:
                    self.show_output("(El programa no generó ninguna salida)\n")
                
                self.show_output(f"\n✅ Ejecución completada en {result.execution_time:.3f} segundos\n")
            else:
                self.show_output("❌ ERRORES DE EJECUCIÓN:\n\n")
                for i, error in enumerate(result.errors, 1):
                    self.show_output(f"  {i}. {error}\n")
                self.show_output(f"\n💡 Total de errores: {len(result.errors)}\n")
                
        except RecursionError:
            self.show_output("❌ ERROR: Recursión infinita detectada\n")
            self.show_output("  El límite de recursión es 1000 llamadas\n")
            self.show_output("💡 Revisa que tus funciones recursivas tengan caso base\n")
        except KeyboardInterrupt:
            self.show_output("\n⚠️  Ejecución interrumpida por el usuario\n")
        except MemoryError:
            self.show_output("❌ ERROR: Memoria insuficiente\n")
            self.show_output("💡 El programa está usando demasiada memoria\n")
        except IndexError as e:
            self.show_output(f"❌ ERROR DE ÍNDICE:\n  {str(e)}\n")
            self.show_output("💡 Verifica que los índices de arrays estén dentro de rango\n")
        except KeyError as e:
            self.show_output(f"❌ ERROR DE CLAVE:\n  {str(e)}\n")
        except TypeError as e:
            self.show_output(f"❌ ERROR DE TIPO:\n  {str(e)}\n")
            self.show_output("💡 Verifica que los tipos de datos sean compatibles\n")
        except ValueError as e:
            self.show_output(f"❌ ERROR DE VALOR:\n  {str(e)}\n")
        except ZeroDivisionError:
            self.show_output("❌ ERROR: División por cero\n")
            self.show_output("💡 No se puede dividir entre 0\n")
        except Exception as e:
            self.show_output(f"❌ ERROR INESPERADO:\n")
            self.show_output(f"  Tipo: {type(e).__name__}\n")
            self.show_output(f"  Mensaje: {str(e)}\n")
            
    def levenshtein_distance(self, s1, s2):
        """Calcula la distancia de Levenshtein entre dos cadenas"""
        if len(s1) < len(s2):
            return self.levenshtein_distance(s2, s1)
        if len(s2) == 0:
            return len(s1)
        
        previous_row = range(len(s2) + 1)
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row
        
        return previous_row[-1]
    
    def sugerir_palabra(self, palabra_incorrecta):
        """Sugiere una palabra reservada similar basada en distancia de Levenshtein"""
        if not palabra_incorrecta:
            return None
        
        # Buscar la palabra más similar
        mejor_sugerencia = None
        menor_distancia = float('inf')
        
        for palabra_correcta in self.PALABRAS_RESERVADAS:
            # Comparación case-insensitive
            distancia = self.levenshtein_distance(
                palabra_incorrecta.lower(), 
                palabra_correcta.lower()
            )
            
            # Solo sugerir si la distancia es razonable (máximo 3 caracteres de diferencia)
            if distancia < menor_distancia and distancia <= 3:
                menor_distancia = distancia
                mejor_sugerencia = palabra_correcta
        
        return mejor_sugerencia
    
    def mejorar_mensaje_error(self, mensaje_error):
        """Mejora mensajes de error agregando sugerencias"""
        # Buscar palabras no reconocidas en el mensaje
        import re
        
        # Patrón para detectar identificadores no reconocidos
        patrones = [
            r"'([A-Za-z_][A-Za-z0-9_]*)' (no reconocido|no definido|no existe)",
            r"nombre '([A-Za-z_][A-Za-z0-9_]*)' no",
            r"palabra reservada mal escrita: '([A-Za-z_][A-Za-z0-9_]*)'"
        ]
        
        mensaje_mejorado = mensaje_error
        
        for patron in patrones:
            match = re.search(patron, mensaje_error, re.IGNORECASE)
            if match:
                palabra_incorrecta = match.group(1)
                sugerencia = self.sugerir_palabra(palabra_incorrecta)
                
                if sugerencia:
                    mensaje_mejorado += f"\n💡 ¿Quisiste decir '{sugerencia}'?"
                break
        
        return mensaje_mejorado
            
    def show_output(self, text):
        # Mejorar mensajes de error con sugerencias
        if "Error" in text or "ERROR" in text:
            text = self.mejorar_mensaje_error(text)
        
        self.output_text.config(state=tk.NORMAL)
        self.output_text.insert(tk.END, text)
        self.output_text.see(tk.END)
        self.output_text.config(state=tk.DISABLED)
        
    def clear_output(self):
        self.output_text.config(state=tk.NORMAL)
        self.output_text.delete('1.0', tk.END)
        self.output_text.config(state=tk.DISABLED)
    
    # ========== MÉTODOS PARA INSERTAR PLANTILLAS ==========
    
    def insertar_main(self):
        """Inserta plantilla de programa principal"""
        codigo = """// Programa principal
Transmutation GateOfTruth() -> void {
    TransmuteLine("Hola Mundo desde Alchemist!")
    
}
"""
        self.code_editor.insert(tk.INSERT, codigo)
        self.update_line_numbers()
    
    def insertar_if_simple(self):
        """Inserta plantilla de condicional simple"""
        codigo = """Reaction (condicion) {
    // código si verdadero
}
"""
        self.code_editor.insert(tk.INSERT, codigo)
        self.update_line_numbers()
    
    def insertar_if_else(self):
        """Inserta plantilla de condicional con else"""
        codigo = """Reaction (condicion) {
    // código si verdadero
} Dissolve {
    // código si falso
}
"""
        self.code_editor.insert(tk.INSERT, codigo)
        self.update_line_numbers()
    
    def insertar_while(self):
        """Inserta plantilla de ciclo while"""
        codigo = """Cycle (condicion) {
    // código del ciclo
}
"""
        self.code_editor.insert(tk.INSERT, codigo)
        self.update_line_numbers()
    
    def insertar_for(self):
        """Inserta plantilla de ciclo for"""
        codigo = """Iterate(Solid i = 0; i < 10; i = i + 1) {
    // código del ciclo
}
"""
        self.code_editor.insert(tk.INSERT, codigo)
        self.update_line_numbers()
    
    def insertar_funcion(self):
        """Inserta plantilla de función con retorno"""
        codigo = """Transmutation nombre_funcion(Solid parametro) -> Solid {
    // código de la función
    EquivalentExchange resultado
}
"""
        self.code_editor.insert(tk.INSERT, codigo)
        self.update_line_numbers()
    
    def insertar_funcion_void(self):
        """Inserta plantilla de función void"""
        codigo = """Transmutation nombre_funcion(Solid parametro) -> void {
    // código de la función
}
"""
        self.code_editor.insert(tk.INSERT, codigo)
        self.update_line_numbers()
    
    def insertar_array(self):
        """Inserta plantilla de array"""
        codigo = """// Declarar array
AlchemicArray[Solid, 5] numeros

// Asignar valores
numeros[0] = 10
numeros[1] = 20

// Leer valores
Solid valor = numeros[0]
"""
        self.code_editor.insert(tk.INSERT, codigo)
        self.update_line_numbers()
    
    def insertar_matriz(self):
        """Inserta plantilla de matriz"""
        codigo = """// Declarar matriz 3x3
AlchemicMatrix[Solid, 3, 3] matriz

// Asignar valores
matriz[0][0] = 1
matriz[0][1] = 2

// Leer valores
Solid valor = matriz[0][0]
"""
        self.code_editor.insert(tk.INSERT, codigo)
        self.update_line_numbers()
    
    def insertar_input(self):
        """Inserta plantilla de entrada de datos"""
        codigo = """// Entrada de datos
Inscription nombre = Absorb("Ingresa tu nombre")
Solid edad = AbsorbSolid("Ingresa tu edad")
Liquid altura = AbsorbLiquid("Ingresa tu altura")
"""
        self.code_editor.insert(tk.INSERT, codigo)
        self.update_line_numbers()
    
    def insertar_output(self):
        """Inserta plantilla de salida de datos"""
        codigo = """// Salida de datos
Transmute("Texto sin salto de linea")
TransmuteLine("Texto con salto de linea")
"""
        self.code_editor.insert(tk.INSERT, codigo)
        self.update_line_numbers()
        
    def run(self):
        self.root.mainloop()

def main():
    ide = AlchemistIDESimple()
    ide.run()

if __name__ == "__main__":
    main()
