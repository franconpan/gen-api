from fastapi import FastAPI, Request, Form, UploadFile, File
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import sqlite3, os

app = FastAPI()

PASSWORD = "Exshop12_"
DB_PATH = "stock.db"

# ===============================
# BASE DE DATOS
# ===============================
def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS stock (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cuenta TEXT NOT NULL
            )
        """)
init_db()

# ===============================
# PÁGINA PRINCIPAL
# ===============================
@app.get("/", response_class=HTMLResponse)
async def home():
    return """
    <html>
    <head><title>Gen API</title></head>
    <body style="font-family: sans-serif; text-align: center; margin-top: 80px;">
        <h1>API activa</h1>
        <p>q miras pillin.</p>
    </body>
    </html>
    """

# ===============================
# PANEL DE ADMINISTRACIÓN
# ===============================
@app.get("/panel", response_class=HTMLResponse)
async def panel():
    return """
    <html>
    <head><title>stock panel</title></head>
    <body style="font-family: sans-serif; text-align: center; margin-top: 50px;">
        <h2>🌐 Subir stock desde web</h2>
        <form action="/upload_stock" method="post" enctype="multipart/form-data">
            <input type="password" name="password" placeholder="pass" required><br><br>
            <input type="file" name="file" accept=".txt" required><br><br>
            <button type="submit">subir stock</button>
        </form>
    </body>
    </html>
    """

# ===============================
# subir stock
# ===============================
@app.post("/upload_stock", response_class=HTMLResponse)
async def upload_stock(password: str = Form(...), file: UploadFile = File(...)):
    if password != PASSWORD:
        return HTMLResponse("<h3>no</h3>", status_code=403)

    content = (await file.read()).decode("utf-8")
    lines = [l.strip() for l in content.splitlines() if l.strip()]

    # Guardar en la base de datos
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("DELETE FROM stock")
        for cuenta in lines:
            conn.execute("INSERT INTO stock (cuenta) VALUES (?)", (cuenta,))
        conn.commit()

    return HTMLResponse(f"<h3>has subido {len(lines)} cuentas.</h3>")

# ===============================
# stock dispo
# ===============================
@app.get("/stock")
async def get_stock():
    with sqlite3.connect(DB_PATH) as conn:
        count = conn.execute("SELECT COUNT(*) FROM stock").fetchone()[0]
    return {"count": count}

# ===============================
# gen acc para el bot
# ===============================
@app.post("/gen")
async def gen_account():
    with sqlite3.connect(DB_PATH) as conn:
        row = conn.execute("SELECT id, cuenta FROM stock ORDER BY id LIMIT 1").fetchone()

        if not row:
            return JSONResponse({"success": False, "message": "No stock available"})

        account_id, account = row
        conn.execute("DELETE FROM stock WHERE id = ?", (account_id,))
        conn.commit()

        remaining = conn.execute("SELECT COUNT(*) FROM stock").fetchone()[0]

    return JSONResponse({
        "success": True,
        "account": account,
        "remaining": remaining,
        "message": "OK"
    })
