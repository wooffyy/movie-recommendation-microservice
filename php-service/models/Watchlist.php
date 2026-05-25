<?php

class Watchlist {
    private $conn = null;
    protected $table = 'watchlist'; 

    public function __construct($conn) {
        $this->conn = $conn;
    }

    public function getAll() {
        $query = "SELECT * FROM {$this->table} ORDER BY added_at DESC";
        
        $stmt = $this->conn->prepare($query);
        $stmt->execute();
        
        return $stmt->fetchAll(PDO::FETCH_ASSOC);
    }

    public function getById($id) {
        $query = "SELECT * FROM {$this->table} WHERE id = ?";
        
        $stmt = $this->conn->prepare($query);
        $stmt->execute([$id]);
        
        return $stmt->fetch(PDO::FETCH_ASSOC);
    }

    public function getByMovieId($movie_id) {
        $stmt = $this->conn->prepare("SELECT * FROM {$this->table} WHERE movie_id = ?");
        $stmt->execute([$movie_id]);
        return $stmt->fetch();
    }

    public function create($data) {
        $query = "INSERT INTO {$this->table} (movie_id, title, overview, genres) VALUES (:movie_id, :title, :overview, :genres)";
        
        $stmt = $this->conn->prepare($query);
        $stmt->execute([
            ":movie_id" => $data["movie_id"],
            ":title"    => $data["title"],
            ":overview" => $data["overview"] ?? "",
            ":genres"   => $data["genres"]   ?? "",
        ]);
        
        return $this->conn->lastInsertId(); 
    }

    public function update($id, $data) {
        $query = "UPDATE {$this->table} SET title = :title, overview = :overview, genres = :genres WHERE id = :id";
        
        $stmt = $this->conn->prepare($query);
        $stmt->execute([
            ":title"    => $data["title"],
            ":overview" => $data["overview"] ?? "",
            ":genres"   => $data["genres"]   ?? "",
            ":id"       => $id,
        ]);
        
        return $stmt->rowCount();
    }

    public function delete($id) {
        $query = "DELETE FROM {$this->table} WHERE id = ?";
        
        $stmt = $this->conn->prepare($query);
        $stmt->execute([$id]);
        
        return $stmt->rowCount();
    }
}