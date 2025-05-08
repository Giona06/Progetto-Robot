import serial
import threading
import time
import struct
from enum import Enum

START_BYTE = 0xAA
END_BYTE = 0xFF
ULTRASONICO_FOLLOWLINE = 0x01
COMANDO = 0x02
DELAY = 0x03

def porteSeriali():
    """Restituisce tutte le porte seriali disponibili"""
    porte = [f"COM{i}" for i in range(256)]
    disponibili = []
    for porta in porte:
        try:
            s = serial.Serial(porta)
            s.close()
            disponibili.append(porta)
        except (OSError, serial.SerialException):
            continue
    return disponibili

def selezionaPortaSeriale():
    disponibili = porteSeriali()
    if not disponibili:
        print("Nessuna porta seriale disponibile.")
        exit(1)

    print("Porte seriali disponibili:")
    for i, port in enumerate(disponibili, start=1):
        print(f"{i}: {port}")

    while True:
        try:
            scelta = int(input(f"Seleziona porta seriale (1-{len(disponibili)}): "))
            if 1 <= scelta <= len(disponibili):
                return disponibili[scelta - 1]
        except ValueError:
            print("Input non valido. Inserisci un numero.")

class Comando(Enum):
    FERMO = 0
    AVANTI = 1
    INDIETRO = 2
    SINISTRA = 3
    DESTRA = 4
    ALZA = 5
    ABBASSA = 6
    APRI = 7
    CHIUDI = 8

class Robot():

    def delay(self, tempo: int):
        data = {
            "Delay": struct.pack('B', tempo)
        }
        self._packetHandler.send_packet(DELAY, data["Delay"])

    def move(self, comando : Comando, velocita: int):
        data = {
            "Comando": struct.pack('B', comando.value),
            "Velocita": struct.pack('B', velocita)
        }
        self._packetHandler.send_packet(COMANDO,  data["Comando"] + data["Velocita"])

    def __init__(self, porta: str, baudrate: int = 9600):
        self._packetHandler = PacketHandler(self, porta, baudrate)
        self._ultrasonico = 0.0
        self._follow_line = 0
        self._packetHandler.start()
    
    @property
    def ultrasonico(self) -> float:
        return self._ultrasonico
    
    @ultrasonico.setter
    def ultrasonico(self, value: float):
        self._ultrasonico = value
    
    @property
    def followLine(self) -> int:
        return self._follow_line
    
    @followLine.setter
    def followLine(self, value: int):
        self._follow_line = value

class PacketHandler():
    def __init__(self, robot: Robot, porta: str, baudrate: int = 9600):
        self.robot = robot
        self.ser = serial.Serial(porta, baudrate)
        self.ser.reset_input_buffer()
        self.ser.reset_output_buffer()
        self.buffer = bytearray()
        self.running = False
    
    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self.read, daemon=True)
        self.thread.start()

    def stop(self):
        self.running = False
        self.thread.join()
        self.ser.close()
    
    def read(self):
        while self.running:
            if self.ser.in_waiting:
                data = self.ser.read(self.ser.in_waiting)
                self.buffer.extend(data)
                self.process_buffer()
            time.sleep(0.01)

    def handle_packet(self, packet_type, payload):
        if packet_type == ULTRASONICO_FOLLOWLINE:
            self.robot.ultrasonico = struct.unpack('<f', payload[:4])[0]
            self.robot.followLine = payload[4]
        else:
            pass

    def process_buffer(self):
        while True:
            if START_BYTE in self.buffer and END_BYTE in self.buffer:
                start = self.buffer.index(START_BYTE)
                end = self.buffer.index(END_BYTE, start)
                packet = self.buffer[start+1:end]
                del self.buffer[:end+1]

                if len(packet) < 4:
                    continue
                
                packet_type = packet[0]
                length = packet[1]
                payload = packet[2:-1]
                checksum = packet[-1]

                if len(payload) != length:
                    continue

                checksum_c = (packet_type + length + sum(payload)) & 0xFF

                if checksum != checksum_c:
                    continue

                self.handle_packet(packet_type, payload)
            else:
                break

    def send_packet(self, packet_type, payload: bytes):
        length = len(payload)
        if length > 255:
            raise ValueError("Il payload non può superare 255 byte.")

        checksum = (packet_type + length + sum(payload)) & 0xFF
        packet = bytearray()
        packet.append(START_BYTE)
        packet.append(packet_type)
        packet.append(length)
        packet.extend(payload)
        packet.append(checksum)
        packet.append(END_BYTE)

        self.ser.write(packet)