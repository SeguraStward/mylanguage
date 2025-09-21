#!/usr/bin/env python3
"""
Alchemist IDE - Círculo de Transmutación Supremo
IDE épico inspirado en Fullmetal Alchemist Brotherhood
Con estilo alquímico transparente y imagen de fondo automática
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog, Menu
import os
from PIL import Image, ImageTk
from .lexer import AlchemistLexer
from .parser import AlchemistParser

class AlchemistIDE:
    """IDE épico para el lenguaje Alchemist con estilo alquímico transparente"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Alchemist")
        self.root.geometry("1400x900")
        
        # Variables para el estado del IDE
        self.current_file = None
        self.code_modified = False
        self.dark_mode = True  # Modo por defecto
        self.bg_image = None
        self.bg_photo = None
        self.canvas_photo = None  # Para imagen redimensionada del canvas
        self.editor_bg_photo = None  # Para imagen compuesta del editor
        self.main_bg_label = None
        self.editor_bg_label = None  # Para imagen del editor
        self.canvas_bg_image = None  # Para imagen en canvas
        
        # Configurar estilos
        self.setup_styles()
        
        # Inicializar componentes
        self.setup_menu()
        self.setup_ui()
        self.setup_bindings()
        
        # Cargar imagen de fondo después de crear la UI
        self.load_theme_background()
        
    def setup_styles(self):
        """Configura los estilos según el modo con transparencias"""
        if self.dark_mode:
            self.colors = {
                'bg_primary': '#000000',        # Negro para modo oscuro
                'bg_transparent': '#000000',    # Fondo transparente
                'fg_primary': '#ffffff',        # Texto blanco
                'fg_secondary': '#cccccc',      # Gris claro
                'border_subtle': '#333333',     # Bordes apenas visibles
                'button_bg': '#1a1a1a',        # Botones visibles
                'button_fg': '#ffffff',
                'button_active': '#2a2a2a',
                'select_bg': '#333333',
                'select_fg': '#ffffff'
            }
        else:
            self.colors = {
                'bg_primary': '#ffffff',        # Blanco para modo claro
                'bg_transparent': '#ffffff',    # Fondo transparente
                'fg_primary': '#000000',        # Texto negro
                'fg_secondary': '#333333',      # Gris oscuro
                'border_subtle': '#cccccc',     # Bordes apenas visibles
                'button_bg': '#e0e0e0',        # Botones visibles
                'button_fg': '#000000',
                'button_active': '#d0d0d0',
                'select_bg': '#cccccc',
                'select_fg': '#000000'
            }
        
        self.root.configure(bg=self.colors['bg_primary'])
        
    def load_theme_background(self):
        """Cargar imagen de fondo según el tema actual"""
        try:
            # Nombre de archivo según el modo (exactamente como los tienes)
            filename = 'BLACK.jpeg' if self.dark_mode else 'WHITE.jpeg'
            
            # Obtener directorio actual (src/)
            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(current_dir)  # Subir un nivel desde src/
            
            # Posibles ubicaciones de la imagen (buscar primero en src/)
            possible_paths = [
                # En el directorio src/ (donde están realmente)
                os.path.join(current_dir, filename),
                # En la raíz del proyecto
                os.path.join(project_root, filename),
                # En el directorio actual de trabajo
                os.path.join(os.getcwd(), filename),
                # También buscar versiones en minúsculas
                os.path.join(current_dir, filename.lower()),
                os.path.join(project_root, filename.lower())
            ]
            
            image_path = None
            for path in possible_paths:
                print(f"🔍 Buscando: {path}")
                if os.path.exists(path):
                    image_path = path
                    print(f"✅ IMAGEN ENCONTRADA: {path}")
                    break
            
            if image_path:
                # Cargar y redimensionar imagen
                image = Image.open(image_path)
                # Redimensionar para que cubra la ventana pero mantenga proporción
                image = image.resize((700, 500), Image.Resampling.LANCZOS)
                self.bg_photo = ImageTk.PhotoImage(image)
                
                # Aplicar imagen de fondo principal
                self.apply_main_background()
                # Aplicar imagen específicamente al editor si ya existe
                if hasattr(self, 'editor_container'):
                    self.apply_editor_background()
                print(f"🎉 Imagen aplicada correctamente: {filename}")
            else:
                print(f"❌ NO SE ENCONTRÓ: {filename}")
                print("Ubicaciones buscadas:")
                for path in possible_paths:
                    print(f"  - {path}")
                
        except Exception as e:
            print(f"❌ Error cargando imagen de fondo: {e}")
    
    def apply_main_background(self):
        """Aplicar imagen de fondo principal centrada"""
        if self.bg_photo:
            # Eliminar imagen anterior si existe
            if self.main_bg_label:
                self.main_bg_label.destroy()
            
            # Crear label de fondo principal
            self.main_bg_label = tk.Label(
                self.root,
                image=self.bg_photo,
                bg=self.colors['bg_primary']
            )
            # Centrar la imagen en toda la ventana
            self.main_bg_label.place(relx=0.5, rely=0.5, anchor='center')
            # Enviar al fondo
            self.main_bg_label.lower()
            
    def setup_menu(self):
        """Configura el menú principal transparente"""
        menubar = Menu(
            self.root, 
            bg=self.colors['bg_transparent'], 
            fg=self.colors['fg_primary'],
            activebackground=self.colors['button_active'],
            relief=tk.FLAT,
            bd=0
        )
        self.root.config(menu=menubar)
        
        # Menú Archivo
        file_menu = Menu(
            menubar, 
            tearoff=0, 
            bg=self.colors['bg_transparent'], 
            fg=self.colors['fg_primary'],
            relief=tk.FLAT
        )
        menubar.add_cascade(label="Archivo", menu=file_menu)
        file_menu.add_command(label="Nuevo", command=self.new_file, accelerator="Ctrl+N")
        file_menu.add_command(label="Abrir", command=self.open_file, accelerator="Ctrl+O")
        file_menu.add_command(label="Guardar", command=self.save_file, accelerator="Ctrl+S")
        file_menu.add_separator()
        file_menu.add_command(label="Salir", command=self.root.quit)
        
        # Menú Herramientas
        tools_menu = Menu(
            menubar, 
            tearoff=0, 
            bg=self.colors['bg_transparent'], 
            fg=self.colors['fg_primary'],
            relief=tk.FLAT
        )
        menubar.add_cascade(label="Herramientas", menu=tools_menu)
        tools_menu.add_command(label="Analizar Elementos", command=self.test_lexer)
        tools_menu.add_command(label="Verificar Estructura", command=self.test_parser)
        
        # Menú Apariencia
        view_menu = Menu(
            menubar, 
            tearoff=0, 
            bg=self.colors['bg_transparent'], 
            fg=self.colors['fg_primary'],
            relief=tk.FLAT
        )
        menubar.add_cascade(label="Apariencia", menu=view_menu)
        view_menu.add_command(label="Modo Oscuro", command=lambda: self.toggle_theme(True))
        view_menu.add_command(label="Modo Claro", command=lambda: self.toggle_theme(False))
        
        # Ayuda
        menubar.add_command(label="Acerca de", command=self.show_about)
        
    def setup_ui(self):
        """Configura la interfaz principal transparente"""
        # Frame principal transparente
        main_frame = tk.Frame(
            self.root, 
            bg=self.colors['bg_transparent'],
            relief=tk.FLAT,
            bd=0
        )
        main_frame.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)
        
        # Título del IDE - semi-transparente
        title_frame = tk.Frame(
            main_frame, 
            bg=self.colors['bg_transparent'], 
            relief=tk.FLAT,
            bd=1,
            highlightbackground=self.colors['border_subtle'],
            highlightthickness=1
        )
        title_frame.pack(fill=tk.X, pady=(0, 8))
        
        title_label = tk.Label(
            title_frame,
            text="ALCHEMIST IDE",
            font=('Arial', 16, 'bold'),
            bg=self.colors['bg_transparent'],
            fg=self.colors['fg_primary'],
            pady=8
        )
        title_label.pack()
        
        subtitle_label = tk.Label(
            title_frame,
            text="Para obtener algo, algo de igual valor debe ser perdido",
            font=('Arial', 10, 'italic'),
            bg=self.colors['bg_transparent'],
            fg=self.colors['fg_secondary']
        )
        subtitle_label.pack()
        
        # Panel de botones (visible)
        self.setup_button_panel(main_frame)
        
        # Panel principal dividido - transparente
        main_paned = tk.PanedWindow(
            main_frame, 
            orient=tk.HORIZONTAL, 
            bg=self.colors['bg_transparent'],
            sashwidth=3,
            sashrelief=tk.FLAT,
            relief=tk.FLAT,
            bd=0
        )
        main_paned.pack(fill=tk.BOTH, expand=True)
        
        # Frame izquierdo transparente
        left_frame = tk.Frame(main_paned, bg=self.colors['bg_transparent'])
        main_paned.add(left_frame, width=800)
        
        # Frame derecho transparente
        right_frame = tk.Frame(main_paned, bg=self.colors['bg_transparent'])
        main_paned.add(right_frame, width=600)
        
        self.setup_code_editor(left_frame)
        self.setup_output_panel(right_frame)
        
    def setup_button_panel(self, parent):
        """Configura el panel de botones (visibles pero compactos)"""
        button_frame = tk.Frame(
            parent, 
            bg=self.colors['button_bg'], 
            relief=tk.RIDGE, 
            bd=2
        )
        button_frame.pack(fill=tk.X, pady=(0, 8))
        
        # Botones principales - compactos pero visibles
        tk.Button(
            button_frame,
            text="Analizar",
            command=self.test_lexer,
            font=('Arial', 9, 'bold'),
            bg=self.colors['button_bg'],
            fg=self.colors['button_fg'],
            activebackground=self.colors['button_active'],
            activeforeground=self.colors['fg_primary'],
            relief=tk.RAISED,
            bd=2,
            padx=10,
            pady=2
        ).pack(side=tk.LEFT, padx=3, pady=3)
        
        tk.Button(
            button_frame,
            text="Verificar",
            command=self.test_parser,
            font=('Arial', 9, 'bold'),
            bg=self.colors['button_bg'],
            fg=self.colors['button_fg'],
            activebackground=self.colors['button_active'],
            activeforeground=self.colors['fg_primary'],
            relief=tk.RAISED,
            bd=2,
            padx=10,
            pady=2
        ).pack(side=tk.LEFT, padx=3, pady=3)
        
        # Separador sutil
        separator = tk.Frame(button_frame, width=2, bg=self.colors['border_subtle'])
        separator.pack(side=tk.LEFT, fill=tk.Y, padx=6, pady=3)
        
        # Botones de ayuda
        tk.Button(
            button_frame,
            text="Palabras",
            command=self.show_reserved_words,
            font=('Arial', 9, 'bold'),
            bg=self.colors['button_bg'],
            fg=self.colors['button_fg'],
            activebackground=self.colors['button_active'],
            activeforeground=self.colors['fg_primary'],
            relief=tk.RAISED,
            bd=2,
            padx=10,
            pady=2
        ).pack(side=tk.LEFT, padx=3, pady=3)
        
        tk.Button(
            button_frame,
            text="Sintaxis",
            command=self.show_control_syntax,
            font=('Arial', 9, 'bold'),
            bg=self.colors['button_bg'],
            fg=self.colors['button_fg'],
            activebackground=self.colors['button_active'],
            activeforeground=self.colors['fg_primary'],
            relief=tk.RAISED,
            bd=2,
            padx=10,
            pady=2
        ).pack(side=tk.LEFT, padx=3, pady=3)
        
        tk.Button(
            button_frame,
            text="Ejemplos",
            command=self.load_example,
            font=('Arial', 9, 'bold'),
            bg=self.colors['button_bg'],
            fg=self.colors['button_fg'],
            activebackground=self.colors['button_active'],
            activeforeground=self.colors['fg_primary'],
            relief=tk.RAISED,
            bd=2,
            padx=10,
            pady=2
        ).pack(side=tk.LEFT, padx=3, pady=3)
        
    def setup_code_editor(self, parent):
        """Configura el editor de código con imagen de fondo visible - NUEVA ESTRATEGIA"""
        # Marco del editor - completamente transparente
        editor_frame = tk.LabelFrame(
            parent,
            text="Editor de Código",
            font=('Arial', 10, 'bold'),
            bg=self.colors['bg_primary'],
            fg=self.colors['fg_primary'],
            relief=tk.FLAT,
            bd=1
        )
        editor_frame.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)
        
        # NUEVA ESTRATEGIA: Canvas con imagen de fondo y text widget encima
        self.editor_canvas = tk.Canvas(
            editor_frame,
            bg=self.colors['bg_primary'],
            highlightthickness=0,
            relief=tk.FLAT,
            bd=0
        )
        self.editor_canvas.pack(fill=tk.BOTH, expand=True, padx=6, pady=6)
        
        # Frame para el texto que va encima del canvas
        self.editor_container = tk.Frame(self.editor_canvas, bg=self.colors['bg_primary'])
        
        # Crear window en canvas para el frame
        self.canvas_window = self.editor_canvas.create_window(
            0, 0, anchor="nw", window=self.editor_container
        )
        
        # Editor de texto con fondo que permite ver a través
        self.code_editor = scrolledtext.ScrolledText(
            self.editor_container,
            wrap=tk.NONE,
            font=('Consolas', 10),
            bg=self.colors['bg_primary'],  # Mismo color que el canvas
            fg=self.colors['fg_primary'],
            insertbackground=self.colors['fg_primary'],
            selectbackground=self.colors['select_bg'],
            selectforeground=self.colors['select_fg'],
            relief=tk.FLAT,
            bd=0,
            highlightthickness=0
        )
        self.code_editor.pack(fill=tk.BOTH, expand=True)
        
        # Configurar el canvas para que se redimensione con el contenido
        def configure_canvas(event=None):
            # Actualizar el tamaño del frame en el canvas
            self.editor_canvas.configure(scrollregion=self.editor_canvas.bbox("all"))
            # Hacer que el frame del editor ocupe todo el canvas
            canvas_width = self.editor_canvas.winfo_width()
            canvas_height = self.editor_canvas.winfo_height()
            self.editor_canvas.itemconfig(self.canvas_window, width=canvas_width, height=canvas_height)
        
        self.editor_canvas.bind('<Configure>', configure_canvas)
        self.editor_container.bind('<Configure>', configure_canvas)
        
        # Aplicar imagen de fondo al canvas después de que se configure
        self.root.after(100, self.apply_canvas_background)
        
        # Código inicial
        initial_code = """// CÍRCULO DE TRANSMUTACIÓN SUPREMO
// Fullmetal Alchemist Brotherhood

Transmutation GateOfTruth() -> void {
    Transmute("ACTIVANDO CÍRCULO ALQUÍMICO")
    
    Inscription alquimista = "Edward Elric"
    Solid edad = 16
    Principle esAlquimista = Accepted
    
    Transmute("Alquimista: " + alquimista)
    Transmute("Edad: " + edad + " años")
    
    Observe (edad >= 15 and esAlquimista == Accepted) {
        Transmute("ACCESO CONCEDIDO")
        
        AlchemicCycle (Solid i = 1; i <= 3; i = i + 1) {
            Transmute("Círculo " + i + " ACTIVADO")
        }
    } Inevitably {
        Transmute("ACCESO DENEGADO")
    }
    
    Transmute("INTERCAMBIO EQUIVALENTE COMPLETADO")
}"""
        
        self.code_editor.insert('1.0', initial_code)
        
    def apply_canvas_background(self):
        """Aplicar imagen de fondo al canvas del editor"""
        if hasattr(self, 'bg_photo') and self.bg_photo and hasattr(self, 'editor_canvas'):
            try:
                # Eliminar imagen anterior si existe
                if hasattr(self, 'canvas_bg_image'):
                    self.editor_canvas.delete(self.canvas_bg_image)
                
                # Obtener dimensiones del canvas
                self.editor_canvas.update_idletasks()
                canvas_width = self.editor_canvas.winfo_width()
                canvas_height = self.editor_canvas.winfo_height()
                
                if canvas_width > 1 and canvas_height > 1:  # Asegurar que el canvas tiene dimensiones válidas
                    # Redimensionar imagen para ajustarse al canvas
                    filename = 'BLACK.jpeg' if self.dark_mode else 'WHITE.jpeg'
                    image_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)
                    
                    # Cargar y redimensionar imagen
                    pil_image = Image.open(image_path)
                    resized_image = pil_image.resize((canvas_width, canvas_height), Image.Resampling.LANCZOS)
                    self.canvas_photo = ImageTk.PhotoImage(resized_image)
                    
                    # Crear imagen de fondo en el canvas centrada
                    self.canvas_bg_image = self.editor_canvas.create_image(
                        canvas_width // 2, canvas_height // 2, 
                        image=self.canvas_photo
                    )
                    
                    # Asegurar que la imagen esté en el fondo
                    self.editor_canvas.tag_lower(self.canvas_bg_image)
                    
                    print(f"🎨 Imagen {filename} aplicada al canvas ({canvas_width}x{canvas_height})")
                    
                    # Hacer el frame del editor transparente
                    if hasattr(self, 'editor_container'):
                        self.editor_container.configure(bg='')  # Transparente
                    
                    # Configurar el text widget para máxima transparencia
                    if hasattr(self, 'code_editor'):
                        # Usar colores que contrasten bien con la imagen de fondo
                        if self.dark_mode:
                            text_bg = '#2a2a2a'  # Gris muy oscuro, semi-transparente
                            text_fg = '#ffffff'
                        else:
                            text_bg = '#e8e8e8'  # Gris muy claro, semi-transparente
                            text_fg = '#000000'
                        
                        self.code_editor.configure(
                            bg=text_bg,
                            fg=text_fg,
                            insertbackground=text_fg,
                            selectbackground='#4a4a4a' if self.dark_mode else '#cccccc',
                            selectforeground=text_fg
                        )
                        
                        print(f"🖌️ Editor configurado con fondo {text_bg}")
                
            except Exception as e:
                print(f"❌ Error aplicando imagen al canvas: {e}")
                import traceback
                traceback.print_exc()

    def apply_editor_background(self):
        """Aplicar imagen de fondo específicamente al editor de código - NUEVA VERSIÓN"""
        # Esta función ahora llama a apply_canvas_background
        if hasattr(self, 'editor_canvas'):
            self.apply_canvas_background()
        else:
            print("⚠️ Canvas del editor no está listo aún")
            if self.dark_mode:
                # En modo oscuro, usar gris muy oscuro semi-transparente
                editor_bg = '#1a1a1a'  # Gris muy oscuro en lugar de negro
            else:
                # En modo claro, usar gris muy claro semi-transparente  
                editor_bg = '#f8f8f8'  # Gris muy claro en lugar de blanco puro
                
            self.code_editor.configure(bg=editor_bg)
        
    def setup_output_panel(self, parent):
        """Configura el panel de salida transparente"""
        # Notebook transparente
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('Transparent.TNotebook', 
                       background=self.colors['bg_transparent'],
                       borderwidth=0)
        style.configure('Transparent.TNotebook.Tab', 
                       background=self.colors['bg_transparent'],
                       foreground=self.colors['fg_primary'],
                       padding=[12, 8])
        
        self.notebook = ttk.Notebook(parent, style='Transparent.TNotebook')
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)
        
        # Tab de errores - transparente
        error_frame = tk.Frame(
            self.notebook, 
            bg=self.colors['bg_transparent'],
            relief=tk.FLAT,
            bd=1,
            highlightbackground=self.colors['border_subtle'],
            highlightthickness=1
        )
        self.notebook.add(error_frame, text="Errores")
        
        self.error_output = scrolledtext.ScrolledText(
            error_frame,
            font=('Consolas', 9),
            bg=self.colors['bg_transparent'],
            fg=self.colors['fg_secondary'],
            relief=tk.FLAT,
            bd=0,
            highlightthickness=1,
            highlightcolor=self.colors['border_subtle'],
            highlightbackground=self.colors['border_subtle']
        )
        self.error_output.pack(fill=tk.BOTH, expand=True, padx=6, pady=6)
        
        # Tab de salida - transparente
        output_frame = tk.Frame(
            self.notebook, 
            bg=self.colors['bg_transparent'],
            relief=tk.FLAT,
            bd=1,
            highlightbackground=self.colors['border_subtle'],
            highlightthickness=1
        )
        self.notebook.add(output_frame, text="Salida")
        
        self.program_output = scrolledtext.ScrolledText(
            output_frame,
            font=('Consolas', 9),
            bg=self.colors['bg_transparent'],
            fg=self.colors['fg_primary'],
            relief=tk.FLAT,
            bd=0,
            highlightthickness=1,
            highlightcolor=self.colors['border_subtle'],
            highlightbackground=self.colors['border_subtle']
        )
        self.program_output.pack(fill=tk.BOTH, expand=True, padx=6, pady=6)
        
        # Tab de información - transparente
        info_frame = tk.Frame(
            self.notebook, 
            bg=self.colors['bg_transparent'],
            relief=tk.FLAT,
            bd=1,
            highlightbackground=self.colors['border_subtle'],
            highlightthickness=1
        )
        self.notebook.add(info_frame, text="Información")
        
        self.info_output = scrolledtext.ScrolledText(
            info_frame,
            font=('Consolas', 9),
            bg=self.colors['bg_transparent'],
            fg=self.colors['fg_secondary'],
            relief=tk.FLAT,
            bd=0,
            highlightthickness=1,
            highlightcolor=self.colors['border_subtle'],
            highlightbackground=self.colors['border_subtle']
        )
        self.info_output.pack(fill=tk.BOTH, expand=True, padx=6, pady=6)
        
        # Mostrar información de bienvenida
        self.show_welcome_info()
        
    def toggle_theme(self, dark_mode):
        """Cambiar entre modo oscuro y claro"""
        self.dark_mode = dark_mode
        self.setup_styles()
        self.load_theme_background()  # Cargar nueva imagen
        self.refresh_ui()
        
    def refresh_ui(self):
        """Refrescar la interfaz con nuevos colores"""
        # Actualizar todos los widgets principales
        self.root.configure(bg=self.colors['bg_primary'])
        
        # Actualizar canvas del editor si existe
        if hasattr(self, 'editor_canvas') and self.editor_canvas:
            self.editor_canvas.configure(bg=self.colors['bg_primary'])
            self.apply_canvas_background()  # Reaplicar imagen de fondo
        
        # Actualizar editor solo si ya existe
        if hasattr(self, 'code_editor') and self.code_editor:
            try:
                self.code_editor.configure(
                    bg=self.colors['bg_primary'],  # Mismo color que el canvas
                    fg=self.colors['fg_primary'],
                    insertbackground=self.colors['fg_primary'],
                    selectbackground=self.colors['select_bg'],
                    selectforeground=self.colors['select_fg']
                )
            except:
                # Fallback
                self.code_editor.configure(
                    bg=self.colors['bg_transparent'],
                    fg=self.colors['fg_primary'],
                    insertbackground=self.colors['fg_primary'],
                    selectbackground=self.colors['select_bg'],
                    selectforeground=self.colors['select_fg']
                )
        
        # Actualizar paneles de salida solo si existen
        if hasattr(self, 'error_output') and self.error_output:
            self.error_output.configure(
                bg=self.colors['bg_transparent'],
                fg=self.colors['fg_secondary']
            )
        
        if hasattr(self, 'program_output') and self.program_output:
            self.program_output.configure(
                bg=self.colors['bg_transparent'],
                fg=self.colors['fg_primary']
            )
        
        if hasattr(self, 'info_output') and self.info_output:
            self.info_output.configure(
                bg=self.colors['bg_transparent'],
                fg=self.colors['fg_secondary']
            )
        
        # Reaplicar imagen de fondo al editor solo si existe
        if hasattr(self, 'editor_container') and hasattr(self, 'bg_photo') and self.bg_photo:
            self.apply_editor_background()
    
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
            
            output += "\nSecuencia de tokens (primeros 25):\n"
            count = 0
            for token in tokens:
                if token.type.name not in ['WHITESPACE', 'NEWLINE'] and count < 25:
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
• Interfaz transparente con imagen de fondo automática
• Modo oscuro/claro con imágenes temáticas
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
        title_frame = tk.Frame(
            window, 
            bg=self.colors['button_bg'], 
            relief=tk.RAISED, 
            bd=3
        )
        title_frame.pack(fill=tk.X, padx=10, pady=10)
        
        title_label = tk.Label(
            title_frame,
            text="EJEMPLOS DE CÓDIGO ALCHEMIST",
            font=('Arial', 14, 'bold'),
            bg=self.colors['button_bg'],
            fg=self.colors['button_fg'],
            pady=8
        )
        title_label.pack()
        
        # Lista
        list_frame = tk.Frame(
            window, 
            bg=self.colors['bg_transparent'], 
            relief=tk.RIDGE, 
            bd=2
        )
        list_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)
        
        listbox = tk.Listbox(
            list_frame,
            font=('Consolas', 10, 'bold'),
            bg=self.colors['bg_transparent'],
            fg=self.colors['fg_primary'],
            selectbackground=self.colors['select_bg'],
            selectforeground=self.colors['select_fg'],
            relief=tk.FLAT,
            bd=0
        )
        listbox.pack(fill=tk.BOTH, expand=True, padx=6, pady=6)
        
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
            font=('Arial', 11, 'bold'),
            bg=self.colors['button_bg'],
            fg=self.colors['button_fg'],
            activebackground=self.colors['button_active'],
            activeforeground=self.colors['fg_primary'],
            relief=tk.RAISED,
            bd=3,
            padx=20,
            pady=6
        ).pack(side=tk.LEFT, padx=(0, 15))
        
        tk.Button(
            button_frame,
            text="CERRAR",
            command=window.destroy,
            font=('Arial', 10),
            bg=self.colors['button_bg'],
            fg=self.colors['button_fg'],
            activebackground=self.colors['button_active'],
            activeforeground=self.colors['fg_primary'],
            relief=tk.RAISED,
            bd=3,
            padx=15,
            pady=6
        ).pack(side=tk.RIGHT)
        
    def show_language_help(self, title, content):
        """Mostrar ayuda"""
        window = tk.Toplevel(self.root)
        window.title(title)
        window.geometry("600x500")
        window.configure(bg=self.colors['bg_primary'])
        
        # Título
        title_frame = tk.Frame(
            window, 
            bg=self.colors['button_bg'], 
            relief=tk.RAISED, 
            bd=3
        )
        title_frame.pack(fill=tk.X, padx=8, pady=8)
        
        title_label = tk.Label(
            title_frame,
            text=title,
            font=('Arial', 12, 'bold'),
            bg=self.colors['button_bg'],
            fg=self.colors['button_fg'],
            pady=6
        )
        title_label.pack()
        
        # Contenido
        text = scrolledtext.ScrolledText(
            window, 
            bg=self.colors['bg_transparent'], 
            fg=self.colors['fg_primary'],
            font=('Consolas', 10),
            relief=tk.FLAT,
            bd=0
        )
        text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        text.insert('1.0', content)
        text.config(state=tk.DISABLED)
        
    def show_about(self):
        """Mostrar acerca de"""
        about = """ALCHEMIST IDE

Versión: 4.0 Transparent Edition
Estilo: Transparente con imagen de fondo automática
Inspirado en: Fullmetal Alchemist Brotherhood
Tema: Intercambio Equivalente

Características:
• Sintaxis épica inspirada en FMA
• Interfaz transparente
• Imagen de fondo automática según tema
• Modos oscuro/claro con imágenes específicas
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
