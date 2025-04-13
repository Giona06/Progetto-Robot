import serial
import socket
import threading
import time
import requests
from requests.auth import HTTPBasicAuth
import struct
import json

DEBUG = True

#Costanti Server
PHP_SERVER_URL = 'http://localhost/capolavoro/ricezione.php'
SOCKET_HOST = 'localhost'
SOCKET_PORT = 12345
USERNAME = 'root'
PASSWORD = 'root'


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

porta = "COM5" if DEBUG else selezionaPortaSeriale()
baudrate = 9600 if DEBUG else selezionaBaudrate()

print(f"Porta selezionata: {porta} - Baudrate: {baudrate}")

ser = serial.Serial(porta, baudrate, timeout=0.1)

#Struttura pacchetto [START_BYTE(1), HEADER_FOLLOW_LINE(1), DATA_FOLLOWLINE(1), HEADER_ULTRASONIC(1), DATA_ULTRASONIC(4), CHECKSUM(1), END_BYTE(1)]
START_BYTE = b'\xaa'
HEADER_FOLLOW_LINE = b'\x01'
HEADER_ULTRASONIC = b'\x02'
HEADER_DIREZIONE = b'\x03'
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

            return {
                "FollowLine": valore_fl,
                "Ultrasonic": valore_us
            }
    
def pack(data):
    """Pack dei dati da inviare alla seriale"""
    data_dir = struct.pack('B', data["Direzione"])
    data_vel = struct.pack('B', data["Velocita"])
    checksum = HEADER_DIREZIONE[0] ^ data_dir[0] ^ HEADER_VELOCITA[0] ^ data_vel[0]
    checksum = struct.pack('B', checksum)
    packet = START_BYTE + HEADER_DIREZIONE + data_dir + HEADER_VELOCITA + data_vel + checksum + END_BYTE
    return packet

def serialListener():
    """Legge i dati dalla seriale e li invia al server PHP"""
    while True:
        try:
            if ser.in_waiting >= PACKET_SIZE:
                data = unpack()
                if data:
                    print(f"[SERIALE] → {data}")
                    response = requests.post(PHP_SERVER_URL, data=data, auth=HTTPBasicAuth(USERNAME, PASSWORD))
                    print(f"[PHP] ← {response.status_code}")
        except Exception as e:
            print(f"[ERRORE POST] {e}")
            time.sleep(0.1)

def socketListener():
    """Riceve dati da socket e li invia alla seriale"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((SOCKET_HOST, SOCKET_PORT))
        s.listen()
        print(f"[SOCKET] In ascolto su porta {SOCKET_PORT}")
        while True:
            conn, addr = s.accept()
            with conn:
                print(f"[SOCKET] Connessione da {addr}")
                data = conn.recv(1024)
                if data:
                    data = json.loads(data)
                    print(f"[PHP → SERIALE] {data}")
                    packet = pack(data)
                    print(f"[SERIALE] → {packet}")
                    ser.write(packet)

threading.Thread(target=serialListener, daemon=True).start()
threading.Thread(target=socketListener, daemon=True).start()

print("[SERVIZIO] Bridge attivo")
try:
    while True:
        time.sleep(0.1)
except KeyboardInterrupt:
    print("\n[SERVIZIO] Interrotto")
    exit(0)