# Non so ancora come chiamarlo

## Requisiti

- [Python 3.x](https://www.python.org/) → servizio bridge
- Librerie Python:

    ```bash
    pip install pyserial requests
    ```

- [XAMPP](https://www.apachefriends.org/it/index.html) → server PHP locale
- [PuTTY](https://apps.microsoft.com/detail/XPFNZKSKLBP7RJ?hl=it-IT&gl=IT&ocid=pdpshare) → monitor seriale per l'invio e la ricezione dei dati (Test Only)

## Installazione porte seriali virtuali e monitor seriale (Test Only)

Se non si dispone del robot ma comunque si vuole provare il programma

### Installazione com0com

- Apri la cartella /emulatore/ ed esegui il setup di com0com
- Segui i passaggi per l'installazione
- Quando richiede quali componenti si vogliono installare deseleziona gli ultimi 2

    ![Componenti](/assets/componenti.png)  

- Una volta terminata l'installazione chiudere il setup senza avviare l'app

### Installazione drivers

- Apri la cartella /emulatore/drivers/ ed esegui setupc come amministratore
- Nel terminale che si è aperto eseguire il seguente comando

    ```bash
    install - -
    ```

### Configurazione porte seriali

- Avviare l'app installata in precedenza

    ![App](/assets/app.png)

- Seleziona **Virtual Port Pair 0**
- Fare doppio click sul nome delle porte e rinominarle (usa la prima coppia di porte disponibile)
  - CNCA0 → COM4
  - CNCA0 → COM5

  ![Programma](/assets/programma.png)

- Una volta rinominate cliccare su applica

### Verica porte virtuali

Per verificare se tutto è stato eseguito correttamente seguire i seguenti passaggi

- Digita **Gestione Dispositivi** nella barra di ricerca e apri il programma, poi seleziona **com0com - serial port emulators**
- Verifica che siano presenti 3 dispositivi, uno è il bus e i restanti sono le porte

    ![Verifica](/assets/verifica.png)  
Si dovrebbe visualizzare una situazione simile all'immagine soprastante

### Monitor seriale (PuTTY)

- Avviare PuTTY
- Selezionare la voce **Terminal**
- Settare **Local echo** e **Local line editing** su **Force on**

    ![Terminale](/assets/terminale.png)  

- Selezionare la voce **Session**
- Settare **Connection type** su **Serial**
- Settare **Serial line** con il nome della **prima** porta nella coppia
- Per salvare la configurazione, seleziona **Default Settings** e premi su **Save**

    ![Sessione](/assets/sessione.png)  

- Dopo averlo configurato come nell'immagine soprastante, premere **Open**  

Questo avvierà il monitor seriale, dal quale possiamo inviare/ricevere dati

## Prossima sezione :D
