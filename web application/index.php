<!DOCTYPE html>
<html lang="it-IT">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Progetto Robot</title>
    <link rel="stylesheet" href="style.css" type="text/css">
    <script src="script.js"></script>
</head>
<body>
    Velocit&agrave; <input type="number" id="velocita" name="velocita" min="1" max="100" value="50">
    <button class="direzione" value="1">Vai Avanti</button>
    <button class="direzione" value="2">Vai Indietro</button>
    <button class="direzione" value="3">Ruota a Sinistra</button>
    <button class="direzione" value="4">Ruota a Destra</button>
    <div id="sensor-data">
        <p>Linea Seguita: <span id="linea"></span></p>
        <p>Valore Ultrasonico: <span id="ultrasonico"></span></p>
    </div>
    <script>
        function fetchSensorData() {
            let data = fetch('si.php')
                .then(response => response.json())
                .then(data => {
                    document.getElementById('linea').innerText = data.FollowLine;
                    document.getElementById('ultrasonico').innerText = data.Ultrasonic;
                })
                .catch(error => console.error('Error fetching sensor data:', error));
        }

        setInterval(fetchSensorData, 100);
    </script>
</body>
</html>