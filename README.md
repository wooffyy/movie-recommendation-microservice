# Movie Recommendation Microservice

Sistem microservice untuk rekomendasi film berbasis Content-Based Filtering menggunakan TF-IDF + Cosine Similarity, diintegrasikan dengan Express.js service.

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
│   └── requirements.txt
└── express-service/
    ├── index.js
    └── package.json
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
- pip

---

### Clone Repository
```bash
git clone https://github.com/wooffyy/movie-recommendation-microservice.git
```
### 1. ML Service (FastAPI)

#### Install dependencies
```bash
cd ml-service
pip install -r requirements.txt
```

#### Train model
> Wajib dijalankan sekali sebelum menjalankan service
```bash
python app/train_model.py
```
Output yang diharapkan:
```
TF-IDF matrix shape: (4803, 10000)
Cosine similarity matrix shape: (4803, 4803)
Test recommendation for 'The Dark Knight':
['The Dark Knight Rises', 'Batman Begins', ...]
Model saved successfully
```

#### Jalankan service
```bash
uvicorn app.main:app --reload --port 8000
```
Service berjalan di: `http://localhost:8000`  
Swagger UI: `http://localhost:8000/docs`

---

### 2. Gateway Service (Express)

```bash
cd express-service
npm install
node index.js
```
Service berjalan di: `http://localhost:3000`

---

## API Endpoints

### ML Service (port 8000)

| Method | Endpoint | Deskripsi |
|--------|----------|-----------|
| GET | `/health` | Status service + info model |
| POST | `/predict` | Rekomendasi berdasarkan 1 judul film |
| POST | `/batch-predict` | Rekomendasi untuk banyak judul sekaligus |

### Express Service (port 3000)

| Method | Endpoint | Deskripsi |
|--------|----------|-----------|
| GET | `/health` | Status Express + status ML service |
| POST | `/recommend` | Forward ke ML `/predict` |
| POST | `/batch-recommend` | Forward ke ML `/batch-predict` |

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
  "timestamp": "2026-05-18T10:00:00.000Z"
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
      "recommendations": [...],
      "total": 2
    },
    {
      "input_title": "Inception",
      "recommendations": [...],
      "total": 2
    }
  ],
  "total_processed": 2,
  "timestamp": "2026-05-18T10:00:00.000Z",
}
```

