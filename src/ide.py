#!/usr/bin/env python3
"""
Alchemist IDE - Círculo de Transmutación Supremo
IDE épico inspirado en Fullmetal Alchemist Brotherhood
Con estilo alquímico en blanco y negro + modos oscuro/claro
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog, Menu
from PIL import Image, ImageTk
import os
from .lexer import AlchemistLexer
from .parser import AlchemistParser

class AlchemistIDE:
    """IDE épico para el lenguaje Alchemist con estilo alquímico"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Alchemist IDE - Círculo de Transmutación Supremo")
        self.root.geometry("1400x900")
        
        # Variables para el estado del IDE
        self.current_file = None
        self.code_modified = False
        self.dark_mode = True  # Modo por defecto
        self.bg_image = None
        self.bg_photo = None
        
        # Configurar estilos
        self.setup_styles()
        
        # Inicializar componentes
        self.setup_menu()
        self.setup_ui()
        self.setup_bindings()
        
    def setup_styles(self):
        """Configura los estilos según el modo"""
        if self.dark_mode:
            self.colors = {
                'bg_primary': '#000000',     # Negro principal
                'bg_secondary': '#1a1a1a',   # Negro secundario
                'bg_accent': '#333333',      # Gris oscuro
                'fg_primary': '#ffffff',     # Blanco principal
                'fg_secondary': '#cccccc',   # Gris claro
                'fg_accent': '#888888',      # Gris medio
                'select_bg': '#444444',      # Selección
                'select_fg': '#ffffff',      # Texto seleccionado
                'button_bg': '#2a2a2a',      # Botones
                'button_fg': '#ffffff',      # Texto botones
                'button_active': '#404040'   # Botones activos
            }
        else:
            self.colors = {
                'bg_primary': '#ffffff',     # Blanco principal
                'bg_secondary': '#f0f0f0',   # Gris muy claro
                'bg_accent': '#e0e0e0',      # Gris claro
                'fg_primary': '#000000',     # Negro principal
                'fg_secondary': '#333333',   # Gris oscuro
                'fg_accent': '#666666',      # Gris medio
                'select_bg': '#cccccc',      # Selección
                'select_fg': '#000000',      # Texto seleccionado
                'button_bg': '#d0d0d0',      # Botones
                'button_fg': '#000000',      # Texto botones
                'button_active': '#c0c0c0'   # Botones activos
            }
        
        self.root.configure(bg=self.colors['bg_primary'])
        
    def setup_menu(self):
        """Configura el menú principal con estilo alquímico"""
        menubar = Menu(self.root, bg=self.colors['bg_secondary'], fg=self.colors['fg_primary'], 
                      activebackground=self.colors['button_active'])
        self.root.config(menu=menubar)
        
        # Menú Archivo
        file_menu = Menu(menubar, tearoff=0, bg=self.colors['bg_secondary'], fg=self.colors['fg_primary'])
        menubar.add_cascade(label="Archivo", menu=file_menu)
        file_menu.add_command(label="Nuevo", command=self.new_file, accelerator="Ctrl+N")
        file_menu.add_command(label="Abrir", command=self.open_file, accelerator="Ctrl+O")
        file_menu.add_command(label="Guardar", command=self.save_file, accelerator="Ctrl+S")
        file_menu.add_separator()
        file_menu.add_command(label="Cargar Imagen de Fondo", command=self.load_background_image)
        file_menu.add_command(label="Quitar Imagen de Fondo", command=self.remove_background_image)
        file_menu.add_separator()
        file_menu.add_command(label="Salir", command=self.root.quit)
        
        # Menú Herramientas
        tools_menu = Menu(menubar, tearoff=0, bg=self.colors['bg_secondary'], fg=self.colors['fg_primary'])
        menubar.add_cascade(label="Herramientas", menu=tools_menu)
        tools_menu.add_command(label="Analizar Elementos", command=self.test_lexer)
        tools_menu.add_command(label="Verificar Estructura", command=self.test_parser)
        
        # Menú Apariencia
        view_menu = Menu(menubar, tearoff=0, bg=self.colors['bg_secondary'], fg=self.colors['fg_primary'])
        menubar.add_cascade(label="Apariencia", menu=view_menu)
        view_menu.add_command(label="Modo Oscuro", command=lambda: self.toggle_theme(True))
        view_menu.add_command(label="Modo Claro", command=lambda: self.toggle_theme(False))
        
        # Ayuda
        menubar.add_command(label="Acerca de", command=self.show_about)
        
    def setup_ui(self):
        """Configura la interfaz principal con estilo alquímico"""
        # Frame principal
        main_frame = tk.Frame(self.root, bg=self.colors['bg_primary'])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Título del IDE
        title_frame = tk.Frame(main_frame, bg=self.colors['bg_accent'], relief=tk.RAISED, bd=3)
        title_frame.pack(fill=tk.X, pady=(0, 10))
         
        self.setup_button_panel(main_frame)
        
        # Panel principal dividido
        main_paned = tk.PanedWindow(main_frame, orient=tk.HORIZONTAL, bg=self.colors['bg_primary'], 
                                   sashwidth=6, sashrelief=tk.RAISED)
        main_paned.pack(fill=tk.BOTH, expand=True)
        
        # Frame izquierdo para editor
        left_frame = tk.Frame(main_paned, bg=self.colors['bg_primary'])
        main_paned.add(left_frame, width=800)
        
        # Frame derecho para output
        right_frame = tk.Frame(main_paned, bg=self.colors['bg_primary'])
        main_paned.add(right_frame, width=600)
        
        self.setup_code_editor(left_frame)
        self.setup_output_panel(right_frame)
        
    def setup_button_panel(self, parent):
        """Configura el panel de botones (versión compacta)"""
        button_frame = tk.Frame(parent, bg=self.colors['bg_secondary'], relief=tk.RIDGE, bd=2)
        button_frame.pack(fill=tk.X, pady=(0, 3))
        
        # Botones principales - más compactos
        tk.Button(
            button_frame,
            text="Analizar Elementos",
            command=self.test_lexer,
            font=('Arial', 9, 'bold'),
            bg=self.colors['button_bg'],
            fg=self.colors['button_fg'],
            activebackground=self.colors['button_active'],
            activeforeground=self.colors['fg_primary'],
            relief=tk.RAISED,
            bd=2,
            padx=12,
            pady=3
        ).pack(side=tk.LEFT, padx=4, pady=4)
        
        tk.Button(
            button_frame,
            text="Verificar Estructura",
            command=self.test_parser,
            font=('Arial', 9, 'bold'),
            bg=self.colors['button_bg'],
            fg=self.colors['button_fg'],
            activebackground=self.colors['button_active'],
            activeforeground=self.colors['fg_primary'],
            relief=tk.RAISED,
            bd=2,
            padx=12,
            pady=3
        ).pack(side=tk.LEFT, padx=4, pady=4)
        
        # Separador más pequeño
        separator = tk.Frame(button_frame, width=2, bg=self.colors['fg_accent'])
        separator.pack(side=tk.LEFT, fill=tk.Y, padx=8, pady=4)
        
        # Botones de ayuda - más compactos
        tk.Button(
            button_frame,
            text="Palabras Reservadas",
            command=self.show_reserved_words,
            font=('Arial', 9, 'bold'),
            bg=self.colors['bg_accent'],
            fg=self.colors['fg_primary'],
            activebackground=self.colors['button_active'],
            activeforeground=self.colors['fg_primary'],
            relief=tk.RAISED,
            bd=2,
            padx=12,
            pady=3
        ).pack(side=tk.LEFT, padx=4, pady=4)
        
        tk.Button(
            button_frame,
            text="Sintaxis",
            command=self.show_control_syntax,
            font=('Arial', 9, 'bold'),
            bg=self.colors['bg_accent'],
            fg=self.colors['fg_primary'],
            activebackground=self.colors['button_active'],
            activeforeground=self.colors['fg_primary'],
            relief=tk.RAISED,
            bd=2,
            padx=12,
            pady=3
        ).pack(side=tk.LEFT, padx=4, pady=4)
        
        tk.Button(
            button_frame,
            text="Ejemplos",
            command=self.load_example,
            font=('Arial', 9, 'bold'),
            bg=self.colors['bg_accent'],
            fg=self.colors['fg_primary'],
            activebackground=self.colors['button_active'],
            activeforeground=self.colors['fg_primary'],
            relief=tk.RAISED,
            bd=2,
            padx=12,
            pady=3
        ).pack(side=tk.LEFT, padx=4, pady=4)
        
    def setup_code_editor(self, parent):
        """Configura el editor de código con soporte para imagen de fondo centrada"""
        # Marco del editor
        editor_frame = tk.LabelFrame(
            parent,
            text="Editor de Código",
            font=('Arial', 10, 'bold'),  # Fuente más pequeña
            bg=self.colors['bg_secondary'],
            fg=self.colors['fg_primary'],
            relief=tk.RIDGE,
            bd=3
        )
        editor_frame.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)
        
        # Frame para imagen de fondo
        self.editor_bg_frame = tk.Frame(editor_frame, bg=self.colors['bg_primary'])
        self.editor_bg_frame.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)
        
        # Editor de texto con fuente más pequeña
        self.code_editor = scrolledtext.ScrolledText(
            self.editor_bg_frame,
            wrap=tk.NONE,
            font=('Consolas', 10),  # Fuente más pequeña
            bg=self.colors['bg_primary'],
            fg=self.colors['fg_primary'],
            insertbackground=self.colors['fg_primary'],
            selectbackground=self.colors['select_bg'],
            selectforeground=self.colors['select_fg'],
            relief=tk.SUNKEN,
            bd=3
        )
        self.code_editor.pack(fill=tk.BOTH, expand=True)
        
        # Código inicial más compacto
        initial_code = """// BIENVENIDO AL CÍRCULO DE TRANSMUTACIÓN SUPREMO
// Inspirado en Fullmetal Alchemist Brotherhood

Transmutation GateOfTruth() -> void {
    Transmute("CÍRCULO DE TRANSMUTACIÓN ACTIVADO")
    
    // Variables alquímicas básicas
    Inscription alquimista = "Edward Elric"
    Solid edad = 16
    Principle esAlquimista = Accepted
    
    Transmute("Alquimista: " + alquimista)
    Transmute("Edad: " + edad + " años")
    
    // Observación de condiciones
    Observe (edad >= 15 and esAlquimista == Accepted) {
        Transmute("ACCESO CONCEDIDO AL ARTE SAGRADO")
        
        // Ciclo alquímico
        AlchemicCycle (Solid circulo = 1; circulo <= 3; circulo = circulo + 1) {
            Transmute("Círculo " + circulo + " ACTIVADO")
        }
    } Inevitably {
        Transmute("ACCESO DENEGADO")
    }
    
    Transmute("INTERCAMBIO EQUIVALENTE COMPLETADO")
}"""
    
        self.code_editor.insert('1.0', initial_code)
        
    def setup_output_panel(self, parent):
        """Configura el panel de salida con soporte para imagen de fondo"""
        # Notebook para tabs
        self.notebook = ttk.Notebook(parent)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=6, pady=6)
        
        # Configurar estilo del notebook
        style = ttk.Style()
        if self.dark_mode:
            style.configure('TNotebook', background=self.colors['bg_secondary'])
            style.configure('TNotebook.Tab', background=self.colors['bg_accent'], 
                          foreground=self.colors['fg_primary'])
        else:
            style.configure('TNotebook', background=self.colors['bg_secondary'])
            style.configure('TNotebook.Tab', background=self.colors['bg_accent'], 
                          foreground=self.colors['fg_primary'])
        
        # Tab de errores
        error_frame = tk.Frame(self.notebook, bg=self.colors['bg_secondary'])
        self.notebook.add(error_frame, text="Errores")
        
        error_label = tk.Label(
            error_frame,
            text="Análisis de Errores",
            font=('Arial', 12, 'bold'),
            bg=self.colors['bg_secondary'],
            fg=self.colors['fg_primary']
        )
        error_label.pack(anchor=tk.W, padx=8, pady=8)
        
        # Frame para imagen de fondo de errores
        self.error_bg_frame = tk.Frame(error_frame, bg=self.colors['bg_primary'])
        self.error_bg_frame.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)
        
        self.error_output = scrolledtext.ScrolledText(
            self.error_bg_frame,
            font=('Consolas', 9),  # Fuente más pequeña
            bg=self.colors['bg_primary'],
            fg=self.colors['fg_secondary'],
            relief=tk.SUNKEN,
            bd=3
        )
        self.error_output.pack(fill=tk.BOTH, expand=True)
        
        # Tab de resultados
        output_frame = tk.Frame(self.notebook, bg=self.colors['bg_secondary'])
        self.notebook.add(output_frame, text="Salida")
        
        output_label = tk.Label(
            output_frame,
            text="Resultados de Análisis",
            font=('Arial', 12, 'bold'),
            bg=self.colors['bg_secondary'],
            fg=self.colors['fg_primary']
        )
        output_label.pack(anchor=tk.W, padx=8, pady=8)
        
        # Frame para imagen de fondo de salida
        self.output_bg_frame = tk.Frame(output_frame, bg=self.colors['bg_primary'])
        self.output_bg_frame.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)
        
        self.program_output = scrolledtext.ScrolledText(
            self.output_bg_frame,
            font=('Consolas', 9),  # Fuente más pequeña
            bg=self.colors['bg_primary'],
            fg=self.colors['fg_primary'],
            relief=tk.SUNKEN,
            bd=3
        )
        self.program_output.pack(fill=tk.BOTH, expand=True)
        
        # Tab de información
        info_frame = tk.Frame(self.notebook, bg=self.colors['bg_secondary'])
        self.notebook.add(info_frame, text="Información")
        
        info_label = tk.Label(
            info_frame,
            text="Documentación del Lenguaje",
            font=('Arial', 12, 'bold'),
            bg=self.colors['bg_secondary'],
            fg=self.colors['fg_primary']
        )
        info_label.pack(anchor=tk.W, padx=8, pady=8)
        
        # Frame para imagen de fondo de info
        self.info_bg_frame = tk.Frame(info_frame, bg=self.colors['bg_primary'])
        self.info_bg_frame.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)
        
        self.info_output = scrolledtext.ScrolledText(
            self.info_bg_frame,
            font=('Consolas', 9),  # Fuente más pequeña
            bg=self.colors['bg_primary'],
            fg=self.colors['fg_secondary'],
            relief=tk.SUNKEN,
            bd=3
        )
        self.info_output.pack(fill=tk.BOTH, expand=True)
        
        # Mostrar información de bienvenida
        self.show_welcome_info()
        
    def setup_bindings(self):
        """Configura los atajos de teclado"""
        self.root.bind('<Control-n>', lambda e: self.new_file())
        self.root.bind('<Control-o>', lambda e: self.open_file())
        self.root.bind('<Control-s>', lambda e: self.save_file())
        self.root.bind('<F9>', lambda e: self.test_lexer())
        self.root.bind('<F5>', lambda e: self.test_parser())
        
    # ========================================
    # MÉTODOS DE ARCHIVO
    # ========================================
    
    def new_file(self):
        """Crear nuevo archivo"""
        self.code_editor.delete('1.0', tk.END)
        self.current_file = None
        self.clear_outputs()
        
    def open_file(self):
        """Abrir archivo existente"""
        file_path = filedialog.askopenfilename(
            title="Abrir archivo Alchemist",
            filetypes=[("Archivos Alchemist", "*.alc"), ("Todos los archivos", "*.*")]
        )
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    content = file.read()
                    self.code_editor.delete('1.0', tk.END)
                    self.code_editor.insert('1.0', content)
                    self.current_file = file_path
                    self.clear_outputs()
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo abrir el archivo:\n{str(e)}")
                
    def save_file(self):
        """Guardar archivo actual"""
        if not self.current_file:
            self.current_file = filedialog.asksaveasfilename(
                title="Guardar archivo Alchemist",
                defaultextension=".alc",
                filetypes=[("Archivos Alchemist", "*.alc"), ("Todos los archivos", "*.*")]
            )
        
        if self.current_file:
            try:
                content = self.code_editor.get('1.0', tk.END)
                with open(self.current_file, 'w', encoding='utf-8') as file:
                    file.write(content)
                messagebox.showinfo("Éxito", "Archivo guardado correctamente")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo guardar:\n{str(e)}")
    
    # ========================================
    # GESTIÓN DE IMÁGENES DE FONDO
    # ========================================
    
    def load_background_image(self):
        """Cargar imagen de fondo"""
        file_path = filedialog.askopenfilename(
            title="Seleccionar imagen de fondo",
            filetypes=[
                ("Imágenes", "*.png *.jpg *.jpeg *.gif *.bmp"),
                ("PNG", "*.png"),
                ("JPEG", "*.jpg *.jpeg"),
                ("Todos los archivos", "*.*")
            ]
        )
        
        if file_path:
            try:
                # Cargar y redimensionar imagen a tamaño más pequeño y centrado
                image = Image.open(file_path)
                # Redimensionar a un tamaño más pequeño para que no ocupe todo el editor
                image = image.resize((300, 200), Image.Resampling.LANCZOS)
                self.bg_photo = ImageTk.PhotoImage(image)
                
                # Aplicar a todos los frames de fondo
                self.apply_background_image()
                
                messagebox.showinfo("Éxito", "Imagen de fondo aplicada")
                
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo cargar la imagen:\n{str(e)}")
    
    def apply_background_image(self):
        """Aplicar imagen de fondo centrada a los frames"""
        if self.bg_photo:
            # Aplicar al editor - imagen centrada y más pequeña
            bg_label_editor = tk.Label(self.editor_bg_frame, image=self.bg_photo, bg=self.colors['bg_primary'])
            # Centrar la imagen
            bg_label_editor.place(relx=0.5, rely=0.5, anchor='center')
            bg_label_editor.lower()
            
            # Hacer el editor semi-transparente para que se vea la imagen
            if self.dark_mode:
                self.code_editor.configure(bg='#000000', highlightbackground=self.colors['bg_primary'])
            else:
                self.code_editor.configure(bg='#ffffff', highlightbackground=self.colors['bg_primary'])
            
            # Aplicar a paneles de salida también centrados
            bg_label_output = tk.Label(self.output_bg_frame, image=self.bg_photo, bg=self.colors['bg_primary'])
            bg_label_output.place(relx=0.5, rely=0.5, anchor='center')
            bg_label_output.lower()
            
            bg_label_error = tk.Label(self.error_bg_frame, image=self.bg_photo, bg=self.colors['bg_primary'])
            bg_label_error.place(relx=0.5, rely=0.5, anchor='center')
            bg_label_error.lower()
            
            bg_label_info = tk.Label(self.info_bg_frame, image=self.bg_photo, bg=self.colors['bg_primary'])
            bg_label_info.place(relx=0.5, rely=0.5, anchor='center')
            bg_label_info.lower()
    
    def remove_background_image(self):
        """Quitar imagen de fondo"""
        self.bg_photo = None
        # Limpiar todos los labels de fondo
        for widget in self.editor_bg_frame.winfo_children():
            if isinstance(widget, tk.Label):
                widget.destroy()
        for widget in self.output_bg_frame.winfo_children():
            if isinstance(widget, tk.Label):
                widget.destroy()
        for widget in self.error_bg_frame.winfo_children():
            if isinstance(widget, tk.Label):
                widget.destroy()
        for widget in self.info_bg_frame.winfo_children():
            if isinstance(widget, tk.Label):
                widget.destroy()
        
        # Restaurar colores originales
        self.code_editor.configure(bg=self.colors['bg_primary'])
        messagebox.showinfo("Éxito", "Imagen de fondo eliminada")
    
    # ========================================
    # GESTIÓN DE TEMAS
    # ========================================
    
    def toggle_theme(self, dark_mode):
        """Cambiar entre modo oscuro y claro"""
        self.dark_mode = dark_mode
        self.setup_styles()
        self.refresh_ui()
        
    def refresh_ui(self):
        """Refrescar la interfaz con nuevos colores"""
        # Actualizar todos los widgets principales
        self.root.configure(bg=self.colors['bg_primary'])
        
        # Actualizar editor
        self.code_editor.configure(
            bg=self.colors['bg_primary'],
            fg=self.colors['fg_primary'],
            insertbackground=self.colors['fg_primary'],
            selectbackground=self.colors['select_bg'],
            selectforeground=self.colors['select_fg']
        )
        
        # Actualizar paneles de salida
        self.error_output.configure(
            bg=self.colors['bg_primary'],
            fg=self.colors['fg_secondary']
        )
        
        self.program_output.configure(
            bg=self.colors['bg_primary'],
            fg=self.colors['fg_primary']
        )
        
        self.info_output.configure(
            bg=self.colors['bg_primary'],
            fg=self.colors['fg_secondary']
        )
        
        # Reaplicar imagen de fondo si existe
        if self.bg_photo:
            self.apply_background_image()
    
    # ========================================
    # ANÁLISIS
    # ========================================
    
    def test_lexer(self):
        """Analizar elementos del código"""
        self.clear_outputs()
        code = self.code_editor.get('1.0', tk.END)
        
        try:
            lexer = AlchemistLexer()
            tokens = lexer.tokenize(code)
            
            output = "=== ANÁLISIS LÉXICO ===\n\n"
            output += f"Total de tokens: {len(tokens)}\n\n"
            
            # Contar tipos de tokens
            token_counts = {}
            for token in tokens:
                if token.type.name not in ['WHITESPACE', 'COMMENT']:
                    token_counts[token.type.name] = token_counts.get(token.type.name, 0) + 1
            
            output += "Tokens por tipo:\n"
            for token_type, count in sorted(token_counts.items()):
                output += f"   {token_type}: {count}\n"
            
            output += "\nSecuencia de tokens (primeros 30):\n"
            count = 0
            for token in tokens:
                if token.type.name not in ['WHITESPACE', 'NEWLINE'] and count < 30:
                    output += f"{count+1:3d}. {token.type.name:15} -> '{token.value}'\n"
                    count += 1
                    
            output += "\nAnálisis léxico completado."
            
            self.program_output.delete('1.0', tk.END)
            self.program_output.insert('1.0', output)
            
        except Exception as e:
            error_msg = f"ERROR EN ANÁLISIS LÉXICO:\n\n{str(e)}"
            self.error_output.delete('1.0', tk.END)
            self.error_output.insert('1.0', error_msg)
            
    def test_parser(self):
        """Verificar estructura del código"""
        self.clear_outputs()
        code = self.code_editor.get('1.0', tk.END)
        
        try:
            parser = AlchemistParser()
            ast = parser.parse(code)
            
            output = "=== ANÁLISIS SINTÁCTICO ===\n\n"
            output += f"Funciones encontradas: {len(ast.functions)}\n\n"
            
            for func in ast.functions:
                output += f"Función: {func.name}\n"
                params = ", ".join(f"{p.type} {p.name}" for p in func.parameters)
                output += f"   Parámetros: ({params})\n"
                output += f"   Retorna: {func.return_type}\n"
                output += f"   Declaraciones: {len(func.body)}\n\n"
                
            output += "Estructura sintáctica correcta."
            
            self.program_output.delete('1.0', tk.END)
            self.program_output.insert('1.0', output)
            
        except Exception as e:
            error_msg = f"ERROR EN ANÁLISIS SINTÁCTICO:\n\n{str(e)}"
            self.error_output.delete('1.0', tk.END)
            self.error_output.insert('1.0', error_msg)
    
    # ========================================
    # AYUDA Y EJEMPLOS
    # ========================================
    
    def show_welcome_info(self):
        """Mostrar información de bienvenida"""
        welcome = """BIENVENIDO A ALCHEMIST IDE

Lenguaje Alchemist - Inspirado en Fullmetal Alchemist Brotherhood

Función Principal: GateOfTruth()
Tipos: Solid, Liquid, Inscription, Principle
Valores: Accepted (true), Rejected (false)
I/O: Transmute(), Absorb()
Control: Observe, Alternatively, Inevitably
Ciclos: AlchemicCycle, TransmuteUntil
Funciones: Transmutation
Retorno: EquivalentExchange

"Para obtener algo, algo de igual valor debe ser perdido"

Características:
• Sintaxis inspirada en FMA
• Modos oscuro y claro
• Soporte para imágenes de fondo
• Análisis léxico y sintáctico
• Ejemplos incluidos

Comienza tu transmutación"""
        
        self.info_output.insert('1.0', welcome)
        
    def show_reserved_words(self):
        """Mostrar palabras reservadas"""
        content = """PALABRAS RESERVADAS DE ALCHEMIST

Definición de Funciones:
  Transmutation    // para definir funciones
  
Función Principal:
  GateOfTruth    // función principal

Retorno de Valores:
  EquivalentExchange    // para retornar valores

Tipos:
  Solid, Liquid, Inscription, Principle, void

Control:
  Observe, Alternatively, Inevitably
  AlchemicCycle, TransmuteUntil

I/O:
  Transmute, Absorb

Valores:
  Accepted, Rejected

Operadores:
  and, or, not, break, continue

Total: 20 palabras reservadas"""
        
        self.show_language_help("Palabras Reservadas", content)
        
    def show_control_syntax(self):
        """Mostrar sintaxis de control"""
        content = """SINTAXIS DE ALCHEMIST

Variables:
  Solid numero = 42
  Liquid decimal = 3.14
  Inscription texto = "hola"
  Principle verdadero = Accepted

Condicionales:
  Observe (condicion) {
      // código
  } Alternatively (otra) {
      // código
  } Inevitably {
      // código
  }

Ciclos:
  AlchemicCycle (Solid i = 0; i < 10; i = i + 1) {
      // código
  }
  
  TransmuteUntil (condicion) {
      // código
  }

Funciones:
  Transmutation GateOfTruth() -> void {
      // función principal
      EquivalentExchange  // retornar sin valor
  }
  
  Transmutation miFuncion() -> Solid {
      EquivalentExchange 42  // retornar valor
  }

I/O:
  Transmute("mensaje")
  Inscription x = Absorb("prompt")"""
        
        self.show_language_help("Sintaxis", content)
        
    def load_example(self):
        """Cargar ejemplos"""
        examples = {
            "Variables Básicas": '''Transmutation GateOfTruth() -> void {
    Solid nivel = 50
    Inscription nombre = "Edward"
    Principle activo = Accepted
    
    Transmute("Nivel: " + nivel)
    Transmute("Nombre: " + nombre)
}''',
            "Condicionales": '''Transmutation GateOfTruth() -> void {
    Solid edad = 16
    
    Observe (edad >= 18) {
        Transmute("Mayor de edad")
    } Alternatively (edad >= 15) {
        Transmute("Acceso limitado")
    } Inevitably {
        Transmute("Menor de edad")
    }
}''',
            "Ciclos": '''Transmutation GateOfTruth() -> void {
    Transmute("Activando círculos")
    
    AlchemicCycle (Solid i = 1; i <= 5; i = i + 1) {
        Transmute("Círculo " + i + " activado")
    }
}''',
            "Funciones": '''Transmutation GateOfTruth() -> void {
    Solid poder = calcularPoder(16)
    Transmute("Poder: " + poder)
}

Transmutation calcularPoder(Solid edad) -> Solid {
    EquivalentExchange edad * 25 + 100
}''',
            "Bucle While": '''Transmutation GateOfTruth() -> void {
    Solid energia = 100
    Solid ronda = 1
    
    TransmuteUntil (energia <= 20) {
        Transmute("Ronda " + ronda + " - Energía: " + energia)
        energia = energia - 15
        ronda = ronda + 1
    }
}''',
            "Entrada de Datos": '''Transmutation GateOfTruth() -> void {
    Transmute("Registro de alquimista")
    
    Inscription nombre = Absorb("Tu nombre: ")
    
    Transmute("Hola " + nombre)
}'''
        }
        
        self.show_example_window(examples)
        
    def show_example_window(self, examples):
        """Mostrar ventana de ejemplos"""
        window = tk.Toplevel(self.root)
        window.title("Ejemplos de Código")
        window.geometry("700x600")
        window.configure(bg=self.colors['bg_primary'])
        window.grab_set()
        
        # Título
        title_frame = tk.Frame(window, bg=self.colors['bg_accent'], relief=tk.RAISED, bd=4)
        title_frame.pack(fill=tk.X, padx=10, pady=10)
        
        title_label = tk.Label(
            title_frame,
            text="EJEMPLOS DE CÓDIGO ALCHEMIST",
            font=('Arial', 16, 'bold'),
            bg=self.colors['bg_accent'],
            fg=self.colors['fg_primary'],
            pady=10
        )
        title_label.pack()
        
        # Lista
        list_frame = tk.Frame(window, bg=self.colors['bg_secondary'], relief=tk.RIDGE, bd=3)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)
        
        listbox = tk.Listbox(
            list_frame,
            font=('Consolas', 11, 'bold'),
            bg=self.colors['bg_primary'],
            fg=self.colors['fg_primary'],
            selectbackground=self.colors['select_bg'],
            selectforeground=self.colors['select_fg'],
            relief=tk.SUNKEN,
            bd=2
        )
        listbox.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)
        
        for title in examples.keys():
            listbox.insert(tk.END, title)
        listbox.selection_set(0)
            
        # Botones
        button_frame = tk.Frame(window, bg=self.colors['bg_primary'])
        button_frame.pack(fill=tk.X, padx=15, pady=15)
        
        def load_selected():
            selection = listbox.curselection()
            if selection:
                title = listbox.get(selection[0])
                code = examples[title]
                
                if messagebox.askyesno(
                    "Cargar Ejemplo", 
                    f"¿Cargar el ejemplo '{title}'?\n\nEsto reemplazará el código actual.",
                    parent=window
                ):
                    self.code_editor.delete('1.0', tk.END)
                    self.code_editor.insert('1.0', code)
                    self.clear_outputs()
                    window.destroy()
                
        tk.Button(
            button_frame,
            text="CARGAR EJEMPLO",
            command=load_selected,
            font=('Arial', 12, 'bold'),
            bg=self.colors['button_bg'],
            fg=self.colors['button_fg'],
            activebackground=self.colors['button_active'],
            activeforeground=self.colors['fg_primary'],
            relief=tk.RAISED,
            bd=3,
            padx=20,
            pady=8
        ).pack(side=tk.LEFT, padx=(0, 15))
        
        tk.Button(
            button_frame,
            text="CERRAR",
            command=window.destroy,
            font=('Arial', 11),
            bg=self.colors['bg_accent'],
            fg=self.colors['fg_primary'],
            activebackground=self.colors['button_active'],
            activeforeground=self.colors['fg_primary'],
            relief=tk.RAISED,
            bd=3,
            padx=15,
            pady=8
        ).pack(side=tk.RIGHT)
        
    def show_language_help(self, title, content):
        """Mostrar ayuda"""
        window = tk.Toplevel(self.root)
        window.title(title)
        window.geometry("600x500")
        window.configure(bg=self.colors['bg_primary'])
        
        # Título
        title_frame = tk.Frame(window, bg=self.colors['bg_accent'], relief=tk.RAISED, bd=3)
        title_frame.pack(fill=tk.X, padx=8, pady=8)
        
        title_label = tk.Label(
            title_frame,
            text=title,
            font=('Arial', 14, 'bold'),
            bg=self.colors['bg_accent'],
            fg=self.colors['fg_primary'],
            pady=8
        )
        title_label.pack()
        
        # Contenido
        text = scrolledtext.ScrolledText(
            window, 
            bg=self.colors['bg_primary'], 
            fg=self.colors['fg_primary'],
            font=('Consolas', 10),
            relief=tk.SUNKEN,
            bd=3
        )
        text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        text.insert('1.0', content)
        text.config(state=tk.DISABLED)
        
    def show_about(self):
        """Mostrar acerca de"""
        about = """ALCHEMIST IDE

Versión: 3.0 Epic Edition
Estilo: Blanco y Negro con modos oscuro/claro
Inspirado en: Fullmetal Alchemist Brotherhood
Tema: Intercambio Equivalente

Características:
• Sintaxis inspirada en FMA
• Modos oscuro y claro
• Soporte para imágenes de fondo personalizadas
• Análisis léxico y sintáctico completo
• 20 palabras reservadas alquímicas
• Función principal GateOfTruth()
• Sistema I/O con Absorb() universal

Filosofía:
"Para obtener algo, algo de igual valor debe ser perdido"
"El conocimiento sin poder es inútil"
"El poder sin conocimiento es peligroso"

Desarrollado para verdaderos alquimistas"""
        
        messagebox.showinfo("Acerca de Alchemist IDE", about)
        
    def clear_outputs(self):
        """Limpiar salidas"""
        self.error_output.delete('1.0', tk.END)
        self.program_output.delete('1.0', tk.END)
        
    def run(self):
        """Ejecutar IDE"""
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()
        
    def on_closing(self):
        """Manejar cierre"""
        if messagebox.askokcancel("Cerrar", "¿Cerrar Alchemist IDE?"):
            self.root.destroy()

def main():
    """Función principal"""
    print("Iniciando Alchemist IDE...")
    ide = AlchemistIDE()
    ide.run()

if __name__ == "__main__":
    main()
