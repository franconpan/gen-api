from fastapi import FastAPI, Form, UploadFile, File
from fastapi.responses import HTMLResponse, JSONResponse
import os
import requests

app = FastAPI()

PASSWORD = "Exshop12_"
STOCK_FILE = "stock.txt"

# 🔗 Configura tus valores de Pastebin
PASTEBIN_RAW_URL = "https://pastebin.com/raw/J0d6VmvF"
PASTEBIN_API_KEY = "MfVd26Py5Tjx5n-DUIHoaYIgXOCKVLw-"
PASTEBIN_USER_KEY = "b305f2ac691288145a1781a7562535dd"
PASTEBIN_PASTE_KEY = "J0d6VmvF"


# ===============================
# 🧠 FUNCIONES DE SINCRONIZACIÓN
# ===============================
def get_stock_from_pastebin():
    """Obtiene el stock directamente desde Pastebin"""
    try:
        r = requests.get(PASTEBIN_RAW_URL, timeout=10)
        if r.status_code == 200:
            lines = [l.strip() for l in r.text.splitlines() if l.strip()]
            return lines
        else:
            print("⚠️ Error al leer Pastebin:", r.status_code)
            return []
    except Exception as e:
        print("⚠️ Error al conectar con Pastebin:", e)
        return []


def update_pastebin(new_lines):
    """Actualiza el Pastebin con una nueva lista de líneas"""
    try:
        data = "\n".join(new_lines)
        payload = {
            "api_dev_key": PASTEBIN_API_KEY,
            "api_user_key": PASTEBIN_USER_KEY,
            "api_option": "edit",
            "api_paste_key": PASTEBIN_PASTE_KEY,
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
    lines = [l.strip() for l in content.decode("utf-8").splitlines() if l.strip()]

    # Guardar local (opcional)
    with open(STOCK_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    # Actualizar Pastebin
    update_pastebin(lines)
    return HTMLResponse(f"<h3>✅ Has subido {len(lines)} cuentas nuevas.</h3>")


# ===============================
# 📦 STOCK DISPONIBLE
# ===============================
@app.get("/stock")
async def get_stock():
    lines = get_stock_from_pastebin()
    return {"count": len(lines)}


# ===============================
# 🎁 GENERAR CUENTA (para el bot)
# ===============================
@app.post("/gen")
async def gen():
    lines = get_stock_from_pastebin()

    if not lines:
        return JSONResponse({"error": "No hay stock disponible."}, status_code=400)

    cuenta = lines.pop(0)  # Quita la primera cuenta del stock

    # Actualiza Pastebin con el resto
    update_pastebin(lines)

    return {"account": cuenta}
