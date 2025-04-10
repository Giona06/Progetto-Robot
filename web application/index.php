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

$data = "lore";

socket_write($socket, $data, strlen($data));

socket_close($socket);
