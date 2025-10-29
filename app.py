from fastapi import FastAPI, Form, UploadFile, File
from fastapi.responses import HTMLResponse, JSONResponse
import os

app = FastAPI()

PASSWORD = "Exshop12_"  # 🔒 Contraseña del panel
STOCK_FILE = "stock.txt"  # 📦 Archivo donde se guarda el stock

# ===============================
# 🌐 PANEL WEB
# ===============================
@app.get("/panel", response_class=HTMLResponse)
async def panel():
    return """
    <html>
    <head><title>Stock Panel</title></head>
    <body style="font-family: sans-serif; text-align: center; margin-top: 50px;">
        <h2>🌐 Subir stock desde web</h2>
        <form action="/upload_stock" method="post" enctype="multipart/form-data">
            <input type="password" name="password" placeholder="Contraseña" required><br><br>
            <input type="file" name="file" accept=".txt" required><br><br>
            <button type="submit">Subir stock</button>
        </form>
    </body>
    </html>
    """

# ===============================
# 📤 SUBIR STOCK
# ===============================
@app.post("/upload_stock", response_class=HTMLResponse)
async def upload_stock(password: str = Form(...), file: UploadFile = File(...)):
    if password != PASSWORD:
        return HTMLResponse("<h3>❌ Contraseña incorrecta</h3>", status_code=403)

    # Lee el nuevo stock
    content = await file.read()
    new_lines = [l.strip() for l in content.decode("utf-8").splitlines() if l.strip()]

    # Carga el stock actual si existe
    existing_lines = []
    if os.path.exists(STOCK_FILE):
        with open(STOCK_FILE, "r", encoding="utf-8") as f:
            existing_lines = [l.strip() for l in f if l.strip()]

    # Añade las nuevas líneas
    combined_lines = existing_lines + new_lines

    with open(STOCK_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(combined_lines))

    return HTMLResponse(f"<h3>✅ Añadidas {len(new_lines)} cuentas.<br>Stock total: {len(combined_lines)}</h3>")

# ===============================
# 📦 ENDPOINT /stock
# ===============================
@app.get("/stock")
async def get_stock():
    if not os.path.exists(STOCK_FILE):
        return {"count": 0}

    with open(STOCK_FILE, "r", encoding="utf-8") as f:
        lines = [l.strip() for l in f if l.strip()]

    return {"count": len(lines)}

# ===============================
# 🎁 ENDPOINT /gen
# ===============================
@app.post("/gen")
async def gen():
    if not os.path.exists(STOCK_FILE):
        return JSONResponse({"error": "No hay stock disponible."}, status_code=400)

    with open(STOCK_FILE, "r", encoding="utf-8") as f:
        lines = [l.strip() for l in f if l.strip()]

    if not lines:
        return JSONResponse({"error": "No hay stock disponible."}, status_code=400)

    cuenta = lines.pop(0)  # Toma la primera cuenta

    # Guarda el resto del stock
    with open(STOCK_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    return {"account": cuenta}
