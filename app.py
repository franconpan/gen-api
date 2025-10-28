from fastapi import FastAPI, Request, Form, UploadFile, File
from fastapi.responses import HTMLResponse, JSONResponse
import os

app = FastAPI()

PASSWORD = "admin123"
STOCK_FILE = "stock.txt"

# ===============================
# PÁGINA PRINCIPAL
# ===============================
@app.get("/", response_class=HTMLResponse)
async def home():
    return """
    <html>
    <head><title>Gen API</title></head>
    <body style="font-family: sans-serif; text-align: center; margin-top: 80px;">
        <h1>🚀 API de generación activa</h1>
        <p>Usa /panel para gestionar el stock.</p>
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
    <head><title>Panel de Stock</title></head>
    <body style="font-family: sans-serif; text-align: center; margin-top: 50px;">
        <h2>🌐 Subir stock desde web</h2>
        <form action="/upload_stock" method="post" enctype="multipart/form-data">
            <input type="password" name="password" placeholder="Contraseña" required><br><br>
            <input type="file" name="file" accept=".txt" required><br><br>
            <button type="submit">📤 Subir Stock</button>
        </form>
    </body>
    </html>
    """

# ===============================
# SUBIR STOCK
# ===============================
@app.post("/upload_stock", response_class=HTMLResponse)
async def upload_stock(password: str = Form(...), file: UploadFile = File(...)):
    if password != PASSWORD:
        return HTMLResponse("<h3>❌ Contraseña incorrecta</h3>", status_code=403)

    content = await file.read()
    with open(STOCK_FILE, "wb") as f:
        f.write(content)

    # Contar cuántas líneas hay
    lines = [l for l in content.decode("utf-8").splitlines() if l.strip()]
    return HTMLResponse(f"<h3>✅ Stock actualizado con {len(lines)} cuentas.</h3>")

# ===============================
# VER STOCK DISPONIBLE
# ===============================
@app.get("/stock")
async def get_stock():
    if not os.path.exists(STOCK_FILE):
        return {"count": 0}

    with open(STOCK_FILE, "r", encoding="utf-8") as f:
        lines = [l.strip() for l in f if l.strip()]

    return {"count": len(lines)}

# ===============================
# GENERAR CUENTA (PARA EL BOT)
# ===============================
@app.post("/gen")
async def gen_account():
    if not os.path.exists(STOCK_FILE):
        return JSONResponse({"success": False, "message": "Stock file not found"})

    with open(STOCK_FILE, "r", encoding="utf-8") as f:
        lines = [l.strip() for l in f if l.strip()]

    if not lines:
        return JSONResponse({"success": False, "message": "No stock available"})

    account = lines.pop(0)

    with open(STOCK_FILE, "w", encoding="utf-8") as f:
        for l in lines:
            f.write(l + "\n")

    return JSONResponse({
        "success": True,
        "account": account,
        "remaining": len(lines),
        "message": "OK"
    })
