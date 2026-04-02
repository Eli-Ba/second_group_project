from flask import Flask, request, redirect, url_for, render_template_string, session  # type: ignore[import]
import sqlite3
import bcrypt

app = Flask(__name__)
app.secret_key = "supersecretkey"

# ---------- DATABASE SETUP ----------
def get_db():
    conn = sqlite3.connect("users.db")
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

# ---------- STYLE ----------
base_style = """
<style>
body {
    font-family: Arial, sans-serif;
    background: #90EE90;
    display: flex;
    justify-content: center;
    align-items: center;
    height: 100vh;
}
.card {
    background: white;
    padding: 25px;
    border-radius: 10px;
    box-shadow: 0 4px 10px rgba(0,0,0,0.1);
    width: 300px;
    text-align: center;
}
input {
    width: 90%;
    padding: 8px;
    margin: 8px 0;
}
button {
    padding: 10px;
    width: 60%;
    background: #4CAF50;
    color: white;
    border: none;
}
.error {
    color: red;
}
</style>
"""

login_page = f"""{base_style}
<div class="card">
<h2>Login</h2>
<form method="POST">
  <input name="username" placeholder="Username"><br>
  <input name="password" type="password" placeholder="Password"><br>
  <button type="submit">Login</button>
</form>
<a href="/register">Create an account</a>
<p class="error">{{{{ error }}}}</p>
</div>
"""

register_page = f"""{base_style}
<div class="card">
<h2>Register</h2>
<form method="POST">
  <input name="username" placeholder="Username"><br>
  <input name="password" type="password" placeholder="Password"><br>
  <select name="gender" required>
    <option value="male">Male</option>
    <option value="female">Female</option>
    <option value="other">Other</option>
    <option value="prefer_not_to_say">Prefer not to say</option>
  <select name="diet" required>
    <option value="all_foods">All foods</option>
    <option value="vegan">Vegan</option>
    <option value="vegetarian">Vegetarian</option>
    <option value="other">Other</option>
    <form action="/submit-allergies" method="post">
  <p>Select all that apply:</p>
  <div>
    <input type="checkbox" id="peanut" name="allergies[]" value="peanut">
    <label for="peanut">Peanuts</label>
  </div>
  <div>
    <input type="checkbox" id="dairy" name="allergies[]" value="dairy">
    <label for="dairy">Dairy</label>
  </div>
  <div>
    <input type="checkbox" id="gluten" name="allergies[]" value="gluten">
    <label for="gluten">Gluten</label>
  </div>
</form>
</select><br>
  <input name="weight" type="number" step="0.1" placeholder="Weight (kg/lbs)" required><br>
  <input name="height" type="number" step="0.1" placeholder="Height (cm/in)" required><br>
  <button type="submit">Sign Up</button>
</form>
<a href="/">Back to login</a>
<p class="error">{{{{ error }}}}</p>
</div>
"""

secret_page = f"""{base_style}
<div class="card">
<h2>Nutriplanr </h2>
<h3>Welcome, {{{{ username }}}}!</h3>
<p>Lets get fit!</p>
<a href="/logout"><button>Logout</button></a>
</div>
"""

# ---------- ROUTES ----------
@app.route("/", methods=["GET", "POST"])
def login():
    error = ""
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = get_db()
        user = conn.execute(
            "SELECT * FROM users WHERE username=? AND password=?",
            (username, password)
        ).fetchone()
        conn.close()

        if user:
            session["user"] = username
            return redirect(url_for("secret"))
        else:
            error = "Incorrect username or password"

    return render_template_string(login_page, error=error)

@app.route("/register", methods=["GET", "POST"])
def register():
    error = ""
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if not username or not password:
            error = "Fields cannot be empty"
        else:
            try:
                conn = get_db()
                hashed_pw = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
                conn.execute(
                    "INSERT INTO users (username, password) VALUES (?, ?)",
                    (username, hashed_pw)
                )
                conn.commit()
                conn.close()
                return redirect(url_for("login"))
            except sqlite3.IntegrityError:
                error = "Username already exists"
            except Exception as e:  # Optional: Catch other potential errors, like hashing failures
                error = f"An error occurred: {str(e)}"

    return render_template_string(register_page, error=error)


@app.route("/secret")
def secret():
    if "user" not in session:
        return redirect(url_for("login"))
    return render_template_string(secret_page, username=session["user"])

@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("login"))

# ---------- RUN ----------
app.run(host="0.0.0.0", port=5000)