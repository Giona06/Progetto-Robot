import serial
import threading
import time

def serial_ports():
    ports = [f"COM{i}" for i in range(256)]
    available_ports = []
    for port in ports:
        try:
            s = serial.Serial(port)
            s.close()
            available_ports.append(port)
        except (OSError, serial.SerialException):
            pass
    return available_ports

def serial_communication(port, baudrate, ser : serial.Serial):
    try:
        print(f"Connessione aperta sulla porta {port} con baudrate {baudrate}")
        while True:
            to_send = input("\nInserisci il messaggio da inviare: ")
            ser.write(to_send.encode('utf-8'))
            print(f"\nMessaggio inviato: {to_send}")
    except serial.SerialException as e:
        print(f"Errore nella connessione seriale: {e}")
    except KeyboardInterrupt:
        print("\nInterruzione manuale. Chiusura della connessione...")
    finally:
        if 'ser' in locals() and ser.is_open:
            ser.close()
            print("Connessione seriale chiusa.")

def continuous_read(ser, delay_ms):
        try:
            while True:
                if ser.in_waiting > 0:
                    response = ser.readline().decode('utf-8').strip()
                    print(f"\nRisposta ricevuta: {response}")
                time.sleep(delay_ms / 1000.0)
        except KeyboardInterrupt:
            print("\nInterruzione manuale del thread di lettura.")

if __name__ == "__main__":
    available_ports = serial_ports()
    if not available_ports:
        print("Nessuna porta seriale disponibile.")
        exit(1)
    porta = input(f"Inserisci la porta seriale (es. COM3):")
    while porta not in available_ports:
        print(f"La porta {porta} non è disponibile. Porte disponibili: {', '.join(available_ports)}")
        porta = input("Inserisci una porta seriale valida (es. COM3):")
    baudrate = 9600
    ser = serial.Serial(porta, baudrate, timeout=1)
    read_thread = threading.Thread(target=continuous_read, args=(ser, 1000), daemon=True)
    read_thread.start()
    serial_communication(porta, baudrate, ser)
