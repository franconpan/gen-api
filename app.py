from fastapi import FastAPI, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os

app = FastAPI()

# Permitir peticiones desde cualquier origen (para el bot)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

STOCK_FILE = "stock.txt"

# -------------------------------
# 📦 Obtener stock actual
# -------------------------------
@app.get("/stock")
async def get_stock():
    if not os.path.exists(STOCK_FILE):
        return {"count": 0}

    with open(STOCK_FILE, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip()]

    return {"count": len(lines)}

# -------------------------------
# 🧩 Generar cuenta (eliminar 1 del stock)
# -------------------------------
@app.post("/gen")
async def generate_account():
    if not os.path.exists(STOCK_FILE):
        return JSONResponse(content={"success": False, "message": "No hay archivo de stock."})

    with open(STOCK_FILE, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip()]

    if not lines:
        return JSONResponse(content={"success": False, "message": "No hay stock disponible."})

    account = lines.pop(0)  # primera cuenta

    with open(STOCK_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    return JSONResponse(content={
        "success": True,
        "account": account,
        "remaining": len(lines),
        "message": "OK"
    })

# -------------------------------
# 🧠 Subir stock manualmente desde formulario
# -------------------------------
@app.post("/upload")
async def upload_stock(content: str = Form(...)):
    lines = [line.strip() for line in content.splitlines() if line.strip()]
    with open(STOCK_FILE, "a", encoding="utf-8") as f:
        for line in lines:
            f.write(line + "\n")
    return {"message": f"{len(lines)} cuentas añadidas correctamente"}

# -------------------------------
# 🌐 Página simple
# -------------------------------
@app.get("/")
async def home():
    return """
    <h2>🚀 Panel de generación activo</h2>
    <p>Endpoints:</p>
    <ul>
        <li><b>GET /stock</b> → muestra cuántas cuentas hay</li>
        <li><b>POST /gen</b> → genera una cuenta</li>
        <li><b>POST /upload</b> (campo "content") → añade cuentas</li>
    </ul>
    """

