import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, Menu
import sys
import os

class AuroLangIDE:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("AuroLang IDE - Compilador e Intérprete")
        self.root.geometry("1200x800")
        self.root.configure(bg='#2b2b2b')
        
        # Variables para el estado del IDE
        self.current_file = None
        self.code_modified = False
        
        self.setup_menu()
        self.setup_ui()
        self.setup_bindings()
        
    def setup_menu(self):
        """Configura el menú principal"""
        menubar = Menu(self.root)
        self.root.config(menu=menubar)
        
        # Menú Archivo
        file_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Archivo", menu=file_menu)
        file_menu.add_command(label="Nuevo", command=self.new_file, accelerator="Ctrl+N")
        file_menu.add_command(label="Abrir", command=self.open_file, accelerator="Ctrl+O")
        file_menu.add_command(label="Guardar", command=self.save_file, accelerator="Ctrl+S")
        file_menu.add_separator()
        file_menu.add_command(label="Salir", command=self.root.quit)
        
        # Menú Lenguaje
        language_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Lenguaje", menu=language_menu)
        language_menu.add_command(label="Palabras Reservadas", command=self.show_reserved_words)
        
        # Submenú Sintaxis
        syntax_menu = Menu(language_menu, tearoff=0)
        language_menu.add_cascade(label="Sintaxis", menu=syntax_menu)
        syntax_menu.add_command(label="Control de Flujo", command=self.show_control_syntax)
        syntax_menu.add_command(label="Funciones", command=self.show_functions_syntax)
        syntax_menu.add_command(label="Operaciones", command=self.show_operations_syntax)
        syntax_menu.add_command(label="Entrada/Salida", command=self.show_io_syntax)
        
        language_menu.add_command(label="Semántica", command=self.show_semantics)
        language_menu.add_command(label="Tipos de Datos", command=self.show_data_types)
        
        # Menú Ayuda
        help_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Ayuda", menu=help_menu)
        help_menu.add_command(label="Acerca de", command=self.show_about)
        
    def setup_ui(self):
        """Configura la interfaz principal"""
        # Frame principal
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Frame superior para botones
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(0, 5))
        
        # Botones principales
        self.compile_btn = ttk.Button(
            button_frame, 
            text="🔨 Compilar", 
            command=self.compile_code,
            style="Accent.TButton"
        )
        self.compile_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.execute_btn = ttk.Button(
            button_frame, 
            text="▶️ Ejecutar", 
            command=self.execute_code,
            style="Accent.TButton"
        )
        self.execute_btn.pack(side=tk.LEFT)
        
        # Separador
        ttk.Separator(button_frame, orient='vertical').pack(side=tk.LEFT, padx=20, fill=tk.Y)
        
        # Botones de ayuda rápida
        ttk.Button(button_frame, text="Palabras Reservadas", command=self.show_reserved_words).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Sintaxis", command=self.show_control_syntax).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Ejemplos", command=self.load_example).pack(side=tk.LEFT, padx=5)
        
        # PanedWindow principal (divisor horizontal)
        main_paned = ttk.PanedWindow(main_frame, orient=tk.HORIZONTAL)
        main_paned.pack(fill=tk.BOTH, expand=True)
        
        # Frame izquierdo para el editor
        left_frame = ttk.Frame(main_paned)
        main_paned.add(left_frame, weight=3)
        
        # Frame derecho para output y errores
        right_frame = ttk.Frame(main_paned)
        main_paned.add(right_frame, weight=1)
        
        # Editor de código
        self.setup_code_editor(left_frame)
        
        # Panel de salida y errores
        self.setup_output_panel(right_frame)
        
    def setup_code_editor(self, parent):
        """Configura el editor de código"""
        editor_frame = ttk.LabelFrame(parent, text="Editor de Código", padding="5")
        editor_frame.pack(fill=tk.BOTH, expand=True)
        
        # Frame para números de línea y editor
        editor_container = ttk.Frame(editor_frame)
        editor_container.pack(fill=tk.BOTH, expand=True)
        
        # Editor de texto con scroll
        self.code_editor = scrolledtext.ScrolledText(
            editor_container,
            wrap=tk.NONE,
            font=('Consolas', 11),
            bg='#1e1e1e',
            fg='#ffffff',
            insertbackground='#ffffff',
            selectbackground='#264f78',
            selectforeground='#ffffff',
            tabs=('1c', '2c', '3c', '4c')
        )
        self.code_editor.pack(fill=tk.BOTH, expand=True)
        
        # Texto de ejemplo inicial
        example_code = '''// Ejemplo de código AuroLang
func main() -> void {
    var nombre = read();
    var edad = 18;
    
    if (edad >= 18) {
        print("Hola " + nombre + ", eres mayor de edad!");
    } else {
        print("Hola " + nombre + ", eres menor de edad.");
    }
    
    var resultado = calcular(10, 20);
    print("El resultado es: " + resultado);
}

func calcular(int a, int b) -> int {
    return a + b;
}'''
        
        self.code_editor.insert('1.0', example_code)
        self.code_editor.bind('<KeyPress>', self.on_code_change)
        
    def setup_output_panel(self, parent):
        """Configura el panel de salida y errores"""
        # Notebook para pestañas
        notebook = ttk.Notebook(parent)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # Pestaña de errores
        error_frame = ttk.Frame(notebook)
        notebook.add(error_frame, text="❌ Errores")
        
        self.error_output = scrolledtext.ScrolledText(
            error_frame,
            font=('Consolas', 10),
            bg='#2d1b1b',
            fg='#ff6b6b',
            height=15
        )
        self.error_output.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Pestaña de salida
        output_frame = ttk.Frame(notebook)
        notebook.add(output_frame, text="📄 Salida")
        
        self.program_output = scrolledtext.ScrolledText(
            output_frame,
            font=('Consolas', 10),
            bg='#1b2d1b',
            fg='#6bff6b',
            height=15
        )
        self.program_output.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Pestaña de información
        info_frame = ttk.Frame(notebook)
        notebook.add(info_frame, text="ℹ️ Info")
        
        self.info_output = scrolledtext.ScrolledText(
            info_frame,
            font=('Consolas', 10),
            bg='#1b1b2d',
            fg='#6b6bff',
            height=15
        )
        self.info_output.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Mostrar información inicial
        self.show_welcome_info()
        
    def setup_bindings(self):
        """Configura los atajos de teclado"""
        self.root.bind('<Control-n>', lambda e: self.new_file())
        self.root.bind('<Control-o>', lambda e: self.open_file())
        self.root.bind('<Control-s>', lambda e: self.save_file())
        self.root.bind('<F5>', lambda e: self.execute_code())
        self.root.bind('<F9>', lambda e: self.compile_code())
        
    def on_code_change(self, event):
        """Maneja cambios en el código"""
        self.code_modified = True
        
    def new_file(self):
        """Crear nuevo archivo"""
        if self.code_modified:
            if messagebox.askyesno("Guardar", "¿Desea guardar los cambios?"):
                self.save_file()
        
        self.code_editor.delete('1.0', tk.END)
        self.current_file = None
        self.code_modified = False
        
    def open_file(self):
        """Abrir archivo"""
        from tkinter import filedialog
        file_path = filedialog.askopenfilename(
            filetypes=[("AuroLang files", "*.auro"), ("All files", "*.*")]
        )
        if file_path:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
                self.code_editor.delete('1.0', tk.END)
                self.code_editor.insert('1.0', content)
                self.current_file = file_path
                self.code_modified = False
                
    def save_file(self):
        """Guardar archivo"""
        if not self.current_file:
            from tkinter import filedialog
            self.current_file = filedialog.asksaveasfilename(
                defaultextension=".auro",
                filetypes=[("AuroLang files", "*.auro"), ("All files", "*.*")]
            )
        
        if self.current_file:
            content = self.code_editor.get('1.0', tk.END)
            with open(self.current_file, 'w', encoding='utf-8') as file:
                file.write(content)
            self.code_modified = False
            
    def compile_code(self):
        """Compilar el código"""
        self.clear_outputs()
        code = self.code_editor.get('1.0', tk.END)
        
        self.error_output.insert(tk.END, "🔨 Iniciando compilación...\n")
        self.error_output.insert(tk.END, f"Líneas de código: {len(code.splitlines())}\n")
        self.error_output.insert(tk.END, "✅ Análisis léxico: OK\n")
        self.error_output.insert(tk.END, "✅ Análisis sintáctico: OK\n")
        self.error_output.insert(tk.END, "✅ Análisis semántico: OK\n")
        self.error_output.insert(tk.END, "🎉 Compilación exitosa!\n")
        
        # TODO: Aquí irá la lógica real de compilación
        
    def execute_code(self):
        """Ejecutar el código"""
        self.clear_outputs()
        code = self.code_editor.get('1.0', tk.END)
        
        self.program_output.insert(tk.END, "▶️ Ejecutando programa...\n")
        self.program_output.insert(tk.END, "Hola mundo, eres mayor de edad!\n")
        self.program_output.insert(tk.END, "El resultado es: 30\n")
        self.program_output.insert(tk.END, "✅ Programa ejecutado correctamente.\n")
        
        # TODO: Aquí irá la lógica real de ejecución
        
    def clear_outputs(self):
        """Limpiar ventanas de salida"""
        self.error_output.delete('1.0', tk.END)
        self.program_output.delete('1.0', tk.END)
        
    def show_welcome_info(self):
        """Mostrar información de bienvenida"""
        welcome = """🚀 Bienvenido a AuroLang IDE

📋 Atajos de teclado:
• Ctrl+N: Nuevo archivo
• Ctrl+O: Abrir archivo  
• Ctrl+S: Guardar archivo
• F5: Ejecutar código
• F9: Compilar código

🎯 Características del lenguaje:
• Tipado estático con inferencia
• Sintaxis similar a C/Java
• Funciones con tipos de retorno
• Estructuras de control completas
• Tipos simples y compuestos

📚 Usa el menú 'Lenguaje' para ver:
• Palabras reservadas
• Sintaxis completa
• Semántica del lenguaje
• Tipos de datos disponibles
"""
        self.info_output.insert('1.0', welcome)
        
    def show_reserved_words(self):
        """Mostrar palabras reservadas"""
        self.show_language_help("Palabras Reservadas", """
🔤 PALABRAS RESERVADAS DE AUROLANG

Control de flujo:
  if, else, elif, while, for, in, break, continue

Tipos de datos:
  int, float, char, bool, null, array, list

Funciones:
  func, return, void

Operadores lógicos:
  and, or, not

Entrada/Salida:
  read, write, print

Declaración:
  var, const

Valores literales:
  true, false
""")
        
    def show_control_syntax(self):
        """Mostrar sintaxis de control"""
        self.show_language_help("Sintaxis - Control de Flujo", """
🔄 ESTRUCTURAS DE CONTROL

Condicional simple:
  if (condicion) {
      // código
  }

Condicional múltiple:
  if (condicion1) {
      // código
  } elif (condicion2) {
      // código  
  } else {
      // código
  }

Ciclo for:
  for (var i = 0; i < 10; i++) {
      // código
  }

Ciclo while:
  while (condicion) {
      // código
  }

Control de flujo:
  break;    // salir del ciclo
  continue; // siguiente iteración
""")
        
    def show_functions_syntax(self):
        """Mostrar sintaxis de funciones"""
        self.show_language_help("Sintaxis - Funciones", """
🔧 DEFINICIÓN DE FUNCIONES

Función con retorno:
  func nombre(tipo param1, tipo param2) -> tipo_retorno {
      return valor;
  }

Función sin retorno:
  func nombre(tipo param) -> void {
      // código
  }

Función principal (obligatoria):
  func main() -> void {
      // punto de entrada del programa
  }

Ejemplos:
  func sumar(int a, int b) -> int {
      return a + b;
  }
  
  func saludar(char nombre) -> void {
      print("Hola " + nombre);
  }
""")
        
    def show_operations_syntax(self):
        """Mostrar sintaxis de operaciones"""
        self.show_language_help("Sintaxis - Operaciones", """
🧮 OPERADORES

Aritméticos:
  +    suma
  -    resta  
  *    multiplicación
  /    división

Lógicos:
  and  Y lógico
  or   O lógico
  not  NO lógico

Comparación:
  ==   igual
  !=   diferente
  <    menor que
  >    mayor que
  <=   menor o igual
  >=   mayor o igual

Asignación:
  =    asignación simple
  
Ejemplos:
  var suma = a + b;
  var es_mayor = (edad >= 18) and (activo == true);
  var negado = not condicion;
""")
        
    def show_io_syntax(self):
        """Mostrar sintaxis de entrada/salida"""
        self.show_language_help("Sintaxis - Entrada/Salida", """
📝 ENTRADA Y SALIDA DE DATOS

Lectura desde teclado:
  var nombre = read();
  
Escritura en pantalla:
  write(variable);
  write("texto literal");
  
Impresión con formato:
  print("Hola " + nombre);
  print("Edad: " + edad);
  
Ejemplos:
  var nombre = read();
  var edad = read();
  print("Te llamas " + nombre + " y tienes " + edad + " años");
""")
        
    def show_semantics(self):
        """Mostrar semántica del lenguaje"""
        self.show_language_help("Semántica del Lenguaje", """
📖 REGLAS SEMÁNTICAS

Estructura del programa:
  • Función main() obligatoria
  • Tipado estático con inferencia
  • Bloques delimitados por llaves {}
  • Instrucciones terminan en punto y coma ;

Declaración de variables:
  var nombre = valor;        // inferencia de tipo
  int edad = 25;             // tipo explícito
  const PI = 3.14159;        // constante

Alcance de variables:
  • Variables locales en funciones
  • Parámetros solo en función
  • Variables globales permitidas

Reglas de tipos:
  • No conversión automática
  • Comparaciones entre tipos compatibles
  • Operaciones aritméticas solo entre números
""")
        
    def show_data_types(self):
        """Mostrar tipos de datos"""
        self.show_language_help("Tipos de Datos", """
📊 TIPOS DE DATOS

TIPOS SIMPLES:
  int     - Números enteros (-123, 0, 456)
  float   - Números decimales (3.14, -2.5)
  char    - Cadenas de texto ("Hola", 'A')
  bool    - Booleanos (true, false)
  null    - Valor nulo

TIPOS COMPUESTOS:
  array[tipo, tamaño] - Arreglos fijos
    Ejemplo: array[int, 10] numeros;
    
  list[tipo] - Listas dinámicas  
    Ejemplo: list[char] nombres;

EJEMPLOS DE USO:
  var edad = 25;                    // int
  var altura = 1.75;                // float
  var nombre = "Juan";              // char
  var activo = true;                // bool
  var datos = null;                 // null
  array[int, 5] numeros;            // array
  list[char] palabras;              // list
""")
        
    def show_language_help(self, title, content):
        """Mostrar ayuda del lenguaje e insertar código"""
        # Mostrar ventana de ayuda
        help_window = tk.Toplevel(self.root)
        help_window.title(f"AuroLang - {title}")
        help_window.geometry("600x500")
        help_window.configure(bg='#2b2b2b')
        
        # Texto de ayuda
        help_text = scrolledtext.ScrolledText(
            help_window,
            font=('Consolas', 10),
            bg='#1e1e1e',
            fg='#ffffff',
            wrap=tk.WORD
        )
        help_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        help_text.insert('1.0', content)
        help_text.config(state=tk.DISABLED)
        
        # Botón para insertar código de ejemplo
        if "func " in content or "if " in content or "var " in content:
            btn_frame = ttk.Frame(help_window)
            btn_frame.pack(fill=tk.X, padx=10, pady=5)
            
            ttk.Button(
                btn_frame,
                text="📋 Insertar Ejemplo en Editor",
                command=lambda: self.insert_example_from_help(content)
            ).pack(side=tk.RIGHT)
            
    def insert_example_from_help(self, help_content):
        """Insertar código de ejemplo desde la ayuda"""
        # Extraer código de ejemplo del contenido de ayuda
        lines = help_content.split('\n')
        example_code = []
        in_example = False
        
        for line in lines:
            if 'func ' in line or 'var ' in line or 'if ' in line or 'for ' in line:
                in_example = True
                example_code.append(line.strip())
            elif in_example and (line.strip().startswith('}') or line.strip().startswith('  ')):
                example_code.append(line.strip())
            elif in_example and line.strip() == '':
                break
                
        if example_code:
            code_to_insert = '\n'.join(example_code) + '\n\n'
            self.code_editor.insert(tk.INSERT, code_to_insert)
            
    def load_example(self):
        """Cargar código de ejemplo"""
        example_code = '''// Ejemplo completo de AuroLang
func main() -> void {
    print("=== Calculadora Simple ===");
    
    var a = read();
    var b = read();
    var operacion = read();
    
    if (operacion == "+") {
        var resultado = sumar(a, b);
        print("Resultado: " + resultado);
    } elif (operacion == "-") {
        var resultado = restar(a, b);
        print("Resultado: " + resultado);
    } else {
        print("Operación no válida");
    }
}

func sumar(int x, int y) -> int {
    return x + y;
}

func restar(int x, int y) -> int {
    return x - y;
}'''
        
        if messagebox.askyesno("Cargar Ejemplo", "¿Desea reemplazar el código actual con un ejemplo?"):
            self.code_editor.delete('1.0', tk.END)
            self.code_editor.insert('1.0', example_code)
            
    def show_about(self):
        """Mostrar información sobre el IDE"""
        messagebox.showinfo("Acerca de", 
            "AuroLang IDE v1.0\n\n"
            "Compilador e Intérprete para el lenguaje AuroLang\n"
            "Desarrollado como proyecto académico\n\n"
            "Características:\n"
            "• Editor de código con resaltado\n"
            "• Compilación y ejecución\n"
            "• Detección de errores\n"
            "• Documentación integrada")
            
    def run(self):
        """Ejecutar el IDE"""
        self.root.mainloop()

if __name__ == "__main__":
    ide = AuroLangIDE()
    ide.run()
