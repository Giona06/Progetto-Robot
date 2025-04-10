<?php
$user = 'root';
$pass = 'root';

if (!isset($_SERVER['PHP_AUTH_USER']) || 
    $_SERVER['PHP_AUTH_USER'] !== $user || 
    $_SERVER['PHP_AUTH_PW'] !== $pass) {
    header('WWW-Authenticate: Basic realm="Area protetta"');
    http_response_code(401);
    exit("Autenticazione richiesta.");
}

$data = [
    'temp' => (int) $_POST['temp'] ?? null,
];
file_put_contents('data.json', json_encode($data, JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE));
header('Content-Type: application/json; charset=utf-8');
