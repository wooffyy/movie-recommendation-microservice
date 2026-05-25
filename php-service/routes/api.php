<?php

function route($method, $pattern, $callback) {
    $uri = parse_url($_SERVER["REQUEST_URI"], PHP_URL_PATH);
    $uri = rtrim($uri, "/");
    $regex = preg_replace("/\{[^}]+\}/", "([^/]+)", $pattern);

    if ($_SERVER["REQUEST_METHOD"] === $method && preg_match("#^{$regex}$#", $uri, $matches)) {
        array_shift($matches);
        call_user_func_array($callback, $matches);
        return true;
    }
    return false;
}