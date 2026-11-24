import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, Menu, filedialog 
import traceback

from .compiler import AurumCompiler, CompilationResult

class AurumIDE:

    #inicia el ide
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Aurum IDE - Compilador e Interprete")
        self.root.geometry("1200x800")
        self.root.configure(bg='#2b2b2b')
        
        # variables para el estado del ide
        self.current_file = None
        self.code_modified = False

        # inicializar el compilador
        self.compiler = AurumCompiler()
        self.compiler.set_verbose(True)
        
        # resultado de compilacion actual
        self.last_compilation: CompilationResult = None
        # inicializa el menu, la ui y los bindings
        self.setup_menu()
        self.setup_ui()
        self.setup_bindings()
        

    def setup_menu(self):
        """Configura el menú principal"""
        # de tkinter utilizamos un Menu para hacer los menus
        menubar = Menu(self.root)
        self.root.config(menu=menubar)
        
        # menu para acciones de archivos
        file_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Archivo", menu=file_menu)
        file_menu.add_command(label="Nuevo", command=self.new_file, accelerator="Ctrl+N")
        file_menu.add_command(label="Abrir", command=self.open_file, accelerator="Ctrl+O")
        file_menu.add_command(label="Guardar", command=self.save_file, accelerator="Ctrl+S")
        file_menu.add_separator()
        file_menu.add_command(label="Salir", command=self.root.quit)
        
        # menu para mostrar info del lenguaje, sintaxis, ejemplos etc
        language_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Lenguaje", menu=language_menu)
        language_menu.add_command(label="Palabras Reservadas", command=self.show_reserved_words)
        
        # submenu para mostrar la sintaxis, separada en control de flujo, funciones, operaciones y io
        syntax_menu = Menu(language_menu, tearoff=0)
        language_menu.add_cascade(label="Sintaxis", menu=syntax_menu)
        syntax_menu.add_command(label="Control de Flujo", command=self.show_control_syntax)
        syntax_menu.add_command(label="Funciones", command=self.show_functions_syntax)
        syntax_menu.add_command(label="Operaciones", command=self.show_operations_syntax)
        syntax_menu.add_command(label="Entrada/Salida", command=self.show_io_syntax)
        
        language_menu.add_command(label="Semántica", command=self.show_semantics)
        language_menu.add_command(label="Tipos de Datos", command=self.show_data_types)
        
        # acerca de
        menubar.add_command(label="Acerca de", command=self.show_about)
        
    def setup_ui(self):
        """Configura la interfaz principal"""
         
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
      
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(0, 5))
        
        
        self.compile_btn = ttk.Button(
            button_frame, 
            text="Compilar", 
            command=self.compile_code,
            style="Accent.TButton"
        )
        self.compile_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.execute_btn = ttk.Button(
            button_frame, 
            text="Ejecutar", 
            command=self.execute_code,
            style="Accent.TButton",
            state='disabled'   
        )
        self.execute_btn.pack(side=tk.LEFT)
        
        # separador
        ttk.Separator(button_frame, orient='vertical').pack(side=tk.LEFT, padx=20, fill=tk.Y)
        
        
        ttk.Button(button_frame, text="Palabras Reservadas", command=self.show_reserved_words).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Sintaxis", command=self.show_control_syntax).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Ejemplos", command=self.load_example).pack(side=tk.LEFT, padx=5)
        
        # paned window para dividir editor y output
        main_paned = ttk.PanedWindow(main_frame, orient=tk.HORIZONTAL)
        main_paned.pack(fill=tk.BOTH, expand=True)
        
        # frame izquierdo para editor
        left_frame = ttk.Frame(main_paned)
        main_paned.add(left_frame, weight=3)

        # frame derecho para output y errores
        right_frame = ttk.Frame(main_paned)
        main_paned.add(right_frame, weight=1)
         
         #pasamos los frames
        self.setup_code_editor(left_frame)
         
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
            bg="#000000",
            fg="#ffffff",
            insertbackground='#ffffff',
            selectbackground='#264f78',
            selectforeground='#ffffff',
            tabs=('1c', '2c', '3c', '4c') 
        )
        self.code_editor.pack(fill=tk.BOTH, expand=True)
        
        # Texto de ejemplo inicial
        example_code = '''// Ejemplo de código aurum
func main() -> void {
    print("¡Hola, aurum!")
    
    int edad = 25
    string nombre = "Usuario"
    
    print("Tu nombre es: " + nombre)
    print("Tu edad es: " + edad)
    
    if (edad >= 18) {
        print("Eres mayor de edad")
    } else {
        print("Eres menor de edad")
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
}'''
        
        self.code_editor.insert('1.0', example_code)
        self.code_editor.bind('<KeyPress>', self.on_code_change)
        
    def setup_output_panel(self, parent):
        """Configura el panel de salida y errores"""
        # notebook para los tabs
        notebook = ttk.Notebook(parent)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # tab para errores
        error_frame = ttk.Frame(notebook)
        notebook.add(error_frame, text="Errores")
        
        self.error_output = scrolledtext.ScrolledText(
            error_frame,
            font=('Consolas', 10),
            bg="#000000",
            fg='#ff6b6b',
            height=15
        )
        self.error_output.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # tab de salida
        output_frame = ttk.Frame(notebook)
        notebook.add(output_frame, text="Salida")
        
        self.program_output = scrolledtext.ScrolledText(
            output_frame,
            font=('Consolas', 10),
            bg='#1b2d1b',
            fg='#6bff6b',
            height=15
        )
        self.program_output.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # tab info
        info_frame = ttk.Frame(notebook)
        notebook.add(info_frame, text="Info")
        
        self.info_output = scrolledtext.ScrolledText(
            info_frame,
            font=('Consolas', 10),
            bg='#1b1b2d',
            fg='#6b6bff',
            height=15
        )
        self.info_output.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        
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
        
        # Limpiar compilación anterior
        self.last_compilation = None
        self.execute_btn.config(state='disabled')
        
    def open_file(self):
        """Abrir archivo"""
        file_path = filedialog.askopenfilename(
            filetypes=[("aurum files", "*.auro"), ("Text files", "*.txt"), ("All files", "*.*")]
        )
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    content = file.read()
                    self.code_editor.delete('1.0', tk.END)
                    self.code_editor.insert('1.0', content)
                    self.current_file = file_path
                    self.code_modified = False
                    
                    # Limpiar compilación anterior
                    self.last_compilation = None
                    self.execute_btn.config(state='disabled')
                    
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo abrir el archivo:\n{e}")
                
    def save_file(self):
        """Guardar archivo"""
        if not self.current_file:
            self.current_file = filedialog.asksaveasfilename(
                defaultextension=".auro",
                filetypes=[("aurum files", "*.auro"), ("Text files", "*.txt"), ("All files", "*.*")]
            )
        
        if self.current_file:
            try:
                content = self.code_editor.get('1.0', tk.END)
                with open(self.current_file, 'w', encoding='utf-8') as file:
                    file.write(content)
                self.code_modified = False
                messagebox.showinfo("Guardado", f"Archivo guardado como:\n{self.current_file}")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo guardar el archivo:\n{e}")
            
    def compile_code(self):
        """Compilar el código"""
        self.clear_outputs()
        code = self.code_editor.get('1.0', tk.END)
        
        self.error_output.insert(tk.END, "🔨 Iniciando compilación de aurum...\n\n")
        
        try:
            # Compilar código usando el compilador real
            self.compiler.set_verbose(False)  # No mostrar verbose en IDE
            compilation_result = self.compiler.compile(code)
            
            if compilation_result.success:
                self.last_compilation = compilation_result
                
                # Mostrar resultado exitoso
                self.error_output.insert(tk.END, "✅ COMPILACIÓN EXITOSA\n")
                self.error_output.insert(tk.END, "=" * 40 + "\n")
                self.error_output.insert(tk.END, f"📊 Instrucciones generadas: {len(compilation_result.instructions)}\n")
                self.error_output.insert(tk.END, f"📊 Variables encontradas: {len(compilation_result.variables)}\n")
                self.error_output.insert(tk.END, f"📊 Funciones definidas: {len(compilation_result.functions)}\n\n")
                
                # Mostrar información de análisis
                self.error_output.insert(tk.END, "🔍 FASES COMPLETADAS:\n")
                self.error_output.insert(tk.END, "  ✅ Análisis léxico\n")
                self.error_output.insert(tk.END, "  ✅ Análisis sintáctico\n")
                self.error_output.insert(tk.END, "  ✅ Análisis semántico\n")
                self.error_output.insert(tk.END, "  ✅ Generación de código\n\n")
                
                self.error_output.insert(tk.END, "🎉 ¡Listo para ejecutar!\n")
                
                # Habilitar botón de ejecución
                self.execute_btn.config(state='normal')
                
            else:
                self.last_compilation = None
                
                # Mostrar errores
                self.error_output.insert(tk.END, "❌ ERRORES DE COMPILACIÓN\n")
                self.error_output.insert(tk.END, "=" * 40 + "\n")
                
                for i, error in enumerate(compilation_result.errors, 1):
                    self.error_output.insert(tk.END, f"{i}. {error}\n")
                
                self.error_output.insert(tk.END, f"\n💡 Se encontraron {len(compilation_result.errors)} errores.\n")
                self.error_output.insert(tk.END, "Corrige los errores y vuelve a compilar.\n")
                
                # Deshabilitar botón de ejecución
                self.execute_btn.config(state='disabled')
                
        except Exception as e:
            self.error_output.insert(tk.END, f"❌ ERROR INTERNO DEL COMPILADOR:\n")
            self.error_output.insert(tk.END, f"{str(e)}\n\n")
            self.error_output.insert(tk.END, "🔧 Detalles técnicos:\n")
            self.error_output.insert(tk.END, traceback.format_exc())
            
            self.last_compilation = None
            self.execute_btn.config(state='disabled')
        
    def execute_code(self):
        """Ejecutar el código"""
        if not self.last_compilation or not self.last_compilation.success:
            messagebox.showwarning("Advertencia", "Debes compilar el código exitosamente antes de ejecutarlo.")
            return
        
        self.clear_output_only()
        
        self.program_output.insert(tk.END, "🚀 Ejecutando programa aurum...\n")
        self.program_output.insert(tk.END, "=" * 40 + "\n")
        
        try:
            # Obtener entrada del usuario si es necesaria
            input_data = self.get_input_data()
            
            # Ejecutar programa
            execution_result = self.compiler.execute(self.last_compilation, input_data)
            
            if execution_result.success:
                # Mostrar salida del programa
                self.program_output.insert(tk.END, "📄 SALIDA DEL PROGRAMA:\n")
                self.program_output.insert(tk.END, "-" * 30 + "\n")
                
                if execution_result.output:
                    for line in execution_result.output:
                        self.program_output.insert(tk.END, f"{line}\n")
                else:
                    self.program_output.insert(tk.END, "(Sin salida)\n")
                
                self.program_output.insert(tk.END, "\n" + "-" * 30 + "\n")
                self.program_output.insert(tk.END, f"✅ Programa ejecutado correctamente.\n")
                self.program_output.insert(tk.END, f"⏱️ Tiempo de ejecución: {execution_result.execution_time:.3f}s\n")
                
            else:
                # Mostrar errores de ejecución
                self.program_output.insert(tk.END, "❌ ERRORES DE EJECUCIÓN:\n")
                self.program_output.insert(tk.END, "-" * 30 + "\n")
                
                for error in execution_result.errors:
                    self.program_output.insert(tk.END, f"{error}\n")
                
                # Mostrar salida parcial si existe
                if execution_result.output:
                    self.program_output.insert(tk.END, "\n📄 SALIDA PARCIAL:\n")
                    for line in execution_result.output:
                        self.program_output.insert(tk.END, f"{line}\n")
                
        except Exception as e:
            self.program_output.insert(tk.END, f"❌ ERROR INTERNO DEL INTÉRPRETE:\n")
            self.program_output.insert(tk.END, f"{str(e)}\n")
            self.program_output.insert(tk.END, "\n🔧 Detalles técnicos:\n")
            self.program_output.insert(tk.END, traceback.format_exc())
    
    def get_input_data(self):
        """Obtiene datos de entrada del usuario si son necesarios"""
        # Por ahora, datos de ejemplo
        # En el futuro se puede implementar un diálogo para entrada
        return []
    
    def clear_output_only(self):
        """Limpiar solo la ventana de salida del programa"""
        self.program_output.delete('1.0', tk.END)
        
    def clear_outputs(self):
        """Limpiar ventanas de salida"""
        self.error_output.delete('1.0', tk.END)
        self.program_output.delete('1.0', tk.END)
        
    def show_welcome_info(self):
        """Mostrar información de bienvenida"""
        welcome = """🚀 Bienvenido a aurum IDE

  Atajos de teclado:
• Ctrl+N: Nuevo archivo
• Ctrl+O: Abrir archivo  
• Ctrl+S: Guardar archivo
• F5: Ejecutar código
• F9: Compilar código

 Características del lenguaje:
• Tipado estático con inferencia
• Sintaxis similar a C/Java
• Funciones con tipos de retorno
• Estructuras de control completas
• Tipos simples y compuestos

  Usa el menú 'Lenguaje' para ver:
• Palabras reservadas
• Sintaxis completa
• Semántica del lenguaje
• Tipos de datos disponibles
"""
        self.info_output.insert('1.0', welcome)
        
    def show_reserved_words(self):
        """Mostrar palabras reservadas"""
        info = self.compiler.get_language_info()
        
        content = f"""
 PALABRAS RESERVADAS DE aurum

Control de flujo:
  if, else, elif, while, for, break, continue

Tipos de datos:
  {', '.join(info['data_types']['simple'])}

Funciones:
  func, return, void, main

Operadores lógicos:
  and, or, not

Entrada/Salida:
  read, write, print

Valores literales:
  true, false

🚀 Total de palabras reservadas: {len(info['keywords'])}

Todas las palabras: {', '.join(info['keywords'])}
"""
        self.show_language_help("Palabras Reservadas", content)
        
    def show_control_syntax(self):
        """Mostrar sintaxis de control"""
        self.show_language_help("Sintaxis - Control de Flujo", """
  ESTRUCTURAS DE CONTROL

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
  OPERADORES

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
  ENTRADA Y SALIDA DE DATOS

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
  REGLAS SEMÁNTICAS

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
 TIPOS DE DATOS

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
        help_window.title(f"aurum - {title}")
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
        example_code = '''// Ejemplo completo de aurum - Calculadora
func main() -> void {
    print("=== CALCULADORA aurum ===")
    
    int a = 15
    int b = 8
    
    print("Número A: " + a)
    print("Número B: " + b)
    print("")
    
    // Operaciones básicas
    int suma = a + b
    int resta = a - b
    int multiplicacion = a * b
    int division = a / b
    
    print("Suma: " + a + " + " + b + " = " + suma)
    print("Resta: " + a + " - " + b + " = " + resta)
    print("Multiplicación: " + a + " * " + b + " = " + multiplicacion)
    print("División: " + a + " / " + b + " = " + division)
    print("")
    
    // Condicionales
    if (suma > 20) {
        print("La suma es mayor a 20")
    } else {
        print("La suma es menor o igual a 20")
    }
    
    // Función recursiva
    int factorial_a = factorial(5)
    print("Factorial de 5: " + factorial_a)
    
    // Ciclo
    print("Contando del 1 al 5:")
    for (int i = 1; i <= 5; i = i + 1) {
        print("Número: " + i)
    }
}

func factorial(int n) -> int {
    if (n <= 1) {
        return 1
    } else {
        return n * factorial(n - 1)
    }
}'''
        
        if messagebox.askyesno("Cargar Ejemplo", "¿Desea reemplazar el código actual con un ejemplo completo?"):
            self.code_editor.delete('1.0', tk.END)
            self.code_editor.insert('1.0', example_code)
            
            # Limpiar compilación anterior
            self.last_compilation = None
            self.execute_btn.config(state='disabled')
            
    def show_about(self):
        """Mostrar información sobre el IDE"""
        info = self.compiler.get_language_info()
        
        about_text = f"""aurum IDE v1.0

{info['description']}

  Características del Compilador:
• Análisis léxico completo
• Análisis sintáctico con AST
• Análisis semántico con verificación de tipos
• Generación de código intermedio
• Intérprete de máquina virtual

  Características del Lenguaje:
• {', '.join(info['features'])}

  Tipos de datos: {', '.join(info['data_types']['simple'])}
  Total de palabras reservadas: {len(info['keywords'])}
  Operadores soportados: {len(info['operators']['arithmetic']) + len(info['operators']['comparison']) + len(info['operators']['logical'])}

Desarrollado como proyecto académico
Universidad Nacional - Sede Regional Brunca
Paradigmas de Programación"""
        
        messagebox.showinfo("Acerca de aurum", about_text)
            
    def run(self):
        """Ejecutar el IDE"""
        self.root.mainloop()

if __name__ == "__main__":
    ide = AurumIDE()
    ide.run()
