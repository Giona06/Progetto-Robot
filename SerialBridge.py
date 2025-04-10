import serial
import socket
import threading
import time
import requests
from requests.auth import HTTPBasicAuth

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

# Costanti
PHP_SERVER_URL = 'http://localhost/capolavoro/ricezione.php'
SOCKET_HOST = 'localhost'
SOCKET_PORT = 12345
USERNAME = 'root'
PASSWORD = 'root'

porta = selezionaPortaSeriale()
baudrate = selezionaBaudrate()

print(f"Porta selezionata: {porta} - Baudrate: {baudrate}")

ser = serial.Serial(porta, baudrate, timeout=1)

def serialListener():
    """Legge i dati dalla seriale e li invia al server PHP"""
    while True:
        try:
            if ser.in_waiting:
                data = ser.readline().decode(errors='ignore').strip()
                if data:
                    print(f"[SERIALE] → {data}")
                    response = requests.post(PHP_SERVER_URL, data={'dato': data}, auth=HTTPBasicAuth(USERNAME, PASSWORD))
                    print(f"[PHP] ← {response.status_code}")
        except Exception as e:
            print(f"[ERRORE POST] {e}")
            time.sleep(1)

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
                data = conn.recv(1024).decode().strip()
                if data:
                    print(f"[PHP → SERIALE] {data}")
                    ser.write((data + '\n').encode())

threading.Thread(target=serialListener, daemon=True).start()
threading.Thread(target=socketListener, daemon=True).start()

print("[SERVIZIO] Bridge attivo")
try:
    while True:
        time.sleep(0.1) # Da settare tutti i ritardi
except KeyboardInterrupt:
    print("\n[SERVIZIO] Interrotto")
    exit(0)
