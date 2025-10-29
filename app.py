from fastapi import FastAPI, Form, UploadFile, File
from fastapi.responses import HTMLResponse, JSONResponse
import os
import requests

app = FastAPI()

# 🔧 CONFIGURACIÓN
PASSWORD = "Exshop12_"
STOCK_FILE = "stock.txt"

# ⚙️ Datos Pastebin (paste privado)
PASTEBIN_RAW_URL = "https://pastebin.com/raw/J0d6VmvF"
PASTEBIN_API_KEY = "MfVd26Py5Tjx5n-DUIHoaYIgXOCKVLw-"
PASTEBIN_USER_KEY = "84b24637a39a3153b785c8a6250ee4d7"
PASTEBIN_PASTE_KEY = "J0d6VmvF"  # ID del paste privado

# ===============================
# 🔁 FUNCIONES PASTEBIN
# ===============================
def load_stock_from_pastebin():
    """Descarga stock del Pastebin y guarda localmente si no existe stock.txt."""
    try:
        r = requests.get(PASTEBIN_RAW_URL, timeout=10)
        if r.status_code == 200:
            data = r.text.strip()
            if not os.path.exists(STOCK_FILE) or os.path.getsize(STOCK_FILE) == 0:
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
    """Actualiza el contenido del paste existente (reemplazo funcional de 'edit')."""
    try:
        if not os.path.exists(STOCK_FILE):
            return
        with open(STOCK_FILE, "r", encoding="utf-8") as f:
            data = f.read().strip()

        payload = {
            "api_dev_key": PASTEBIN_API_KEY,
            "api_user_key": PASTEBIN_USER_KEY,
            "api_option": "paste",
            "api_paste_private": "1",  # 0 = público, 1 = unlisted, 2 = privado
            "api_paste_name": "Stock actualizado",
            "api_paste_code": data
        }

        # Creamos un nuevo paste y actualizamos el ID global si cambia
        r = requests.post("https://pastebin.com/api/api_post.php", data=payload, timeout=10)
        if r.status_code == 200 and "Bad API request" not in r.text:
            new_url = r.text.strip()
            print(f"✅ Stock actualizado en Pastebin: {new_url}")
        else:
            print("⚠️ Error al actualizar Pastebin:", r.text)
    except Exception as e:
        print("⚠️ Error al sincronizar con Pastebin:", e)

# ===============================
# 🔰 INICIO
# ===============================
@app.on_event("startup")
def startup_event():
    """Al iniciar Render, descarga el stock si no existe local."""
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
    new_lines = [l.strip() for l in content.decode("utf-8").splitlines() if l.strip()]

    # Leer stock existente y combinar
    existing_lines = []
    if os.path.exists(STOCK_FILE):
        with open(STOCK_FILE, "r", encoding="utf-8") as f:
            existing_lines = [l.strip() for l in f if l.strip()]

    combined_lines = existing_lines + new_lines

    with open(STOCK_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(combined_lines))

    # Actualiza Pastebin
    update_pastebin()
    return HTMLResponse(f"<h3>✅ Añadidas {len(new_lines)} cuentas. Stock total: {len(combined_lines)}</h3>")

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
        # Restaurar stock desde Pastebin si se vació
        lines = load_stock_from_pastebin()
        if not lines:
            return JSONResponse({"error": "No hay stock disponible."}, status_code=400)

    cuenta = lines.pop(0)

    with open(STOCK_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    # Actualiza Pastebin
    update_pastebin()
    return {"account": cuenta}


