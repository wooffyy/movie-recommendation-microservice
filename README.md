# Movie Recommendation Microservice

Sistem microservice untuk rekomendasi film berbasis Content-Based Filtering menggunakan TF-IDF + Cosine Similarity, diintegrasikan dengan Express.js Gateway dan PHP Watchlist Service.

---

## Struktur Project

```
├── ml-service/
│   ├── app/
│   │   ├── main.py
│   │   ├── train_model.py
│   │   └── models/
│   │       ├── tfidf_vectorizer.pkl
│   │       ├── cosine_sim.pkl
│   │       ├── title_to_idx.pkl
│   │       └── movies_metadata.csv
│   ├── dataset/
│   │   ├── tmdb_5000_movies.csv
│   │   └── tmdb_5000_credits.csv
│   ├── Dockerfile
│   └── requirements.txt
├── express-service/
│   ├── index.js
│   ├── package.json
│   └── Dockerfile
├── php-service/
│   ├── config/
│   │   └── db.php
│   ├── controllers/
│   │   └── WatchlistController.php
│   ├── models/
│   │   └── Watchlist.php
│   ├── routes/
│   │   └── api.php
│   ├── index.php
│   ├── init.sql
│   └── Dockerfile
└── docker-compose.yml
```

---

## Dataset & Model

### Dataset
**TMDB 5000 Movie Dataset** dari Kaggle  
https://www.kaggle.com/datasets/tmdb/tmdb-movie-metadata

Terdiri dari 2 file:
- `tmdb_5000_movies.csv` — metadata film (judul, overview, genre, keywords)
- `tmdb_5000_credits.csv` — data cast & crew

Total: 4803 film setelah preprocessing

### Model
**Content-Based Filtering** dengan:
- **TF-IDF Vectorizer** (`max_features=10000`), untuk mengubah teks *soup* (gabungan overview + genre + keywords + cast + director) menjadi vektor numerik
- **Cosine Similarity**, untuk mengukur kemiripan antar film berdasarkan vektor TF-IDF

Disimpan dengan joblib dan di-load saat startup FastAPI

---

## Instalasi & Menjalankan

### Prerequisites
- Python 3.10+
- Node.js 18+
- PHP 8.2+
- Docker & Docker Compose

### Clone Repository
```bash
git clone https://github.com/wooffyy/movie-recommendation-microservice.git
cd movie-recommendation-microservice
```

---

### Menjalankan dengan Docker (Recommended)

#### 1. Train model terlebih dahulu
> Wajib dijalankan sekali sebelum build Docker
```bash
cd ml-service
pip install -r requirements.txt
python app/train_model.py
cd ..
```

Output yang diharapkan:
```
TF-IDF matrix shape: (4803, 10000)
Cosine similarity matrix shape: (4803, 4803)
Test recommendation for 'The Dark Knight':
['The Dark Knight Rises', 'Batman Begins', ...]
Model saved successfully
```

#### 2. Jalankan semua service
```bash
docker-compose up --build
```

Seluruh service akan berjalan di:

| Service | URL |
|---------|-----|
| Express Gateway | http://localhost:3000 |
| ML Service | http://localhost:8000 |
| PHP Watchlist Service | http://localhost:8080 |
| Swagger UI | http://localhost:8000/docs |

#### Menghentikan service
```bash
docker-compose down        # stop, data MySQL tetap ada
docker-compose down -v     # stop + hapus data MySQL
```

---

### Menjalankan Manual (Tanpa Docker)

#### 1. ML Service (FastAPI)
```bash
cd ml-service
pip install -r requirements.txt
python app/train_model.py
uvicorn app.main:app --reload --port 8000
```

#### 2. PHP Watchlist Service
```bash
cd php-service
php -S localhost:8080
```

#### 3. Express Gateway
```bash
cd express-service
npm install
node index.js
```

---

## API Endpoints

### ML Service (port 8000)

| Method | Endpoint | Deskripsi |
|--------|----------|-----------|
| GET | `/health` | Status service + info model |
| POST | `/predict` | Rekomendasi berdasarkan 1 judul film |
| POST | `/batch-predict` | Rekomendasi untuk banyak judul sekaligus |

### PHP Watchlist Service (port 8080)

| Method | Endpoint | Deskripsi |
|--------|----------|-----------|
| GET | `/watchlist` | Ambil semua item watchlist |
| GET | `/watchlist/{id}` | Ambil satu item watchlist |
| POST | `/watchlist` | Tambah film ke watchlist |
| PUT | `/watchlist/{id}` | Update item watchlist |
| DELETE | `/watchlist/{id}` | Hapus item dari watchlist |

### Express Gateway (port 3000)

| Method | Endpoint | Forward ke |
|--------|----------|------------|
| GET | `/health` | — (cek status ML service) |
| POST | `/recommend` | ML `/predict` |
| POST | `/batch-recommend` | ML `/batch-predict` |
| GET | `/watchlist` | PHP `/watchlist` |
| GET | `/watchlist/:id` | PHP `/watchlist/{id}` |
| POST | `/watchlist` | PHP `/watchlist` |
| PUT | `/watchlist/:id` | PHP `/watchlist/{id}` |
| DELETE | `/watchlist/:id` | PHP `/watchlist/{id}` |

---

## Contoh Request & Response

### POST /recommend
**Request:**
```json
{
  "title": "The Dark Knight",
  "top_n": 3
}
```
**Response:**
```json
{
  "input_title": "The Dark Knight",
  "recommendations": [
    {
      "id": 272,
      "title": "The Dark Knight Rises",
      "overview": "Following the death of District Attorney Harvey Dent...",
      "genres": "Action Crime Drama Thriller"
    }
  ],
  "total": 3,
  "timestamp": "2026-05-25T10:00:00.000Z"
}
```

### POST /batch-recommend
**Request:**
```json
{
  "titles": ["The Dark Knight", "Inception"],
  "top_n": 2
}
```
**Response:**
```json
{
  "results": [
    {
      "input_title": "The Dark Knight",
      "recommendations": [],
      "total": 2
    },
    {
      "input_title": "Inception",
      "recommendations": [],
      "total": 2
    }
  ],
  "total_processed": 2,
  "timestamp": "2026-05-25T10:00:00.000Z"
}
```

### POST /watchlist
**Request:**
```json
{
  "movie_id": 272,
  "title": "The Dark Knight Rises",
  "overview": "Following the death of District Attorney Harvey Dent...",
  "genres": "Action Crime Drama Thriller"
}
```
**Response:**
```json
{
  "message": "Film berhasil ditambahkan ke watchlist",
  "data": {
    "id": 1,
    "movie_id": 272,
    "title": "The Dark Knight Rises",
    "overview": "Following the death of District Attorney Harvey Dent...",
    "genres": "Action Crime Drama Thriller",
    "added_at": "2026-05-25 10:00:00"
  }
}
```

---

## Circuit Breaker

Express Gateway mengimplementasikan circuit breaker sederhana untuk koneksi ke ML Service:

| Parameter | Value |
|-----------|-------|
| Threshold | 3 kali gagal berturut-turut |
| Cooldown | 30 detik |

Apabila ML Service gagal dijangkau sebanyak 3 kali, circuit breaker akan terbuka dan seluruh request ke `/recommend` dan `/batch-recommend` akan langsung dikembalikan dengan status 503 tanpa meneruskan request ke ML Service, hingga cooldown selesai.
