<?php
$host = 'localhost';
$port = '12345';

$socket = socket_create(AF_INET, SOCK_STREAM, SOL_TCP);
if ($socket === false) {
    die("Failed to create socket: " . socket_strerror(socket_last_error()));
}
$conn = socket_connect($socket, $host, $port);
if ($conn === false) {
    die("Failed to connect to $host:$port: " . socket_strerror(socket_last_error($socket)));
}

if(checkData()){
    $data = json_encode([
        'Comando' => (int)$_POST['Comando'],
        'Velocita' => (int)$_POST['Velocita']
    ]);
    socket_write($socket, $data, strlen($data));
    http_response_code(200);
}
else{
    http_response_code(400);
}

socket_close($socket);

function checkData(){
    if(!isset($_POST['Comando']) || !isset($_POST['Velocita'])){
        return false;
    }
    if(!is_numeric($_POST['Comando']) || !is_numeric($_POST['Velocita'])){
        return false;
    }
    if($_POST['Velocita'] < 0 || $_POST['Velocita'] > 100){
        return false;
    }
    if($_POST['Comando'] < 0 || $_POST['Comando'] > 8){
        return false;
    }
    return true;
}
