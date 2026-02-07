import express from "express";
import path from "path";
import { fileURLToPath } from "url";
import pkg from "pg";
const { Pool } = pkg;

const db = new Pool({
    user: "postgres",
    host: "localhost",
    database: "postgres",
    password: "Debayan@1904",
    port: 5432,
});
const app = express();
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
app.set("view engine", "ejs");
app.set("views", path.join(__dirname, "../frontend"));
app.use(express.static(path.join(__dirname, "../frontend/public")));
app.use(express.urlencoded({ extended: true }));
app.get("/", (req, res) => {
    res.render("first");
});
app.get("/police/login", (req, res) => {
    res.render("police_details")
})
app.get("/women/login", (req, res) => {
    res.render("auth")
})
app.post("/women/register", async (req, res) => {
    const { name, email, password } = req.body;
    try {
        const result = await db.query(
            "INSERT INTO women_users (name, email, password) VALUES ($1, $2, $3) RETURNING *",
            [name, email, password]
        );
        console.log(result.rows[0]);
        res.redirect("/women/dashboard");
    } catch (err) {
        console.error(err);
        res.status(500).send("Error registering user");
    }
});
app.post("/women/login", async (req, res) => {
    const { email, password } = req.body;

    try {
        const result = await db.query(
            "SELECT * FROM women_users WHERE email = $1 AND password = $2",
            [email, password]
        );

        if (result.rows.length > 0) {
            res.redirect("/women/dashboard");
        } else {
            res.render("auth", { error: "Invalid email or password" });
        }
    } catch (err) {
        console.error(err);
        res.render("auth", { error: "Login failed" });
    }
});
app.get("/women/dashboard", (req, res) => {
    res.render("women_dashboard");
});
app.post("/police/login", async (req, res) => {
    const { officer_name, batch_number } = req.body;

    try {
        const result = await db.query(
            "SELECT * FROM police_users WHERE TRIM(UPPER(officer_name)) = TRIM(UPPER($1)) AND TRIM(UPPER(batch_number)) = TRIM(UPPER($2))",
            [officer_name, batch_number]
        );

        if (result.rows.length > 0) {
            res.redirect("/police/dashboard");
        } else {
            res.render("police_details", {
                error: "Unauthorized access"
            });
        }
    } catch (err) {
        console.error(err);
        res.render("police_details", {
            error: "Server error"
        });
    }
});

app.get("/police/dashboard", (req, res) => {
    res.render("police_dashboard");
});
const port = process.env.PORT || 3000;
app.listen(port, () => {
    console.log(`Server running on port ${port}`);
});
