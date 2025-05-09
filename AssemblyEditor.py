import tkinter as tk
from tkinter import filedialog, Menu, messagebox
import tkinter.font as tkfont 
from PIL import Image, ImageTk
import ctypes
import json
import re
from Assembler import Assembler

class AssemblyEditor:

    def __init__(self, root):

        self.root = root
        self.configure_root()
        self.setup_icon()
        self.setup_default_configs()
        self.create_menu()
        self.load_configuration_files()
        self.setup_main_frame()
        self.bind_events()

    def configure_root(self):
        """Configure the root window."""

        self.root.title("Assembly Editor")
        self.root.geometry("1600x1000")
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
        self.root.option_add("*Font", "Arial 14")
        self.root.bind("<Configure>", self.handle_resize)

    def setup_icon(self):
        """Set the window icon."""

        path = "assets/edit.png"
        load = Image.open(path)
        render = ImageTk.PhotoImage(load)
        self.root.iconphoto(False, render)

    def setup_default_configs(self):
        """Setup default configurations."""

        self.font_size = 12  # Default font size
        self.dark_mode = True  # Default theme

    def setup_main_frame(self):
        """Setup the main frame."""

        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Theme selection
        THEME = self.dark_theme if self.dark_mode else self.light_theme

        # Line Numbers
        self.line_numbers = tk.Text(self.main_frame, width=4, padx=15, takefocus=0, border=0, pady=15,
                                    background=THEME.get('line_number_bg'), foreground=THEME.get('line_number_fg'), state=tk.DISABLED)
        self.line_numbers.pack(side=tk.LEFT, fill=tk.Y)

        # Separator (a linha vertical)
        self.separator = tk.Frame(self.main_frame, width=1, bg=THEME.get('line_separator'))
        self.separator.pack(side=tk.LEFT, fill=tk.Y)

        # Text Area
        self.text_area_frame = tk.Frame(self.main_frame)  # Create a frame for the text area and scrollbar
        self.text_area_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.text_area = tk.Text(self.text_area_frame, wrap="word", undo=True, font=("Courier New", 12), padx=15, pady=15, border=0,
                                background=THEME.get('background'), foreground=THEME.get('foreground'), insertbackground=THEME.get('foreground'))
        self.text_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Scrollbar
        self.scrollbar = tk.Scrollbar(self.text_area_frame, command=self.text_area.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.text_area.config(yscrollcommand=self.scrollbar.set)

        # Sync the line numbers with the text area scroll
        self.text_area.config(yscrollcommand=lambda *args: self.sync_scroll(*args))
        self.line_numbers.config(yscrollcommand=lambda *args: self.sync_scroll(*args))

        # Set Font 
        font = tkfont.Font(font=self.text_area['font']) 
        self.change_font_size(7)
        
        # Set Tab size 
        tab_size = font.measure('   ') 
        self.text_area.config(tabs=tab_size)

        # Add Syntax Highlighting Tags
        self.syntax_highlight_theme()
        self.highlight_syntax()           # Apply syntax highlighting

    def sync_scroll(self, *args):
        """Sync scrolling between text area and line numbers."""
        # Movimenta ambos os widgets juntos usando o mesmo parâmetro de scroll
        self.line_numbers.yview_moveto(args[0])
        self.text_area.yview_moveto(args[0])
        self.scrollbar.set(*args)

    def handle_resize(self, event=None):
        """Force scroll position maintenance on resize"""
        self.update_line_numbers()
        self.highlight_syntax()

    def load_configuration_files(self):
        """Load configuration files: color schemes and ISA."""

        self.dark_theme = self.load_json_file("./configs/dark_theme.json")
        self.light_theme = self.load_json_file("./configs/light_theme.json")
        self.isa_config = self.load_json_file("./configs/default_isa.json")

        self.load_isa()             # Load ISA instructions and registers

    def load_json_file(self, file_path):
        """Load a JSON file (configs)."""

        try:
            with open(file_path, 'r') as file:
                return json.load(file)
        except Exception as e:
            print(f"Failed to load {file_path}: {e}")
            return {}

    def syntax_highlight_theme(self):
        """"Apply syntax highlighting tags."""

        THEME = self.dark_theme if self.dark_mode else self.light_theme

        self.text_area.tag_configure("instruction", foreground=THEME.get('instruction'))
        self.text_area.tag_configure("register", foreground=THEME.get('register'))
        self.text_area.tag_configure("label", foreground=THEME.get('label'))
        self.text_area.tag_configure("comment", foreground=THEME.get('comment'))
        self.text_area.tag_configure("number", foreground=THEME.get('number'))

    def load_isa_config(self):
        file_path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json"), ("All files", "*.*")])
        if file_path:
            try:
                with open(file_path, 'r') as file:
                    self.isa_config = json.load(file)
                    self.load_isa()
                    self.highlight_syntax()
            except Exception as e:
                print(f"Failed to load ISA config: {e}")

    def load_isa(self):
        """Load ISA instructions and registers."""
        self.instructions = self.isa_config.get("instructions", {}).keys()
        self.registers = self.isa_config.get("registers", {}).keys()

    def highlight_syntax(self):
        """Apply syntax highlighting."""
        self.text_area.tag_remove("instruction", "1.0", tk.END)
        self.text_area.tag_remove("register", "1.0", tk.END)
        self.text_area.tag_remove("label", "1.0", tk.END)
        self.text_area.tag_remove("comment", "1.0", tk.END)
        self.text_area.tag_remove("number", "1.0", tk.END)

        text = self.text_area.get("1.0", tk.END)

        for instr in self.instructions:
            for match in re.finditer(rf'\b{instr}\b', text):
                self.text_area.tag_add("instruction", f"1.0+{match.start()}c", f"1.0+{match.end()}c")

        for reg in self.registers:
            for match in re.finditer(rf'\b{reg}\b', text):
                self.text_area.tag_add("register", f"1.0+{match.start()}c", f"1.0+{match.end()}c")

        for match in re.finditer(r'\b\d+\b', text):
            self.text_area.tag_add("number", f"1.0+{match.start()}c", f"1.0+{match.end()}c")

        for match in re.finditer(r'^\s*[A-Za-z_][A-Za-z0-9_]*:', text, re.MULTILINE):
            self.text_area.tag_add("label", f"1.0+{match.start()}c", f"1.0+{match.end()}c")

        for match in re.finditer(r';.*', text):
            self.text_area.tag_add("comment", f"1.0+{match.start()}c", f"1.0+{match.end()}c")

    def bind_events(self):
        """Bind events to the text area"""

        self.text_area.bind("<KeyRelease>", self.on_key_release)
        self.text_area.bind("<MouseWheel>", self.on_scroll)
        self.text_area.bind("<Control-MouseWheel>", self.zoom_text)
        self.text_area.bind("<Control-plus>", lambda e: self.change_font_size(1))
        self.text_area.bind("<Control-equal>", lambda e: self.change_font_size(1))  # For some keyboards
        self.text_area.bind("<Control-minus>", lambda e: self.change_font_size(-1))
        self.text_area.bind("<Control-s>", lambda e: self.save_file())
        self.text_area.bind("<Control-o>", lambda e: self.open_file())
        self.text_area.bind("<Control-r>", lambda e: self.assemble_code())
        self.text_area.bind("<FocusIn>", self.update_line_numbers)  
        self.text_area.bind("<FocusOut>", self.update_line_numbers)  
        self.text_area.bind("<Configure>", self.update_line_numbers)
        self.text_area.bind("<Control-v>", self.update_line_numbers)
        self.text_area.bind("<<Modified>>", self.on_text_modified)

    def on_text_modified(self, event):
        """Handle text modification events."""
        if self.text_area.edit_modified():
            self.update_line_numbers()
            self.highlight_syntax()
            self.text_area.edit_modified(False)  # Reseta o flag

    def on_key_release(self, event):
        """Update syntax highlighting and line numbers."""
        self.highlight_syntax()

    def update_line_numbers(self, event=None):
        """Update the line numbers panel."""
        # Salva a posição atual do scroll
        current_scroll = self.text_area.yview()[0]

        # Atualiza os números das linhas
        self.line_numbers.config(state=tk.NORMAL)
        self.line_numbers.delete("1.0", tk.END)

        # Obtém o número correto de linhas usando o índice do text_area
        last_line_index = self.text_area.index("end-1c")
        total_lines = int(last_line_index.split(".")[0])
        
        line_numbers_str = "\n".join(str(i) for i in range(1, total_lines + 1))
        self.line_numbers.insert("1.0", line_numbers_str)
        self.line_numbers.config(state=tk.DISABLED)

        # Restaura a posição do scroll sincronizando ambos os widgets
        self.text_area.yview_moveto(current_scroll)
        self.line_numbers.yview_moveto(current_scroll)

    def on_scroll(self, event):
        """Synchronize line numbers with text scrolling."""
        self.line_numbers.yview_moveto(self.text_area.yview()[0])

    def zoom_text(self, event):
        """ Zooms in and out using Ctrl + Mouse Scroll """
        if event.delta > 0:
            self.change_font_size(1)
        else:
            self.change_font_size(-1)

    def change_font_size(self, delta):
        """ Changes the font size """
        self.font_size = max(8, min(self.font_size + delta, 32))
        self.text_area.config(font=("Courier", self.font_size))
        self.line_numbers.config(font=("Courier", self.font_size))

    def create_menu(self):
        """Creates the menu bar """
        menu_bar = Menu(self.root)

        file_menu = Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="Open", command=self.open_file, accelerator="Ctrl+O")
        file_menu.add_command(label="Save", command=self.save_file, accelerator="Ctrl+S")
        file_menu.add_command(label="Exit", command=self.root.quit)
        menu_bar.add_cascade(label="File", menu=file_menu)

        settings_menu = Menu(menu_bar, tearoff=0)
        settings_menu.add_command(label="Load ISA Configuration", command=self.load_isa_config)
        settings_menu.add_command(label="Toggle Dark/Light Mode", command=self.toggle_theme)
        menu_bar.add_cascade(label="Settings", menu=settings_menu)

        assemble_menu = Menu(menu_bar, tearoff=0)
        assemble_menu.add_command(label="Assemble", command=self.assemble_code, accelerator="Ctrl+R")
        menu_bar.add_cascade(label="Assembler", menu=assemble_menu)

        about_menu = Menu(menu_bar, tearoff=0)
        about_menu.add_command(label="About", command=self.show_about_info)
        menu_bar.add_cascade(label="About", menu=about_menu)

        self.root.config(menu=menu_bar)

    def show_about_info(self):
        """Displays information about the software."""

        about_message = (
            "BIP-ACE (Assembly Coding Environment)   \n\n"
            "Versão: 1.0.0\n"
            "Autor: André Maiolini\n\n"
            "Descrição: Ferramenta para montagem de código e "
            "comunicação via UART, desenvolvida como meio de "
            "suporte à disciplina de Arquitetura e "
            "Organização de Computadores, permitindo a "
            "configuração de ISAs (Instruction Set "
            "Architectures) e execução de montagens em"
            "hardware real."
        )

        messagebox.showinfo("Sobre", about_message, icon=None)

    def update_theme(self):
        """ Applies the selected theme """

        self.syntax_highlight_theme()

        theme_val = self.dark_theme if self.dark_mode else self.light_theme

        bg, fg = theme_val.get('background'), theme_val.get('foreground')
        line_bg, line_fg = theme_val.get('line_number_bg'), theme_val.get('line_number_fg')
        line_color = theme_val.get('line_separator')

        self.text_area.config(background=bg, foreground=fg, insertbackground=fg)
        self.line_numbers.config(background=line_bg, foreground=line_fg)
        self.separator.config(bg=line_color)
        self.change_font_size(1)
        self.change_font_size(-1)

    def toggle_theme(self):
        """ Applies the selected theme """
        self.dark_mode = not self.dark_mode
        self.update_theme()

    def open_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Assembly Files", "*.asm"), ("All Files", "*.*")])
        if file_path:
            with open(file_path, "r") as file:
                self.text_area.delete("1.0", tk.END)
                self.text_area.insert("1.0", file.read())
            self.highlight_syntax()
            self.update_line_numbers()
            self.change_font_size(1)
            self.change_font_size(-1)

    def save_file(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".asm", filetypes=[("Assembly Files", "*.asm"), ("All Files", "*.*")])
        if file_path:
            with open(file_path, "w") as file:
                file.write(self.text_area.get("1.0", tk.END))

    def assemble_code(self):
        """This method calls the assembler and displays the machine code."""
        Assembler(self.root, self.text_area, self.isa_config, self.dark_theme)
