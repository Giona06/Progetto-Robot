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
<div class="velocita-container">
        <label for="velocita">Velocità</label>
        <input type="number" id="velocita" name="velocita" min="1" max="100" value="50">
    </div>

    <div class="stile-controller">
        <div class="pannello-movimento">
            <div class="joystick">
                <button class="comando movimento su" value="1">↑</button>
                <div class="middle-row">
                    <button class="comando movimento sinistra" value="3">↶</button>
                    <div class="spazio"></div>
                    <button class="comando movimento destra" value="4">↷</button>
                </div>
                <button class="comando movimento giu" value="2">↓</button>
            </div>
        </div>

        <div class="pannello-azione">
            <div class="joystick">
                <button class="comando azione su " value="5">Alza</button>
                <div class="middle-row">
                    <button class="comando azione sinistra " value="7">Apri</button>
                    <div class="spazio"></div>
                    <button class="comando azione destra " value="8">Chiudi</button>
                </div>
                <button class="comando azione giu " value="6">Abbassa</button>
            </div>
        </div>
    </div>

    <div id="sensor-data">
        <p>Valore FollowLine: <span id="linea"></span></p>
        <p>Valore Ultrasonico: <span id="ultrasonico"></span></p>
    </div>
</body>
</html>