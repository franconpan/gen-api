from fastapi import FastAPI, UploadFile, Form
from fastapi.responses import HTMLResponse, JSONResponse
import os

app = FastAPI()

STOCK_FILE = "stock.txt"
PASSWORD = "admin123"  # 🔒 cámbiala a algo más seguro


@app.get("/")
def home():
    return {"message": "API de generación funcionando 🚀"}


@app.get("/gen")
def gen():
    if not os.path.exists(STOCK_FILE):
        return JSONResponse({"success": False, "message": "No hay stock disponible"})

    with open(STOCK_FILE, "r", encoding="utf-8") as f:
        lines = [l.strip() for l in f if l.strip()]

    if not lines:
        return JSONResponse({"success": False, "message": "Sin stock"})

    account = lines.pop(0)

    with open(STOCK_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    return JSONResponse({
        "success": True,
        "account": account,
        "remaining": len(lines),
        "message": "OK"
    })


@app.get("/stock")
def stock():
    if not os.path.exists(STOCK_FILE):
        return {"count": 0}

    with open(STOCK_FILE, "r", encoding="utf-8") as f:
        lines = [l.strip() for l in f if l.strip()]

    return {"count": len(lines)}


# 🌐 Panel web para subir stock
@app.get("/panel", response_class=HTMLResponse)
def panel():
    html = """
    <html>
        <head>
            <title>Panel de Stock</title>
            <style>
                body { font-family: Arial; margin: 40px; background-color: #111; color: #eee; }
                input, button { padding: 8px; margin-top: 10px; }
                .card { background: #222; padding: 20px; border-radius: 10px; width: 300px; }
            </style>
        </head>
        <body>
            <div class="card">
                <h2>📦 Panel de Stock</h2>
                <form action="/upload_stock" method="post" enctype="multipart/form-data">
                    <label>Contraseña:</label><br>
                    <input type="password" name="password" /><br>
                    <label>Archivo stock.txt:</label><br>
                    <input type="file" name="file" accept=".txt"/><br>
                    <button type="submit">Subir Stock</button>
                </form>
            </div>
        </body>
    </html>
    """
    return HTMLResponse(html)


@app.post("/upload_stock")
async def upload_stock(file: UploadFile, password: str = Form(...)):
    if password != PASSWORD:
        return HTMLResponse("<h2>❌ Contraseña incorrecta</h2>", status_code=403)

    content = await file.read()
    with open(STOCK_FILE, "wb") as f:
        f.write(content)

    return HTMLResponse("<h2>✅ Stock actualizado correctamente</h2>")
