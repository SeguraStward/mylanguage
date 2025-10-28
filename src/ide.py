#!/usr/bin/env python3
"""
Alchemist IDE - Circulo de Transmutacion Supremo
IDE minimalista inspirado en Fullmetal Alchemist Brotherhood
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog, Menu
import os
import sys

# Agregar el directorio padre al path para importar modulos
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.lexer import AlchemistLexer
from src.parser import AlchemistParser

class AlchemistIDE:
    """IDE minimalista para el lenguaje Alchemist"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Alchemist IDE")
        self.root.geometry("1400x900")
        
        # Variables para el estado del IDE
        self.current_file = None
        self.code_modified = False
        self.dark_mode = True  # Modo por defecto
        
        # Configurar estilos
        self.setup_styles()
        
        # Inicializar componentes
        self.setup_menu()
        self.setup_ui()
        self.setup_bindings()
        
    def setup_styles(self):
        """Configura los estilos con colores puros blanco y negro"""
        # Fuente alquimica bold y minimalista
        self.fonts = {
            'main': ('Trebuchet MS', 11, 'bold'),      # Fuente principal
            'code': ('Consolas', 10, 'bold'),          # Editor de codigo
            'menu': ('Trebuchet MS', 9, 'bold'),       # Menús
            'title': ('Trebuchet MS', 12, 'bold'),     # Titulos
            'button': ('Trebuchet MS', 9, 'bold')      # Botones
        }
        
        if self.dark_mode:
            self.colors = {
                'bg_primary': '#000000',        # Negro puro
                'fg_primary': '#FFFFFF',        # Blanco puro
                'bg_secondary': '#000000',      # Negro puro para areas secundarias
                'fg_secondary': '#FFFFFF',      # Blanco puro
                'border': '#FFFFFF',            # Bordes blancos
                'button_bg': '#000000',         # Botones negros
                'button_fg': '#FFFFFF',         # Texto blanco en botones
                'button_active': '#333333',     # Boton activo
                'select_bg': '#FFFFFF',         # Seleccion blanca
                'select_fg': '#000000',         # Texto negro en seleccion
                'tab_bg': '#FFFFFF',            # Tabs blancos puros
                'tab_fg': '#000000',            # Texto negro en tabs
                'tab_active_bg': '#FFFFFF',     # Tab activo blanco
                'tab_active_fg': '#000000'      # Texto negro en tab activo
            }
        else:
            self.colors = {
                'bg_primary': '#FFFFFF',        # Blanco puro
                'fg_primary': '#000000',        # Negro puro
                'bg_secondary': '#FFFFFF',      # Blanco puro para areas secundarias
                'fg_secondary': '#000000',      # Negro puro
                'border': '#000000',            # Bordes negros
                'button_bg': '#FFFFFF',         # Botones blancos
                'button_fg': '#000000',         # Texto negro en botones
                'button_active': '#CCCCCC',     # Boton activo
                'select_bg': '#000000',         # Seleccion negra
                'select_fg': '#FFFFFF',         # Texto blanco en seleccion
                'tab_bg': '#FFFFFF',            # Tabs blancos puros
                'tab_fg': '#000000',            # Texto negro en tabs
                'tab_active_bg': '#FFFFFF',     # Tab activo blanco
                'tab_active_fg': '#000000'      # Texto negro en tab activo
            }
        
        # Configurar el root
        self.root.configure(bg=self.colors['bg_primary'])
        
    def setup_menu(self):
        """Configura la barra de menú con todos los botones integrados"""
        menubar = Menu(self.root, 
                      bg=self.colors['bg_primary'], 
                      fg=self.colors['fg_primary'],
                      font=self.fonts['menu'])
        self.root.config(menu=menubar)
        
        # Menú Archivo
        file_menu = Menu(menubar, tearoff=0,
                        bg=self.colors['bg_primary'], 
                        fg=self.colors['fg_primary'],
                        font=self.fonts['menu'])
        menubar.add_cascade(label="Archivo", menu=file_menu)
        file_menu.add_command(label="Nuevo", command=self.new_file, accelerator="Ctrl+N")
        file_menu.add_command(label="Abrir", command=self.open_file, accelerator="Ctrl+O")
        file_menu.add_command(label="Guardar", command=self.save_file, accelerator="Ctrl+S")
        file_menu.add_command(label="Guardar Como", command=self.save_file_as, accelerator="Ctrl+Shift+S")
        file_menu.add_separator()
        file_menu.add_command(label="Salir", command=self.on_closing, accelerator="Ctrl+Q")
        
        # Menú Codigo (movido desde botones)
        code_menu = Menu(menubar, tearoff=0,
                        bg=self.colors['bg_primary'], 
                        fg=self.colors['fg_primary'],
                        font=self.fonts['menu'])
        menubar.add_cascade(label="Analisis", menu=code_menu)
        code_menu.add_command(label="Analisis Lexico", command=self.lexical_analysis, accelerator="F6")
        code_menu.add_command(label="Analisis Sintactico", command=self.syntactic_analysis, accelerator="F7")
        code_menu.add_separator()
        code_menu.add_command(label="Limpiar Salidas", command=self.clear_outputs)
        
        # Menú Ejemplos (movido desde botones)
        examples_menu = Menu(menubar, tearoff=0,
                           bg=self.colors['bg_primary'], 
                           fg=self.colors['fg_primary'],
                           font=self.fonts['menu'])
        menubar.add_cascade(label="Ejemplos", menu=examples_menu)
        examples_menu.add_command(label="Cargar Ejemplo", command=self.load_example)
        
        # Menú Ayuda (movido desde botones)
        help_menu = Menu(menubar, tearoff=0,
                        bg=self.colors['bg_primary'], 
                        fg=self.colors['fg_primary'],
                        font=self.fonts['menu'])
        menubar.add_cascade(label="Ayuda", menu=help_menu)
        help_menu.add_command(label="Palabras Sagradas", command=self.show_reserved_words)
        help_menu.add_command(label="Sintaxis", command=self.show_control_syntax) 
        
        # Menú Apariencia
        view_menu = Menu(menubar, tearoff=0,
                        bg=self.colors['bg_primary'], 
                        fg=self.colors['fg_primary'],
                        font=self.fonts['menu'])
        menubar.add_cascade(label="Apariencia", menu=view_menu)
        view_menu.add_command(label="Modo Oscuro", command=lambda: self.toggle_theme(True))
        view_menu.add_command(label="Modo Claro", command=lambda: self.toggle_theme(False))
        
    def setup_ui(self):
        """Configura la interfaz de usuario minimalista"""
        # Frame principal sin titulo grande
        main_frame = tk.Frame(self.root, bg=self.colors['bg_primary'])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Panel superior: Editor de codigo
        self.setup_code_editor(main_frame)
        
        # Panel inferior: Salidas con notebook y tabs blancos
        self.setup_output_panel(main_frame)
        
    def setup_code_editor(self, parent):
        """Configura el editor de codigo minimalista"""
        # Frame del editor
        editor_frame = tk.LabelFrame(
            parent,
            text="Editor de Codigo",
            font=self.fonts['title'],
            bg=self.colors['bg_primary'],
            fg=self.colors['fg_primary'],
            relief=tk.SOLID,
            bd=1
        )
        editor_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 5))
        
        # Editor de texto
        self.code_editor = scrolledtext.ScrolledText(
            editor_frame,
            wrap=tk.NONE,
            font=self.fonts['code'],
            bg=self.colors['bg_primary'],
            fg=self.colors['fg_primary'],
            insertbackground=self.colors['fg_primary'],
            selectbackground=self.colors['select_bg'],
            selectforeground=self.colors['select_fg'],
            relief=tk.FLAT,
            bd=0,
            highlightthickness=1,
            highlightcolor=self.colors['border']
        )
        self.code_editor.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Codigo inicial minimalista
        initial_code = """// CIRCULO DE TRANSMUTACION
Transmutation GateOfTruth() -> void {
    Solid power = 100
    Inscription name = "Edward Elric"
    
    Transmute("Poder: " + power)
    Transmute("Alquimista: " + name)
    
    Observe (power > 50) {
        Transmute("Transmutacion exitosa")
    }
}"""
        
        self.code_editor.insert('1.0', initial_code)
        
    def setup_output_panel(self, parent):
        """Configura el panel de salidas con tabs blancos puros"""
        # Frame para las salidas
        output_frame = tk.Frame(parent, bg=self.colors['bg_primary'])
        output_frame.pack(fill=tk.BOTH, expand=False, pady=(5, 0))
        
        # Notebook con estilo personalizado para tabs blancos
        self.setup_notebook_style()
        
        self.notebook = ttk.Notebook(output_frame, style='Custom.TNotebook')
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Tab 1: Informacion
        info_frame = tk.Frame(self.notebook, bg=self.colors['bg_primary'])
        self.notebook.add(info_frame, text=" Informacion")
        
        self.info_output = scrolledtext.ScrolledText(
            info_frame,
            height=15,
            font=self.fonts['main'],
            bg=self.colors['bg_primary'],
            fg=self.colors['fg_primary'],
            relief=tk.FLAT,
            bd=0
        )
        self.info_output.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Tab 2: Errores
        error_frame = tk.Frame(self.notebook, bg=self.colors['bg_primary'])
        self.notebook.add(error_frame, text=" Errores")
        
        self.error_output = scrolledtext.ScrolledText(
            error_frame,
            height=15,
            font=self.fonts['main'],
            bg=self.colors['bg_primary'],
            fg=self.colors['fg_primary'],
            relief=tk.FLAT,
            bd=0
        )
        self.error_output.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Tab 3: Programa
        program_frame = tk.Frame(self.notebook, bg=self.colors['bg_primary'])
        self.notebook.add(program_frame, text=" Programa")
        
        self.program_output = scrolledtext.ScrolledText(
            program_frame,
            height=15,
            font=self.fonts['main'],
            bg=self.colors['bg_primary'],
            fg=self.colors['fg_primary'],
            relief=tk.FLAT,
            bd=0
        )
        self.program_output.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Mostrar informacion de bienvenida
        self.show_welcome_info()
        
    def setup_notebook_style(self):
        """Configura estilo personalizado para tabs blancos puros"""
        style = ttk.Style()
        
        # Configurar tema basico
        style.theme_use('clam')
        
        # Estilo para el notebook con tabs blancos puros
        style.configure('Custom.TNotebook', 
                       background=self.colors['bg_primary'],
                       borderwidth=0,
                       relief='flat')
        
        style.configure('Custom.TNotebook.Tab',
                       background=self.colors['tab_bg'],          # Blanco puro
                       foreground=self.colors['tab_fg'],          # Negro
                       padding=[10, 5],
                       font=self.fonts['menu'],
                       borderwidth=1,
                       relief='solid')
        
        # Tab activo
        style.map('Custom.TNotebook.Tab',
                 background=[('selected', self.colors['tab_active_bg'])],  # Blanco puro
                 foreground=[('selected', self.colors['tab_active_fg'])],  # Negro
                 borderwidth=[('selected', 2)])
        
    def setup_bindings(self):
        """Configura los atajos de teclado"""
        self.root.bind('<Control-n>', lambda e: self.new_file())
        self.root.bind('<Control-o>', lambda e: self.open_file())
        self.root.bind('<Control-s>', lambda e: self.save_file())
        self.root.bind('<Control-Shift-S>', lambda e: self.save_file_as())
        self.root.bind('<Control-q>', lambda e: self.on_closing())
        self.root.bind('<F6>', lambda e: self.lexical_analysis())
        self.root.bind('<F7>', lambda e: self.syntactic_analysis())
        
        # Detectar cambios en el codigo
        self.code_editor.bind('<KeyPress>', self.on_text_change)
        self.code_editor.bind('<Button-1>', self.on_text_change)
        
    def on_text_change(self, event=None):
        """Detectar cambios en el codigo"""
        self.code_modified = True
        self.update_title()
        
    def update_title(self):
        """Actualizar titulo de la ventana"""
        title = "Alchemist IDE"
        if self.current_file:
            title += f" - {os.path.basename(self.current_file)}"
        if self.code_modified:
            title += " *"
        self.root.title(title)
        
    # ========================================
    # OPERACIONES DE ARCHIVO
    # ========================================
    
    def new_file(self):
        """Crear nuevo archivo"""
        if self.code_modified:
            if not messagebox.askyesno("Archivo sin guardar", 
                                     "¿Guardar cambios antes de crear uno nuevo?"):
                return
        
        self.code_editor.delete('1.0', tk.END)
        self.current_file = None
        self.code_modified = False
        self.clear_outputs()
        self.update_title()
        
    def open_file(self):
        """Abrir archivo"""
        file_path = filedialog.askopenfilename(
            title="Abrir archivo Alchemist",
            filetypes=[("Archivos Alchemist", "*.alch"), ("Todos los archivos", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    content = file.read()
                
                self.code_editor.delete('1.0', tk.END)
                self.code_editor.insert('1.0', content)
                
                self.current_file = file_path
                self.code_modified = False
                self.update_title()
                self.clear_outputs()
                
            except Exception as e:
                messagebox.showerror("Error", f"Error al abrir archivo: {e}")
                
    def save_file(self):
        """Guardar archivo"""
        if not self.current_file:
            return self.save_file_as()
        
        try:
            content = self.code_editor.get('1.0', tk.END)
            with open(self.current_file, 'w', encoding='utf-8') as file:
                file.write(content)
            
            self.code_modified = False
            self.update_title()
            messagebox.showinfo("exito", "Archivo guardado correctamente")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar archivo: {e}")
            
    def save_file_as(self):
        """Guardar archivo como"""
        file_path = filedialog.asksaveasfilename(
            title="Guardar archivo Alchemist",
            defaultextension=".alch",
            filetypes=[("Archivos Alchemist", "*.alch"), ("Todos los archivos", "*.*")]
        )
        
        if file_path:
            self.current_file = file_path
            self.save_file()
            
    # ========================================
    # ANALISIS DE CODIGO
    # ========================================
    
    def lexical_analysis(self):
        """Realizar solo analisis lexico"""
        self.clear_outputs()
        code = self.code_editor.get('1.0', tk.END).strip()
        
        if not code:
            self.error_output.insert('1.0', "No hay codigo para analizar")
            return
        
        try:
            lexer = AlchemistLexer()
            tokens = lexer.tokenize(code)
            
            self.info_output.insert('1.0', "ANaLISIS LeXICO COMPLETADO\n")
            self.info_output.insert(tk.END, f"Tokens generados: {len(tokens)}\n\n")
            
            # Mostrar tokens agrupados por tipo
            token_counts = {}
            token_list = []
            
            for token in tokens:
                token_type = token.type.name
                token_counts[token_type] = token_counts.get(token_type, 0) + 1
                token_list.append(f"  {token.type.name}: '{token.value}' (linea {token.line})")
            
            self.info_output.insert(tk.END, "Resumen por tipo:\n")
            for token_type, count in sorted(token_counts.items()):
                self.info_output.insert(tk.END, f"  {token_type}: {count}\n")
            
            self.info_output.insert(tk.END, "\nListado completo de tokens:\n")
            for token_info in token_list:
                self.info_output.insert(tk.END, f"{token_info}\n")
            
            self.info_output.insert(tk.END, "\nANaLISIS LeXICO EXITOSO")
            
        except Exception as e:
            self.error_output.insert('1.0', f"Error en analisis lexico: {str(e)}")
    
    def syntactic_analysis(self):
        """Realizar solo analisis sintactico (requiere que el lexico sea exitoso)"""
        self.clear_outputs()
        code = self.code_editor.get('1.0', tk.END).strip()
        
        if not code:
            self.error_output.insert('1.0', "No hay codigo para analizar")
            return
        
        try:
            # Primero verificar que el analisis lexico funcione
            lexer = AlchemistLexer()
            tokens = lexer.tokenize(code)
            
            # Realizar analisis sintactico
            parser = AlchemistParser()
            ast = parser.parse(code)
            
            self.info_output.insert('1.0', "ANALISIS SINTACTICO COMPLETADO\n")
            self.info_output.insert(tk.END, "="*50 + "\n\n")
            self.info_output.insert(tk.END, f"Funciones encontradas: {len(ast.functions)}\n\n")
            
            # Mostrar estructura del AST
            self.info_output.insert(tk.END, "ESTRUCTURA DEL AST:\n")
            self.info_output.insert(tk.END, "-"*30 + "\n")
            ast_structure = self._get_ast_structure(ast, 0)
            self.info_output.insert(tk.END, ast_structure)
            
            self.info_output.insert(tk.END, "\n" + "="*50 + "\n")
            self.info_output.insert(tk.END, "ANALISIS SINTACTICO EXITOSO")
            
        except Exception as e:
            self.error_output.insert('1.0', f"Error en analisis sintactico: {str(e)}")
    
    def _get_ast_structure(self, node, indent=0):
        """Generar representación en texto de la estructura del AST"""
        from src.parser import Program, Function, VariableDeclaration, Assignment, ObserveStatement, ForStatement, WhileStatement, ReturnStatement, ExpressionStatement, FunctionCall, BinaryOperation, UnaryOperation, Literal, Variable, AlternativelyPart
        
        result = ""
        prefix = "  " * indent
        
        if isinstance(node, Program):
            result += f"{prefix}Program\n"
            for func in node.functions:
                result += self._get_ast_structure(func, indent + 1)
        
        elif isinstance(node, Function):
            params = ", ".join(f'{p.type} {p.name}' for p in node.parameters)
            result += f"{prefix}Function: {node.name}({params}) -> {node.return_type}\n"
            for stmt in node.body:
                result += self._get_ast_structure(stmt, indent + 1)
        
        elif isinstance(node, VariableDeclaration):
            init_val = f" = {node.value.value if hasattr(node.value, 'value') else 'expr'}" if node.value else ""
            result += f"{prefix}VariableDeclaration: {node.type} {node.name}{init_val}\n"
            if node.value:
                result += self._get_ast_structure(node.value, indent + 1)
        
        elif isinstance(node, Assignment):
            result += f"{prefix}Assignment: {node.name} = \n"
            result += self._get_ast_structure(node.value, indent + 1)
        
        elif isinstance(node, ObserveStatement):
            result += f"{prefix}ObserveStatement\n"
            result += f"{prefix}  Condition:\n"
            result += self._get_ast_structure(node.condition, indent + 2)
            result += f"{prefix}  Then:\n"
            for stmt in node.then_body:
                result += self._get_ast_structure(stmt, indent + 2)
            
            if hasattr(node, 'alternatively_parts') and node.alternatively_parts:
                for alt in node.alternatively_parts:
                    result += f"{prefix}  Alternatively:\n"
                    result += self._get_ast_structure(alt.condition, indent + 2)
                    for stmt in alt.body:
                        result += self._get_ast_structure(stmt, indent + 2)
            
            if hasattr(node, 'inevitably_body') and node.inevitably_body:
                result += f"{prefix}  Inevitably:\n"
                for stmt in node.inevitably_body:
                    result += self._get_ast_structure(stmt, indent + 2)
        
        elif isinstance(node, ForStatement):
            result += f"{prefix}ForStatement\n"
            if node.init:
                result += f"{prefix}  Init:\n"
                result += self._get_ast_structure(node.init, indent + 2)
            if node.condition:
                result += f"{prefix}  Condition:\n"
                result += self._get_ast_structure(node.condition, indent + 2)
            if node.update:
                result += f"{prefix}  Update:\n"
                result += self._get_ast_structure(node.update, indent + 2)
            result += f"{prefix}  Body:\n"
            for stmt in node.body:
                result += self._get_ast_structure(stmt, indent + 2)
        
        elif isinstance(node, WhileStatement):
            result += f"{prefix}WhileStatement\n"
            result += f"{prefix}  Condition:\n"
            result += self._get_ast_structure(node.condition, indent + 2)
            result += f"{prefix}  Body:\n"
            for stmt in node.body:
                result += self._get_ast_structure(stmt, indent + 2)
        
        elif isinstance(node, ReturnStatement):
            result += f"{prefix}ReturnStatement\n"
            if node.value:
                result += self._get_ast_structure(node.value, indent + 1)
        
        elif isinstance(node, ExpressionStatement):
            result += f"{prefix}ExpressionStatement\n"
            result += self._get_ast_structure(node.expression, indent + 1)
        
        elif isinstance(node, FunctionCall):
            result += f"{prefix}FunctionCall: {node.name}()\n"
            for arg in node.arguments:
                result += self._get_ast_structure(arg, indent + 1)
        
        elif isinstance(node, BinaryOperation):
            result += f"{prefix}BinaryOperation: {node.operator}\n"
            result += self._get_ast_structure(node.left, indent + 1)
            result += self._get_ast_structure(node.right, indent + 1)
        
        elif isinstance(node, UnaryOperation):
            result += f"{prefix}UnaryOperation: {node.operator}\n"
            result += self._get_ast_structure(node.operand, indent + 1)
        
        elif isinstance(node, Literal):
            result += f"{prefix}Literal: {node.value} ({node.type})\n"
        
        elif isinstance(node, Variable):
            result += f"{prefix}Variable: {node.name}\n"
        
        else:
            result += f"{prefix}{type(node).__name__}\n"
        
        return result

    def analyze_code(self):
        """Analisis completo: lexico + sintactico"""
        self.clear_outputs()
        code = self.code_editor.get('1.0', tk.END).strip()
        
        if not code:
            self.error_output.insert('1.0', "No hay codigo para analizar")
            return
        
        try:
            # Analisis lexico
            lexer = AlchemistLexer()
            tokens = lexer.tokenize(code)
            
            self.info_output.insert('1.0', "ANALISIS COMPLETO INICIADO\n")
            self.info_output.insert(tk.END, "="*50 + "\n")
            self.info_output.insert(tk.END, "FASE 1: ANALISIS LEXICO\n")
            self.info_output.insert(tk.END, f"Tokens generados: {len(tokens)}\n\n")
            
            # Analisis sintactico
            parser = AlchemistParser()
            ast = parser.parse(code)
            
            self.info_output.insert(tk.END, "FASE 2: ANALISIS SINTACTICO\n")
            self.info_output.insert(tk.END, f"Funciones encontradas: {len(ast.functions)}\n\n")
            
            # Detalles de funciones
            for func in ast.functions:
                params = ", ".join(f'{p.type} {p.name}' for p in func.parameters)
                self.info_output.insert(tk.END, f"  {func.name}({params}) -> {func.return_type}\n")
                self.info_output.insert(tk.END, f"  Statements: {len(func.body)}\n")
            
            self.info_output.insert(tk.END, "\n" + "="*50 + "\n")
            self.info_output.insert(tk.END, "ANALISIS COMPLETO EXITOSO")
            
        except Exception as e:
            self.error_output.insert('1.0', f"Error en analisis: {str(e)}")
        
    # ========================================
    # TEMA Y APARIENCIA
    # ========================================
    
    def toggle_theme(self, dark_mode):
        """Cambiar entre modo oscuro y claro"""
        self.dark_mode = dark_mode
        self.setup_styles()
        self.refresh_ui()
        
    def refresh_ui(self):
        """Refrescar la interfaz con nuevos colores"""
        # Actualizar root
        self.root.configure(bg=self.colors['bg_primary'])
        
        # Actualizar editor
        if hasattr(self, 'code_editor'):
            self.code_editor.configure(
                bg=self.colors['bg_primary'],
                fg=self.colors['fg_primary'],
                insertbackground=self.colors['fg_primary'],
                selectbackground=self.colors['select_bg'],
                selectforeground=self.colors['select_fg']
            )
        
        # Actualizar outputs
        outputs = [
            ('info_output', self.info_output),
            ('error_output', self.error_output), 
            ('program_output', self.program_output)
        ]
        
        for name, output in outputs:
            if hasattr(self, name):
                output.configure(
                    bg=self.colors['bg_primary'],
                    fg=self.colors['fg_primary']
                )
         
        self.setup_notebook_style()
    
    def show_welcome_info(self):
        """Mostrar informacion de bienvenida"""
        welcome = """ALCHEMIST IDE - CiRCULO DE TRANSMUTACION

Lenguaje Alchemist - Inspirado en Fullmetal Alchemist Brotherhood

Funcion Principal: GateOfTruth()
Tipos Alquimicos: Solid, Liquid, Inscription, Principle
Valores: Accepted (true), Rejected (false)
Transmutacion I/O: Transmute(), Absorb()
Observaciones(if-elseif-else): Observe, Alternatively, Inevitably
Ciclos: AlchemicCycle, TransmuteUntil

"Para obtener algo, algo de igual valor debe ser perdido"

 """

        self.info_output.delete('1.0', tk.END)
        self.info_output.insert('1.0', welcome)

    def show_reserved_words(self):
        """Mostrar palabras sagradas"""
        content = """PALABRAS SAGRADAS DE ALCHEMIST

Funcion Principal:
  GateOfTruth    // funcion principal

Tipos Alquimicos:
  Solid, Liquid, Inscription, Principle, void

Control:
  Observe, Alternatively, Inevitably
  AlchemicCycle, TransmuteUntil
  Transmutation

I/O:
  Transmute, Absorb

Valores:
  Accepted, Rejected

Operadores:
  and, or, not, EquivalentExchange, break, continue

Total: 20 palabras sagradas"""

        self.show_language_help("Palabras Sagradas", content)

    def show_control_syntax(self):
        """Mostrar sintaxis de control"""
        content = """SINTAXIS DE ALCHEMIST

Variables:
  Solid numero = 42
  Liquid decimal = 3.14
  Inscription texto = "hola"
  Principle verdadero = Accepted

Observaciones:
  Observe (condicion) {
      // codigo
  } Alternatively (otra) {
      // codigo
  } Inevitably {
      // codigo
  }

Ciclos:
  AlchemicCycle (Solid i = 0; i < 10; i = i + 1) {
      // codigo
  }

  TransmuteUntil (condicion) {
      // codigo
  }

Transmutaciones:
  Transmutation GateOfTruth() -> void {
      // funcion principal
  }

I/O:
  Transmute("mensaje")
  Inscription x = Absorb(":")"""

        self.show_language_help("Sintaxis", content)

    def load_example(self):
        """Cargar ejemplos"""
        examples = {
            "Variables Basicas": '''Transmutation GateOfTruth() -> void {
    Solid nivel = 50
    Inscription nombre = "Edward"
    Principle activo = Accepted

    Transmute("Nivel: " + nivel)
    Transmute("Nombre: " + nombre)
    Observe (activo == Accepted) {
        Transmute("Estado: ACTIVO")
    } Inevitably {
        Transmute("Estado: INACTIVO")
    }
}''',
            "Observaciones": '''Transmutation GateOfTruth() -> void {
    Solid edad = 16

    Observe (edad >= 18) {
        Transmute("Mayor de edad - Acceso completo")
    } Alternatively (edad >= 15) {
        Transmute("Acceso limitado - Supervision requerida")
    } Inevitably {
        Transmute("Menor de edad - Acceso denegado")
    }
}''',
            "Ciclo Alquimico": '''Transmutation GateOfTruth() -> void {
    Transmute("=== ACTIVANDO CiRCULOS ===")

    AlchemicCycle (Solid i = 1; i <= 5; i = i + 1) {
        Transmute("Circulo " + i + " ACTIVADO")
        Transmute("   Energia: " + (i * 20) + "%")
    }

    Transmute("Transmutacion completada")
}''',
            "Transmutaciones": '''Transmutation GateOfTruth() -> void {
    Solid poder = calcularPoder(16)
    Transmute("Poder alquimico: " + poder)
}

Transmutation calcularPoder(Solid edad) -> Solid {
    EquivalentExchange edad * 25 + 100
}''',
            "TransmuteUntil": '''Transmutation GateOfTruth() -> void {
    Solid energia = 100
    Solid ronda = 1

    Transmute("=== ENTRENAMIENTO INICIADO ===")

    TransmuteUntil (energia <= 20) {
        Transmute("Ronda " + ronda + " - Energia: " + energia + "%")
        energia = energia - 15
        ronda = ronda + 1
    }

    Transmute("Entrenamiento completado")
}''',
            "Absorcion de Datos": '''Transmutation GateOfTruth() -> void {
    Transmute("=== REGISTRO ALQUiMICO ===")

    Inscription nombre = Absorb("Tu nombre: ")

    Transmute("")
    Transmute("Perfil registrado:")
    Transmute("Nombre: " + nombre)

    Observe (nombre == "Edward") {
        Transmute("ALQUIMISTA SENIOR")
    } Inevitably {
        Transmute("APRENDIZ")
    }
}'''
        }

        self.show_example_window(examples)

    def show_example_window(self, examples):
        """Mostrar ventana de ejemplos con estilo minimalista"""
        window = tk.Toplevel(self.root)
        window.title("Grimorio de Ejemplos")
        window.geometry("700x600")
        window.configure(bg=self.colors['bg_primary'])
        window.grab_set()

        # Titulo
        title_label = tk.Label(
            window,
            text="GRIMORIO DE TRANSMUTACIONES",
            font=self.fonts['title'],
            bg=self.colors['bg_primary'],
            fg=self.colors['fg_primary'],
            pady=10
        )
        title_label.pack()

        # Lista
        list_frame = tk.Frame(window, bg=self.colors['bg_primary'])
        list_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)

        listbox = tk.Listbox(
            list_frame,
            font=self.fonts['main'],
            bg=self.colors['bg_primary'],
            fg=self.colors['fg_primary'],
            selectbackground=self.colors['select_bg'],
            selectforeground=self.colors['select_fg'],
            relief=tk.SOLID,
            bd=1
        )
        listbox.pack(fill=tk.BOTH, expand=True)

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
                    "Activar Transmutacion",
                    f"¿Activar circulo de transmutacion?\\n\\n{title}\\n\\nEsto reemplazara el codigo actual.",
                    parent=window
                ):
                    self.code_editor.delete('1.0', tk.END)
                    self.code_editor.insert('1.0', code)
                    self.clear_outputs()
                    window.destroy()

        tk.Button(
            button_frame,
            text="ACTIVAR",
            command=load_selected,
            font=self.fonts['button'],
            bg=self.colors['button_bg'],
            fg=self.colors['button_fg'],
            activebackground=self.colors['button_active'],
            activeforeground=self.colors['fg_primary'],
            relief=tk.SOLID,
            bd=1,
            padx=20,
            pady=5
        ).pack(side=tk.LEFT, padx=(0, 15))

        tk.Button(
            button_frame,
            text="CERRAR",
            command=window.destroy,
            font=self.fonts['button'],
            bg=self.colors['button_bg'],
            fg=self.colors['button_fg'],
            activebackground=self.colors['button_active'],
            activeforeground=self.colors['fg_primary'],
            relief=tk.SOLID,
            bd=1,
            padx=15,
            pady=5
        ).pack(side=tk.RIGHT)

    def show_language_help(self, title, content):
        """Mostrar ayuda con estilo minimalista"""
        window = tk.Toplevel(self.root)
        window.title(title)
        window.geometry("600x500")
        window.configure(bg=self.colors['bg_primary'])

        # Titulo
        title_label = tk.Label(
            window,
            text=title,
            font=self.fonts['title'],
            bg=self.colors['bg_primary'],
            fg=self.colors['fg_primary'],
            pady=10
        )
        title_label.pack()

        # Contenido
        text = scrolledtext.ScrolledText(
            window,
            bg=self.colors['bg_primary'],
            fg=self.colors['fg_primary'],
            font=self.fonts['main'],
            relief=tk.SOLID,
            bd=1
        )
        text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        text.insert('1.0', content)
        text.config(state=tk.DISABLED)

    def show_about(self):
        """Mostrar acerca de"""
        about = """ALCHEMIST IDE 
 """

        messagebox.showinfo("Acerca del Arte Sagrado", about)

    def clear_outputs(self):
        """Limpiar salidas"""
        self.info_output.delete('1.0', tk.END)
        self.error_output.delete('1.0', tk.END)
        self.program_output.delete('1.0', tk.END)

    def run(self):
        """Ejecutar IDE"""
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()

    def on_closing(self):
        """Manejar cierre"""
        if self.code_modified:
            if messagebox.askyesno("Archivo sin guardar", 
                                 "¿Guardar cambios antes de cerrar?"):
                self.save_file()
        
        if messagebox.askokcancel("Cerrar Portal", 
                                "¿Cerrar el Circulo de Transmutacion?"):
            self.root.destroy()

def main():
    """Funcion principal"""
    print("Iniciando Alchemist IDE Minimalista...")
    ide = AlchemistIDE()
    ide.run()

if __name__ == "__main__":
    main()
