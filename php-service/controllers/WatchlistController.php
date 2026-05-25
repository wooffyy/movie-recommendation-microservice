<?php

require_once __DIR__ . "/../models/Watchlist.php";

class WatchlistController {
    private $model;

    public function __construct($conn) {
        $this->model = new Watchlist($conn);
    }

    public function getAll() {
        $data = $this->model->getAll();
        $this->json(200, ["data" => $data]);
    }

    public function getById($id) {
        $item = $this->model->getById($id);
        if (!$item) {
            $this->json(404, ["error" => "Watchlist item not found"]);
            return;
        }
        $this->json(200, ["data" => $item]);
    }

    public function create() {
        $body = $this->getBody();

        if (empty($body["movie_id"]) || empty($body["title"])) {
            $this->json(400, ["error" => "Field 'movie_id' dan 'title' wajib diisi"]);
            return;
        }

        $is_exist = $this->model->getByMovieId($body["movie_id"]);
        if ($is_exist) {
            $this->json(409, ["error" => "Film tersebut sudah ada di watchlist"]);
            return;
        }

        $id = $this->model->create($body);
        $this->json(201, [
            "message" => "Film berhasil ditambahkan ke watchlist",
            "data" => $this->model->getById($id)
        ]);
    }

    public function update($id) {
        $item = $this->model->getById($id);
        if(!$item) {
            $this->json(404, ["error" => "Item tidak ditemukan"]);
            return;
        }

        $body = $this->getBody();
        if (empty($body["title"])) {
            $this->json(400, ["error" => "Field 'title' wajib diisi"]);
            return;
        }

        $this->model->update($id, $body);
        $this->json(200, [
            "message" => "Watchlist berhasil diupdate",
            "data" => $this->model->getById($id)
        ]);
    }

    public function delete($id){
        $item = $this->model->getById($id);
        if(!$item) {
            $this->json(404, ["error" => "Item tidak ditemukan"]);
            return;
        }
        $this->model->delete($id);
        $this->json(200, ["message" => "Film berhasil dihapus dari watchlist"]);
    }

    private function getBody() {
        return json_decode(file_get_contents("php://input"), true) ?? [];
    }

    private function json($code, $data){
        http_response_code($code);
        echo json_encode($data);
    }
}