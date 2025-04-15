import serial
import threading
import time
import random
import struct
from enum import Enum

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
            else:
                print("Porta non valida.")
        except ValueError:
            print("Inserisci un numero valido.")

def selezionaBaudrate():
    while True:
        try:
            baudrate = int(input("Baudrate (default 9600): ") or 9600)
            if baudrate in serial.Serial.BAUDRATES:
                return baudrate
            else:
                print("Baudrate non valido.")
        except ValueError:
            print("Inserisci un numero valido.")

porta = selezionaPortaSeriale()
baudrate = selezionaBaudrate()

print(f"Porta selezionata: {porta} - Baudrate: {baudrate}")

ser = serial.Serial(porta, baudrate, timeout=0.1)

ultrasonico = 0.0
follow_line = 0

#Struttura pacchetto [START_BYTE(1), HEADER_FOLLOW_LINE(1), DATA_FOLLOWLINE(1), HEADER_ULTRASONIC(1), DATA_ULTRASONIC(4), CHECKSUM(1), END_BYTE(1)]
START_BYTE = b'\xaa'
HEADER_FOLLOW_LINE = b'\x01'
HEADER_ULTRASONIC = b'\x02'
HEADER_COMANDO = b'\x03'
HEADER_VELOCITA = b'\x04'
END_BYTE = b'\xff'

LENGTH_FOLLOW_LINE = 1
LENGTH_ULTRASONIC = 4
PACKET_SIZE = 10

# Più efficciente usare i byte invece di stringhe :'D
def unpack():
    """Unpack dei dati dalla seriale"""
    while True:
        if ser.read(1) == START_BYTE:
            # Sezione follow line
            header_fl = ser.read(1)
            if header_fl != HEADER_FOLLOW_LINE:
                print("Pacchetto non valido")
                continue
            data_fl = ser.read(LENGTH_FOLLOW_LINE)

            # Sezione ultrasonico
            header_us = ser.read(1)
            if header_us != HEADER_ULTRASONIC:
                print("Pacchetto non valido")
                continue
            data_us = ser.read(LENGTH_ULTRASONIC)

            # Controllo checksum xor
            checksum = ser.read(1)
            end = ser.read(1)
            if end != END_BYTE:
                print("Pacchetto non valido")
                continue
            
            checksum_c = header_fl[0] ^ data_fl[0] ^ header_us[0]
            for byte in data_us:
                checksum_c ^= byte
            checksum_c = struct.pack('B', checksum_c)

            if checksum_c != checksum:
                print("Checksum non valido")
                continue
            
            valore_fl = struct.unpack('B', data_fl)[0] # B = unsigned char (1 byte)
            valore_us = struct.unpack('<f', data_us)[0] # <f = float(4 bytes) ordine Little Endian
            valore_us = round(valore_us, 2)
            return {
                "FollowLine": valore_fl,
                "Ultrasonic": valore_us
            }
    
def pack(data):
    """Pack dei dati da inviare alla seriale"""
    data_cmd = struct.pack('B', data["Comando"])
    data_vel = struct.pack('B', data["Velocita"])
    checksum = HEADER_COMANDO[0] ^ data_cmd[0] ^ HEADER_VELOCITA[0] ^ data_vel[0]
    checksum = struct.pack('B', checksum)
    packet = START_BYTE + HEADER_COMANDO + data_cmd + HEADER_VELOCITA + data_vel + checksum + END_BYTE
    return packet

def serialListener():
    """Legge i dati dalla seriale e li invia al server PHP"""
    while True:
        try:
            if ser.in_waiting >= PACKET_SIZE:
                data = unpack()
                if data:
                    print(f"[SERIALE] → {data}") 
                    ultrasonico = data["Ultrasonic"]
                    follow_line = data["FollowLine"]
        except Exception as e:
            print(f"[ERRORE POST] {e}")
            time.sleep(0.1)

#Funzione per muovimenti del robot

def move(comando : Comando, velocita: int):
    """Invia un comando alla seriale"""
    data = {
        "Comando": comando.value,
        "Velocita": velocita
    }
    packet = pack(data)
    print(f"[SERIALE] → {packet}")
    ser.write(packet)

####Programma princimale

def zona_bianca():
    move(Comando.AVANTI, 30)
    if follow_line == 0:
        print("[SERIALE] → Rilevato bordo")
        move(Comando.AVANTI, 0)
        move(Comando.INDIETRO, 50)
        time.sleep(1)
        if random.randint(1, 10) > 5:
            print("[SERIALE] → Svolta a destra")
            move(Comando.DESTRA, 50)
            time.sleep(1.5)
        else:
            print("[SERIALE] → Svolta a sinistra")
            move(Comando.SINISTRA, 50)
            time.sleep(1.5)

def spingi_ostacolo():
    move(Comando.AVANTI, 30)
    if ultrasonico < 25:
        move(Comando.AVANTI, 100)
        print("[SERIALE] → Ostacolo rilevato")

def socketListener():
    """Riceve dati da socket e li invia alla seriale"""
    input("Premere invio per avviare il programma") #Accendere il robot prima di avviare il programma
    while True:
        zona_bianca()
        spingi_ostacolo()

###

threading.Thread(target=serialListener, daemon=True).start()
threading.Thread(target=socketListener, daemon=True).start()

print("[SERVIZIO] Bridge attivo")
try:
    while True:
        time.sleep(0.1)
except KeyboardInterrupt:
    print("\n[SERVIZIO] Interrotto")
    exit(0)