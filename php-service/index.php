<?php

header("Content-Type: application/json");
header("Access-Control-Allow-Origin: *");
header("Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS");
header("Access-Control-Allow-Headers: Content-Type");

if ($_SERVER["REQUEST_METHOD"] === "OPTIONS") {
    http_response_code(204);
    exit;
}

require_once __DIR__ . "/config/db.php";
require_once __DIR__ . "/controllers/WatchlistController.php";
require_once __DIR__ . "/routes/api.php";

$db         = (new Database())->connect();
$controller = new WatchlistController($db);

$matched =
    route("GET", "/watchlist", fn() => $controller->getAll()) ||
    route("GET", "/watchlist/{id}", fn($id) => $controller->getById($id)) ||
    route("POST", "/watchlist", fn() => $controller->create()) ||
    route("PUT", "/watchlist/{id}", fn($id) => $controller->update($id)) ||
    route("DELETE", "/watchlist/{id}", fn($id) => $controller->delete($id));

if (!$matched) {
    http_response_code(404);
    echo json_encode(["error" => "Route not found"]);
}