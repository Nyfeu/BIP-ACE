import tkinter as tk
from tkinter import ttk, messagebox
import serial.tools.list_ports
from SerialCommunicator import SerialCommunicator, ComException

def get_available_ports():
    ports = serial.tools.list_ports.comports()
    return [port.device for port in ports]

class SerialGUI:

    def __init__(self, root, data_pairs):

        self.root = root

        available_ports = get_available_ports()

        if not available_ports:
            messagebox.showerror("Erro", "Nenhuma porta serial disponível!")
            return

        serial_window = tk.Toplevel(self.root)
        serial_window.title("Serial")
        serial_window.geometry("300x275")
        serial_window.resizable(False, False)

        serial_window.configure(bg='#f0f0f0')
        self.data_pairs = data_pairs

        # Block interaction with the main window
        serial_window.grab_set()

        ttk.Label(serial_window, text="Porta COM:").pack(pady=5)
        self.port_var = tk.StringVar()

        self.port_dropdown = ttk.Combobox(serial_window, textvariable=self.port_var, values=available_ports, state='readonly', width=12)
        if available_ports:
            self.port_dropdown.current(0)
        self.port_dropdown.pack(pady=5)

        ttk.Label(serial_window, text="Baud Rate (bps):").pack(pady=5)
        self.baudrate_entry = ttk.Entry(serial_window, width=15)
        self.baudrate_entry.insert(0, "9600")
        self.baudrate_entry.pack(pady=5)

        self.send_button = ttk.Button(serial_window, text="Enviar", command=self.send_data)
        self.send_button.pack(pady=10)

        self.progress = ttk.Progressbar(serial_window, orient="horizontal", length=200, mode='determinate')
        self.progress.pack(pady=10)

        # Ensure the window stays on top
        serial_window.grab_set()
        serial_window.wait_window()  # Wait until the serial window is closed


    def send_data(self):
        port = self.port_var.get()
        baudrate = self.baudrate_entry.get()
        try:
            baudrate = int(baudrate)
        except ValueError:
            messagebox.showerror("Erro", "Baud rate inválido!")
            return

        address_data_pairs = self.data_pairs

        if not port:
            messagebox.showerror("Erro", "Porta serial não especificada!")
            return

        try:

            communicator = SerialCommunicator(port, baudrate)

        except ComException as e:
            
            messagebox.showerror("Erro", f"Erro ao abrir a porta serial: {e}")
            return

        packets = communicator.generate_data_packet(address_data_pairs)

        self.progress['value'] = 0
        step = 100 / len(packets)

        for packet in packets:
            communicator.send_serial_data([packet])
            self.progress['value'] += step
            self.root.update_idletasks()

        messagebox.showinfo("Concluído", "Transmissão concluída!")

