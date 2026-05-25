const express = require("express");
const axios = require("axios");

const app = express();
app.use(express.json());

const PORT = 3000;
const ML_SERVICE_URL  = process.env.ML_SERVICE_URL  || "http://localhost:8000";
const PHP_SERVICE_URL = process.env.PHP_SERVICE_URL || "http://localhost:8080";
 
let failures = 0;
let lastFailedAt = null;
const THRESHOLD = 3;
const COOLDOWN = 30000; 

function isServiceOpen() {
    if (failures >= THRESHOLD) {
        if (Date.now() - lastFailedAt < COOLDOWN) return true;
        failures = 0; 
    }
    return false;
}

app.post("/recommend", async (req, res) => {
    const { title, top_n, user_id, metadata } = req.body;
    
    if (!title) {
        return res.status(400).json({ error: "Field 'title' wajib diisi" });
    }
  
    if (isServiceOpen()) {
        return res.status(503).json({
            error: "ML Service sedang tidak tersedia, coba lagi nanti",
            retry_after: `${Math.ceil((COOLDOWN - (Date.now() - lastFailedAt)) / 1000)}s`,
        });
    }
  
    try {
        const mlResponse = await axios.post(
            `${ML_SERVICE_URL}/predict`,
            { title, top_n: top_n ?? 5, user_id, metadata },
            { timeout: 5000 }
        );
    
        failures = 0;
    
        return res.json({
            input_title: mlResponse.data.input_title,
            recommendations: mlResponse.data.recommendations,
            total: mlResponse.data.total,
            timestamp: new Date().toISOString(),
        });
    } catch (error) {
        if (error.code === "ECONNREFUSED" || error.code === "ETIMEDOUT") {
            failures++;
            lastFailedAt = Date.now();
            return res.status(503).json({
                error: "ML Service tidak tersedia",
                failures: `${failures}/${THRESHOLD}`,
            });
        }
      
        if (error.response?.status === 404) {
            return res.status(404).json({ error: error.response.data.detail });
        }
        return res.status(500).json({ error: error.message });
    }
});

app.post("/batch-recommend", async (req, res) => {
    const { titles, top_n } = req.body; 
    if (!titles || !Array.isArray(titles) || titles.length === 0) {
        return res.status(400).json({ error: "Field 'titles' wajib diisi" });
    }

    if (isServiceOpen()) {
        return res.status(503).json({
            error: "ML Service sedang tidak tersedia, coba lagi nanti",
            retry_after: `${Math.ceil((COOLDOWN - (Date.now() - lastFailedAt)) / 1000)}s`,
        });
    }   

    try {
        const mlResponse = await axios.post(
            `${ML_SERVICE_URL}/batch-predict`,
            { titles, top_n: top_n ?? 5 },
            { timeout: 10000 }
        );    
        failures = 0; 
        
        return res.json({
            results: mlResponse.data.results,
            total_processed: mlResponse.data.total_processed,
            timestamp: new Date().toISOString(),
        });

    } catch (error) {
        if (error.code === "ECONNREFUSED" || error.code === "ETIMEDOUT") {
            failures++;
            lastFailedAt = Date.now();
            return res.status(503).json({
              error: "ML Service tidak tersedia",
              failures: `${failures}/${THRESHOLD}`,
            });
        } 
        return res.status(500).json({ error: error.message });
    }
});

app.get("/health", async (req, res) => {
    try {
        const mlHealth = await axios.get(`${ML_SERVICE_URL}/health`, { timeout: 3000 });
        return res.json({ status: "ok", ml_service: mlHealth.data });
    } catch {
        return res.status(200).json({ status: "ok", ml_service: "unreachable" });
    }
});

app.get("/watchlist", async (req, res) => {
    try {
        const response = await axios.get(`${PHP_SERVICE_URL}/watchlist`);
        return res.json(response.data);
    } catch (error) {
        if (error.code === "ECONNREFUSED") {
            return res.status(503).json({ error: "PHP Service tidak tersedia" });
        }
        return res.status(500).json({ error: error.message });
    }
});

app.get("/watchlist/:id", async (req, res) => {
    try {
        const response = await axios.get(`${PHP_SERVICE_URL}/watchlist/${req.params.id}`);
        return res.json(response.data);
    } catch (error) {
        if (error.code === "ECONNREFUSED") {
            return res.status(503).json({ error: "PHP Service tidak tersedia" });
        }
        if (error.response?.status === 404) {
            return res.status(404).json({ error: error.response.data.error });
        }
        return res.status(500).json({ error: error.message });
    }
});

app.post("/watchlist", async (req, res) => {
    const { movie_id, title, overview, genres } = req.body;

    if (!movie_id || !title) {
        return res.status(400).json({ error: "Field 'movie_id' dan 'title' wajib diisi" });
    }

    try {
        const response = await axios.post(`${PHP_SERVICE_URL}/watchlist`, {
            movie_id, title, overview, genres
        });
        return res.status(201).json(response.data);
    } catch (error) {
        if (error.code === "ECONNREFUSED") {
            return res.status(503).json({ error: "PHP Service tidak tersedia" });
        }
        if (error.response?.status === 409) {
            return res.status(409).json({ error: error.response.data.error });
        }
        return res.status(500).json({ error: error.message });
    }
});

app.put("/watchlist/:id", async (req, res) => {
    try {
        const response = await axios.put(
            `${PHP_SERVICE_URL}/watchlist/${req.params.id}`,
            req.body
        );
        return res.json(response.data);
    } catch (error) {
        if (error.code === "ECONNREFUSED") {
            return res.status(503).json({ error: "PHP Service tidak tersedia" });
        }
        if (error.response?.status === 404) {
            return res.status(404).json({ error: error.response.data.error });
        }
        return res.status(500).json({ error: error.message });
    }
});

app.delete("/watchlist/:id", async (req, res) => {
    try {
        const response = await axios.delete(`${PHP_SERVICE_URL}/watchlist/${req.params.id}`);
        return res.json(response.data);
    } catch (error) {
        if (error.code === "ECONNREFUSED") {
            return res.status(503).json({ error: "PHP Service tidak tersedia" });
        }
        if (error.response?.status === 404) {
            return res.status(404).json({ error: error.response.data.error });
        }
        return res.status(500).json({ error: error.message });
    }
});

app.get("/health", async (req, res) => {
    try {
        const mlHealth = await axios.get(`${ML_SERVICE_URL}/health`, { timeout: 3000 });
        return res.json({ status: "ok", ml_service: mlHealth.data });
    } catch {
        return res.status(200).json({ status: "ok", ml_service: "unreachable" });
    }
});

app.listen(PORT, () => {
    console.log(`Express Service running on port ${PORT}`);
});