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

/* Fix __dirname in ES modules */
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

/* Set EJS as view engine */
app.set("view engine", "ejs");

/* Tell Express where EJS files are */
app.set("views", path.join(__dirname, "../frontend"));

/* Tell Express where static files (CSS) are */
app.use(express.static(path.join(__dirname, "../frontend/public")));

/* Parse form data */
app.use(express.urlencoded({ extended: true }));

/* Home route */
app.get("/", (req, res) => {
    res.render("first"); // loads first.ejs
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
      // Login success
      res.redirect("/women/dashboard");
    } else {
      // Invalid credentials
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
const port = process.env.PORT || 3000;
app.listen(port, () => {
    console.log(`Server running on port ${port}`);
});
