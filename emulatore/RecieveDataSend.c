#include <windows.h>
#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>

#define START_BYTE 0xaa
#define HEADER_CMD 0x03
#define HEADER_VEL 0x04
#define END_BYTE 0xff

uint8_t calculate_checksum(uint8_t header_cmd, uint8_t data_cmd, uint8_t header_vel, uint8_t data_vel) {
    uint8_t checksum_c = header_cmd ^ data_cmd ^ header_vel ^ data_vel;
    return checksum_c;
}

uint8_t xor_checksum(uint8_t *data, size_t length) {
    uint8_t checksum = 0;

    for (size_t i = 0; i < length; i++) {
        checksum ^= data[i];
    }

    return checksum;
}

// Funzione unpack pacchetto
int unpack_data(HANDLE hSerial) {
    uint8_t start_byte;
    uint8_t header_cmd;
    uint8_t data_cmd[1];
    uint8_t header_vel;
    uint8_t data_vel[1];
    uint8_t checksum;
    uint8_t end_byte;
    
    DWORD bytesRead;
    
    while (1) {
        // Read the start byte        
        if (!ReadFile(hSerial, &start_byte, 1, &bytesRead, NULL) || start_byte != START_BYTE) {
            printf("Invalid start byte\n");
            continue;
        }

        // Command Section
        if (!ReadFile(hSerial, &header_cmd, 1, &bytesRead, NULL) || header_cmd != HEADER_CMD) {
            printf("Invalid Command header\n");
            continue;
        }
        
        if (!ReadFile(hSerial, data_cmd, 1, &bytesRead, NULL)) {
            printf("Error reading command data\n");
            continue;
        }

        // Velocity Section
        if (!ReadFile(hSerial, &header_vel, 1, &bytesRead, NULL) || header_vel != HEADER_VEL) {
            printf("Invalid Velocity header\n");
            continue;
        }
        
        if (!ReadFile(hSerial, data_vel, 1, &bytesRead, NULL)) {
            printf("Error reading velocity data\n");
            continue;
        }


        // Check checksum
        if (!ReadFile(hSerial, &checksum, 1, &bytesRead, NULL)) {
            printf("Error reading checksum\n");
            continue;
        }

        // Read end byte
        if (!ReadFile(hSerial, &end_byte, 1, &bytesRead, NULL) || end_byte != END_BYTE) {
            printf("Invalid end byte\n");
            continue;
        }

        // Calculate checksum
        uint8_t calculated_checksum = calculate_checksum(header_cmd, data_cmd[0], header_vel, data_vel[0]);

        // Compare checksum
        if (calculated_checksum != checksum) {
            printf("Checksum mismatch\n");
            continue;
        }

        int8_t value_cmd = data_cmd[0];
        int8_t value_vel = data_vel[0];

        printf("Command Value: %d\n", value_cmd);
        printf("Velocity Value: %d\n", value_vel);

        return 0;
    }

    return -1;
}

int send_data(HANDLE hSerial, int followLine, float ultrasonicDistance) {
    uint8_t followLineBytes[1];
    followLineBytes[0] = (uint8_t)followLine;
    uint8_t bytes[4];     
    uint8_t *ultrasonicBytes = (uint8_t *)&ultrasonicDistance;
    for (int i = 0; i < 4; i++) {
        bytes[i] = ultrasonicBytes[i];
    }
    uint8_t data[] = {0x01, followLineBytes[0], 0x02, bytes[0], bytes[1], bytes[2], bytes[3]};
    size_t length = sizeof(data) / sizeof(data[0]);

    uint8_t packet[] = {
        0xAA,       // START
        data[0],       // HEADER_FOLLOW_LINE
        data[1],       // DATA_FOLLOWLINE
        data[2],       // HEADER_ULTRASONIC
        data[3], data[4], data[5], data[6], // DATA_ULTRASONIC BIG_ENDIAN
        xor_checksum(data, length),       // CHECKSUM
        0xFF        // END
    };

    DWORD bytesWritten;
    if (!WriteFile(hSerial, packet, sizeof(packet), &bytesWritten, NULL)) {
        return 1;
    } else {
        return 0;
    }
    
}

int main() {
    int numero_porta = 0;
    printf("Inserisci il numero della porta COM: ");
    scanf("%d", &numero_porta);
    char porta[8];
    sprintf(porta, "COM%d", numero_porta);
    printf("Porta selezionata: %s\n", porta);

    HANDLE hSerial = CreateFile(porta, GENERIC_READ | GENERIC_WRITE, 0, NULL, OPEN_EXISTING, 0, NULL);


    if (hSerial == INVALID_HANDLE_VALUE) {
        printf("Error opening serial port\n");
        return 1;
    }

    // Parametri porta seriale
    DCB dcbSerialParams = { 0 };
    dcbSerialParams.DCBlength = sizeof(dcbSerialParams);

    if (!GetCommState(hSerial, &dcbSerialParams)) {
        printf("Error getting serial port state\n");
        CloseHandle(hSerial);
        return 1;
    }

    dcbSerialParams.BaudRate = CBR_9600;
    dcbSerialParams.ByteSize = 8;
    dcbSerialParams.StopBits = ONESTOPBIT;
    dcbSerialParams.Parity = NOPARITY;

    if (!SetCommState(hSerial, &dcbSerialParams)) {
        printf("Error setting serial port parameters\n");
        CloseHandle(hSerial);
        return 1;
    }

    DWORD bytesAvailable;

    while (1) {
        int random_followLine = rand() % 4;
        float random_ultrasonicDistance = rand() % 100 + 1;
        send_data(hSerial, random_followLine, random_ultrasonicDistance);
        COMSTAT status;
        if (ClearCommError(hSerial, NULL, &status)) {
            bytesAvailable = status.cbInQue;
            if (bytesAvailable >= 7) {
                int result = unpack_data(hSerial);
            }
        }
        Sleep(100);
    }
    
    CloseHandle(hSerial);
    getchar();
    return 0;
}
