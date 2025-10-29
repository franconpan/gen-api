from fastapi import FastAPI, Form, UploadFile, File
from fastapi.responses import HTMLResponse, JSONResponse
import os
import requests

app = FastAPI()

# ===============================
# ⚙️ CONFIGURACIÓN
# ===============================
PASSWORD = "Exshop12_"
STOCK_FILE = "stock.txt"

# 🔗 Configura tus valores de Pastebin
PASTEBIN_RAW_URL = "https://pastebin.com/raw/J0d6VmvF"
PASTEBIN_API_KEY = "MfVd26Py5Tjx5n-DUIHoaYIgXOCKVLw-"
PASTEBIN_USER_KEY = "b305f2ac691288145a1781a7562535dd"
PASTEBIN_PASTE_KEY = "J0d6VmvF"

# ===============================
# 🔁 FUNCIONES DE SINCRONIZACIÓN
# ===============================
def load_stock_from_pastebin():
    """Descarga el stock desde Pastebin y lo guarda localmente"""
    try:
        r = requests.get(PASTEBIN_RAW_URL, timeout=10)
        if r.status_code == 200:
            with open(STOCK_FILE, "w", encoding="utf-8") as f:
                f.write(r.text)
            print(f"✅ Stock restaurado desde Pastebin ({len(r.text.splitlines())} cuentas).")
        else:
            print("⚠️ Error al restaurar stock:", r.status_code)
    except Exception as e:
        print("⚠️ Error al conectar con Pastebin:", e)


def update_pastebin():
    """Actualiza el contenido del paste con el stock local"""
    try:
        with open(STOCK_FILE, "r", encoding="utf-8") as f:
            data = f.read()

        payload = {
            "api_dev_key": PASTEBIN_API_KEY,
            "api_user_key": PASTEBIN_USER_KEY,
            "api_option": "edit",
            "api_paste_key": PASTEBIN_PASTE_KEY,
            "api_paste_code": data
        }

        r = requests.post("https://pastebin.com/api/api_post.php", data=payload, timeout=10)
        if r.status_code == 200 and "Bad API request" not in r.text:
            print("✅ Stock actualizado correctamente en Pastebin.")
        else:
            print("⚠️ Error al actualizar Pastebin:", r.text)
    except Exception as e:
        print("⚠️ Error al sincronizar con Pastebin:", e)

# ===============================
# 🚀 SINCRONIZACIÓN INICIAL
# ===============================
# 🔄 Siempre sincroniza desde Pastebin al iniciar
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
            <button type="submit">📤 Subir stock</button>
        </form>
    </body>
    </html>
    """

@app.post("/upload_stock", response_class=HTMLResponse)
async def upload_stock(password: str = Form(...), file: UploadFile = File(...)):
    if password != PASSWORD:
        return HTMLResponse("<h3>❌ Contraseña incorrecta</h3>", status_code=403)

    content = await file.read()
    with open(STOCK_FILE, "wb") as f:
        f.write(content)

    lines = [l for l in content.decode("utf-8").splitlines() if l.strip()]
    update_pastebin()  # 🔄 sincroniza automáticamente

    return HTMLResponse(f"<h3>✅ Has subido {len(lines)} cuentas nuevas.</h3>")

# ===============================
# 📦 STOCK DISPONIBLE
# ===============================
@app.get("/stock")
async def get_stock():
    if not os.path.exists(STOCK_FILE):
        return {"count": 0}

    with open(STOCK_FILE, "r", encoding="utf-8") as f:
        lines = [l.strip() for l in f if l.strip()]

    return {"count": len(lines)}

# ===============================
# 🎁 GENERAR CUENTA (para el bot)
# ===============================
@app.post("/gen")
async def gen():
    if not os.path.exists(STOCK_FILE):
        return JSONResponse({"error": "No hay stock disponible."}, status_code=400)

    with open(STOCK_FILE, "r", encoding="utf-8") as f:
        lines = [l.strip() for l in f if l.strip()]

    if not lines:
        return JSONResponse({"error": "Stock vacío."}, status_code=400)

    cuenta = lines.pop(0)

    # Reescribe el archivo sin la cuenta usada
    with open(STOCK_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    # 🔄 Actualiza Pastebin
    update_pastebin()

    return {"account": cuenta}
