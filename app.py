from fastapi import FastAPI, Form, UploadFile, File
from fastapi.responses import HTMLResponse, JSONResponse
import os
import requests

app = FastAPI()

PASSWORD = "Exshop12_"
STOCK_FILE = "stock.txt"

# ⚙️ CONFIGURA TUS DATOS DE PASTEBIN
PASTEBIN_RAW_URL = "https://pastebin.com/raw/J0d6VmvF"
PASTEBIN_API_KEY = "MfVd26Py5Tjx5n-DUIHoaYIgXOCKVLw-"
PASTEBIN_USER_KEY = "b305f2ac691288145a1781a7562535dd"
PASTEBIN_PASTE_KEY = "J0d6VmvF"

# ===============================
# 🔁 FUNCIONES PASTEBIN
# ===============================
def load_stock_from_pastebin():
    """Descarga el stock del Pastebin y lo guarda localmente."""
    try:
        r = requests.get(PASTEBIN_RAW_URL, timeout=10)
        if r.status_code == 200:
            data = r.text.strip()
            with open(STOCK_FILE, "w", encoding="utf-8") as f:
                f.write(data)
            print("✅ Stock restaurado desde Pastebin.")
            return data.splitlines()
        else:
            print("⚠️ Error al restaurar stock:", r.status_code)
            return []
    except Exception as e:
        print("⚠️ Error al conectar con Pastebin:", e)
        return []

def update_pastebin():
    """Sube el stock actualizado al Pastebin."""
    try:
        with open(STOCK_FILE, "r", encoding="utf-8") as f:
            data = f.read().strip()

        payload = {
            "api_dev_key": PASTEBIN_API_KEY,
            "api_user_key": PASTEBIN_USER_KEY,
            "api_option": "paste",  # ✅ se crea una nueva versión pública
            "api_paste_private": "0",  # público
            "api_paste_name": "Stock actualizado",
            "api_paste_code": data
        }

        r = requests.post("https://pastebin.com/api/api_post.php", data=payload, timeout=10)
        if r.status_code == 200 and "Bad API request" not in r.text:
            print("✅ Stock actualizado en Pastebin.")
        else:
            print("⚠️ Error al actualizar Pastebin:", r.text)
    except Exception as e:
        print("⚠️ Error al sincronizar con Pastebin:", e)

# ===============================
# 🔰 INICIO
# ===============================
@app.on_event("startup")
def startup_event():
    """Al iniciar Render, descarga el stock actual del Pastebin."""
    load_stock_from_pastebin()

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

@app.post("/upload_stock", response_class=HTMLResponse)
async def upload_stock(password: str = Form(...), file: UploadFile = File(...)):
    if password != PASSWORD:
        return HTMLResponse("<h3>❌ Contraseña incorrecta</h3>", status_code=403)

    content = await file.read()
    decoded = content.decode("utf-8").strip()

    with open(STOCK_FILE, "w", encoding="utf-8") as f:
        f.write(decoded)

    update_pastebin()
    count = len([l for l in decoded.splitlines() if l.strip()])
    return HTMLResponse(f"<h3>✅ Has subido {count} cuentas nuevas.</h3>")

# ===============================
# 📦 ENDPOINT /stock
# ===============================
@app.get("/stock")
async def get_stock():
    if not os.path.exists(STOCK_FILE):
        lines = load_stock_from_pastebin()
    else:
        with open(STOCK_FILE, "r", encoding="utf-8") as f:
            lines = [l.strip() for l in f if l.strip()]

    return {"count": len(lines)}

# ===============================
# 🎁 ENDPOINT /gen
# ===============================
@app.post("/gen")
async def gen():
    lines = []

    if os.path.exists(STOCK_FILE):
        with open(STOCK_FILE, "r", encoding="utf-8") as f:
            lines = [l.strip() for l in f if l.strip()]

    if not lines:
        # Si el stock local está vacío, intenta restaurarlo del Pastebin
        lines = load_stock_from_pastebin()
        if not lines:
            return JSONResponse({"error": "No hay stock disponible."}, status_code=400)

    cuenta = lines.pop(0)

    with open(STOCK_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    # Actualiza Pastebin con el nuevo stock
    update_pastebin()

    return {"account": cuenta}
