import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
from SerialGUI import SerialGUI

class AssemblyException(Exception):
    """
    Exceção personalizada para erros no processo de montagem de código.
    """
    def __init__(self, message, line):
        super().__init__(message)
        self.line = line

    def __str__(self):
        return f"ERROR LINE {self.line}: {super().__str__()}"

class Assembler:

    def __init__(self, root, text_area, isa_config, dark_theme):
        self.root = root
        self.text_area = text_area
        self.isa_config = isa_config
        self.dark_theme = dark_theme
        self.machine_code = []
        self.assembled_code = []
        self.assemble_code()

    def assemble_code(self):
        """Assemble the code and generate machine code with addresses."""

        try:

            assembly_code = self.text_area.get("1.0", tk.END).strip().split("\n")
            machine_code = []
            label_addresses = {}
            current_address = 0
            processed_instructions = []

            # First Pass: Identify Labels
            for line in assembly_code:
                line = line.split(";")[0].strip()  # Remove comments
                if not line:
                    continue  # Skip empty lines

                if ":" in line:  # Label definition
                    label = line.split(":")[0].strip()
                    label_addresses[label] = current_address  # Store address for label
                    continue  # Labels don't generate instructions

                processed_instructions.append(line)
                current_address += 1  # Increment memory address for instruction

            # Second Pass: Convert to Machine Code
            assembled_code = []
            for index, line in enumerate(processed_instructions):
                try:
                    parts = line.split()
                    instr = parts[0]
                    operand = parts[1] if len(parts) > 1 else None

                    if instr not in self.isa_config["instructions"]:
                        raise AssemblyException(f"Invalid instruction {instr}", index+1)

                    opcode = self.isa_config["instructions"][instr]["opcode"]
                    format_type = self.isa_config["instructions"][instr]["format"]

                    if format_type == "0":  # No operand
                        operand_bin = "000000000000"
                    elif format_type == "1":  # Has an operand
                        if operand is None:
                            raise AssemblyException(f"Missing operand for {instr}", index+1)
                        elif operand in self.isa_config["registers"]:  # Register operand
                            operand_bin = self.isa_config["registers"][operand].zfill(12)
                        elif operand.isdigit():  # Numeric operand
                            operand_bin = format(int(operand), "012b")  # Convert number to 12-bit binary
                        elif operand in label_addresses:  # Label reference
                            operand_bin = format(label_addresses[operand], "012b")  # Convert label address to 12-bit binary
                        else:
                            raise AssemblyException(f"Invalid operand {operand}", index+1)
   
                    else:
                        raise AssemblyException(f"Unknown format {format_type}", index+1)

                    binary_instr = opcode + operand_bin  # Full 16-bit machine code
                    binary_address = format(index, "016b")  # 16-bit binary address
                    hex_address = format(index, "x").upper()  # Address in lowercase hex
                    hex_instr = format(int(binary_instr, 2), "04x").upper()  # 16-bit instruction in hex

                    assembled_code.append(f"{hex_address} : {hex_instr}")  # For .cdm export
                    machine_code.append(f"{binary_address}: {binary_instr}")  # For display

                except AssemblyException as e:
                    messagebox.showerror("Error", str(e))
                    return

            # Store machine code for export
            self.machine_code = machine_code
            self.assembled_code = assembled_code

            self.display_machine_code(machine_code)  # Show formatted binary output

        except Exception as e:
            
            messagebox.showerror("Erro de Execução", f"Ocorreu um erro inesperado: {str(e)}")

    def serial_communication(self):
        """Open the serial communication window."""
        data_pairs = []
        for line in self.assembled_code:
            address, data = line.split(":")
            data_pairs.append((int(address, 16), int(data, 16)))
        
        SerialGUI(self.root, data_pairs)

    def export_cdm(self):
        """Export machine code as a .cdm file."""
        file_path = filedialog.asksaveasfilename(defaultextension=".cdm", filetypes=[("Cedar Logic Memory Files", "*.cdm"), ("All Files", "*.*")])
        if file_path:
            with open(file_path, "w") as cdm_file:
                cdm_file.write("\n".join(self.assembled_code))  # Use hex format

    def save_binary(self):
        """Save the machine code as a .bin file."""
        file_path = filedialog.asksaveasfilename(defaultextension=".bin", filetypes=[("Binary Files", "*.bin"), ("All Files", "*.*")])
        if file_path:
            with open(file_path, "wb") as bin_file:
                for instruction in self.machine_code:
                    bin_file.write(int(instruction.split()[1], 2).to_bytes(2, byteorder='big'))

    def display_machine_code(self, machine_code):
        """Display the generated machine code in a new window."""

        output_window = tk.Toplevel(self.root)
        output_window.title("Machine Code Output")
        output_window.geometry("650x1000")  # Ajustei a altura para melhorar a visualização
        output_window.option_add("*Font", "Arial 14")
        output_window.resizable(0, 0)
        output_window.configure(bg=self.dark_theme.get('background'))

        # Block interaction with the main window
        output_window.grab_set()

        path = "assets/assemble.png"
        load = Image.open(path)
        render = ImageTk.PhotoImage(load)
        output_window.iconphoto(False, render)

        # Criar um frame para conter a Text e a Scrollbar
        text_frame = tk.Frame(output_window)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Criar uma Scrollbar vertical
        scrollbar = tk.Scrollbar(text_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Criar a área de texto
        output_text = tk.Text(
            text_frame, wrap="word", font=("Cascadia Mono", 20), padx=10, pady=10, 
            yscrollcommand=scrollbar.set  # Associa a Scrollbar ao Text
        )
        output_text.pack(fill=tk.BOTH, expand=True)

        # Configurar a Scrollbar para controlar a Text
        scrollbar.config(command=output_text.yview)

        # Inserir o código de máquina no text area
        output_text.insert("1.0", "\n".join(machine_code))
        output_text.config(state=tk.DISABLED)

        # Criar um frame para os botões
        button_frame = tk.Frame(output_window, bg=self.dark_theme.get('background'))
        button_frame.pack(pady=7)

        # Botão para salvar como .bin
        btn_bin = tk.Button(button_frame, text="Save BIN", command=self.save_binary, font=("Courier New", 14, "bold"), bg="#187498", fg="white", padx=5)
        btn_bin.pack(side=tk.LEFT, padx=5)

        # Botão para exportar como .cdm
        btn_cdm = tk.Button(button_frame, text="Export CDM", command=self.export_cdm, font=("Courier New", 14, "bold"), bg="#187498", fg="white", padx=5)
        btn_cdm.pack(side=tk.LEFT, padx=5)

        # Botão para abrir a comunicação serial
        btn_serial = tk.Button(button_frame, text="Serial", command=self.serial_communication, font=("Courier New", 14, "bold"), bg="#187498", fg="white", padx=5)
        btn_serial.pack(side=tk.LEFT, padx=5)

        # Garantir que a janela fique no topo
        output_window.grab_set()
        output_window.wait_window()  # Esperar até a janela ser fechada
