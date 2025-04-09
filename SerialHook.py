import serial
import threading
import time

def serial_communication(port, baudrate, ser : serial.Serial):
    try:
        print(f"Connessione aperta sulla porta {port} con baudrate {baudrate}")
        
        while True:
            # Chiede all'utente di inviare un messaggio
            to_send = input("\nInserisci il messaggio da inviare (o 'exit' per uscire): ")
            if to_send.lower() == 'exit':
                print("Chiusura della connessione...")
                break
            
            # Invia il messaggio tramite la porta seriale
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
    # Specifica la porta e il baudrate
    porta = input("Inserisci la porta seriale (es. COM3): ")
    baudrate = int(input("Inserisci il baudrate (es. 9600): "))
   

    ser = serial.Serial(porta, baudrate, timeout=1)
    delay_ms = int(input("Inserisci il delay in millisecondi per la lettura continua: "))

    read_thread = threading.Thread(target=continuous_read, args=(ser, delay_ms), daemon=True)
    read_thread.start()
    serial_communication(porta, baudrate, ser)
