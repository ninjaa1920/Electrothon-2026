import express from "express";
import path from "path";
import { fileURLToPath } from "url";

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
app.get("/police/login",(req,res)=>{
    res.render("police_details")
})
const port = process.env.PORT || 3000;
app.listen(port, () => {
  console.log(`Server running on port ${port}`);
});
