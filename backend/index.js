import express from "express";
import path from "path";
import { fileURLToPath } from "url";
import pkg from "pg";
import http from "http";
import { Server } from "socket.io";

const { Pool } = pkg;
const DEMO_MODE = true;

/* 1️⃣ CREATE EXPRESS APP FIRST */
const app = express();

/* 2️⃣ CREATE HTTP SERVER + SOCKET.IO */
const server = http.createServer(app);
const io = new Server(server);

/* 3️⃣ DATABASE (optional in demo) */
const db = new Pool({
    user: "postgres",
    host: "localhost",
    database: "postgres",
    password: "Debayan@1904",
    port: 5432,
});

/* 4️⃣ SOCKET.IO LOGIC */
let latestRisk = {
    level: "Safe",
    description: ""
};







io.on("connection", (socket) => {
    console.log("Client connected:", socket.id);

    // Send initial state
    socket.emit("risk_update", latestRisk);

    socket.on("new_alert", (data) => {
        // LOG EVERYTHING
        const time = new Date().toLocaleTimeString();
        if (data.riskLevel === "Critical") {
            console.log(`[${time}] 🚨 CRITICAL ALERT RECEIVED:`, data.description);
        } else {
            // Optional: Comment out safe logs if too noisy, but for now keep them to see the rhythm
            // console.log(`[${time}] 🟢 Safe Update`); 
        }

        // UPDATE GLOBAL STATE
        latestRisk = {
            level: data.riskLevel,
            description: data.description,
            location: data.location || "Unknown",
            latitude: data.latitude,
            longitude: data.longitude,
            timestamp: data.timestamp || Date.now()
        };

        // BROADCAST TO ALL CLIENTS
        io.emit("risk_update", latestRisk);

        if (data.riskLevel === "Critical") {
            console.log(`[${time}] 📡 Broadcasted CRITICAL RISK to all clients`);
        }
    });
});

/* 5️⃣ EXPRESS CONFIG */
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

app.set("view engine", "ejs");
app.set("views", path.join(__dirname, "../frontend"));
app.use(express.static(path.join(__dirname, "../frontend/public")));
app.use(express.urlencoded({ extended: true }));

/* 6️⃣ ROUTES */
app.get("/", (req, res) => res.render("first"));
app.get("/women/login", (req, res) => res.render("auth"));
app.get("/police/login", (req, res) => res.render("police_details"));

app.post("/women/login", (req, res) => {
    if (DEMO_MODE) return res.redirect("/women/dashboard");
});

app.post("/women/register", (req, res) => {
    if (DEMO_MODE) return res.redirect("/women/dashboard");
});

app.get("/women/dashboard", (req, res) => {
    res.render("women_dashboard");
});

app.post("/police/login", (req, res) => {
    if (DEMO_MODE) return res.redirect("/police/dashboard");
});

app.get("/police/dashboard", (req, res) => {
    res.render("police_dashboard");
});

/* 7️⃣ START SERVER (REPLACES app.listen) */
const port = process.env.PORT || 3000;
server.listen(port, () => {
    console.log(`✅ Server running on port ${port}`);
});
