from fastapi import FastAPI, Request, Form, UploadFile, File
from fastapi.responses import HTMLResponse, JSONResponse
import os

app = FastAPI()

PASSWORD = "Exshop12_"
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

    content = await file.read()
    with open(STOCK_FILE, "wb") as f:
        f.write(content)

    # Contar cuántas líneas hay
    lines = [l for l in content.decode("utf-8").splitlines() if l.strip()]
    return HTMLResponse(f"<h3>has subido {len(lines)} cuentas.</h3>")

# ===============================
# stock dispo
# ===============================
@app.get("/stock")
async def get_stock():
    if not os.path.exists(STOCK_FILE):
        return {"count": 0}

    with open(STOCK_FILE, "r", encoding="utf-8") as f:
        lines = [l.strip() for l in f if l.strip()]

    return {"count": len(lines)}

# ===============================
# gen acc para el bot
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

