import serial
import struct
import time

class ComException(Exception):
    """
    Exceção personalizada para erros de comunicação serial.
    """
    def __init__(self, message, port=None, baudrate=None):
        super().__init__(message)
        self.port = port
        self.baudrate = baudrate

    def __str__(self):
        details = f"Erro de comunicação: {super().__str__()}"
        if self.port:
            details += f" | Porta: {self.port}"
        if self.baudrate:
            details += f" | Baudrate: {self.baudrate}"
        return details

class SerialCommunicator:
    
    EOT = 0xF0000000

    def __init__(self, port, baudrate=9600):
        self.port = port
        self.baudrate = baudrate

    def generate_data_packet(self, address_data_pairs):
        """
        Gera uma sequência de pacotes de 32 bits no formato:
        0x0 (4 bits) | address (12 bits) | data (16 bits)
        e finaliza com EOT (end_of_transmission).
        
        :param address_data_pairs: Lista de tuplas (address, data) com valores inteiros.
        :return: Lista representando os pacotes de 32 bits.
        """
        packets = []

        for address, data in address_data_pairs:
            if not (0 <= address < 2**12):
                raise ValueError(f"Endereço {address} fora do intervalo de 12 bits!")
            if not (0 <= data < 2**16):
                raise ValueError(f"Dado {data} fora do intervalo de 16 bits!")

            packet = (0x0 << 28) | (address << 16) | data
            packets.append(packet)

        packets.append(self.EOT)
        return packets

    def send_serial_data(self, packets):
        """
        Envia os pacotes de 32 bits via Serial (UART).

        :param packets: Lista de pacotes de 32 bits para enviar
        """
        try:

            with serial.Serial(self.port, self.baudrate, timeout=1) as ser:
                send_serial_data_period = 10 * 1 / self.baudrate
                send_serial_data_period *= 2

                #print(f"Enviando dados para {self.port} a {self.baudrate} baud...")

                for packet in packets:
                    data_bytes = struct.pack(">I", packet)
                    for byte in data_bytes:
                        ser.write(bytes([byte]))
                        #print(f"Enviado byte: 0x{byte:02X}")
                        time.sleep(send_serial_data_period)

                #print("Transmissão concluída.")

        except serial.SerialException as e:

            print(f"Erro ao abrir a porta serial: {e}")
            raise ComException(f"Erro ao abrir a porta serial: {self.port}")

    def assemble_and_send(self, address_data_pairs):
        packets = self.generate_data_packet(address_data_pairs)
        self.send_serial_data(packets)
