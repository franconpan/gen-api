from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import os, json

app = FastAPI()

# Permitir CORS para que el bot o panel web accedan sin problema
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

STOCK_FILE = "stock.txt"
PASSWORD = "admin123"  # 🔐 contraseña del panel


# ===========================
# Página principal
# ===========================
@app.get("/", response_class=HTMLResponse)
async def home():
    return """
    <h2>✅ API Online</h2>
    <p>Endpoints disponibles:</p>
    <ul>
      <li><b>GET</b> /stock → Ver cantidad disponible</li>
      <li><b>POST</b> /gen → Generar una cuenta</li>
      <li><b>GET</b> /panel → Subir stock (requiere contraseña)</li>
    </ul>
    """


# ===========================
# Obtener stock
# ===========================
@app.get("/stock")
async def get_stock():
    if not os.path.exists(STOCK_FILE):
        return {"count": 0}

    with open(STOCK_FILE, "r", encoding="utf-8") as f:
        lines = [x.strip() for x in f if x.strip()]

    return {"count": len(lines)}


# ===========================
# Generar cuenta
# ===========================
@app.post("/gen")
async def gen():
    if not os.path.exists(STOCK_FILE):
        return {"success": False, "message": "No hay stock disponible."}

    with open(STOCK_FILE, "r", encoding="utf-8") as f:
        lines = [x.strip() for x in f if x.strip()]

    if not lines:
        return {"success": False, "message": "No hay stock disponible."}

    cuenta = lines.pop(0)

    with open(STOCK_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"✅ GEN: {cuenta} | Restante: {len(lines)}")

    return {
        "success": True,
        "account": cuenta,
        "remaining": len(lines),
        "message": "OK"
    }


# ===========================
# Panel web para subir stock
# ===========================
@app.get("/panel", response_class=HTMLResponse)
async def panel_form():
    return """
    <h2>🌐 Subir stock</h2>
    <form action="/upload_stock" method="post">
      <label>Contraseña:</label><br>
      <input type="password" name="password" /><br><br>
      <label>Lista (una cuenta por línea):</label><br>
      <textarea name="stock" rows="10" cols="50"></textarea><br><br>
      <button type="submit">Subir</button>
    </form>
    """


# ===========================
# Subir stock (POST)
# ===========================
@app.post("/upload_stock")
async def upload_stock(password: str = Form(...), stock: str = Form(...)):
    if password != PASSWORD:
        return HTMLResponse("<h3>❌ Contraseña incorrecta</h3>")

    stock = stock.strip().splitlines()
    stock = [x.strip() for x in stock if x.strip()]

    with open(STOCK_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(stock))

    print(f"✅ STOCK actualizado: {len(stock)} cuentas")

    return HTMLResponse(f"<h3>✅ Stock actualizado correctamente ({len(stock)} cuentas)</h3>")


# ===========================
# Run local (opcional)
# ===========================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=10000)
