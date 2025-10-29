from fastapi import FastAPI, Form, UploadFile, File
from fastapi.responses import HTMLResponse, JSONResponse
import os
import requests

app = FastAPI()

PASSWORD = "Exshop12_"
STOCK_FILE = "stock.txt"

# 🧠 Configura estos valores
PASTEBIN_RAW_URL = "https://pastebin.com/raw/XXXXXXXX"  # tu paste actual
PASTEBIN_API_KEY = "MfVd26Py5Tjx5n-DUIHoaYIgXOCKVLw-"
PASTEBIN_USER_KEY = "TU_USER_KEY_DE_PASTEBIN"  # opcional si usas cuenta

# ===============================
# FUNCIÓN: Descargar stock si falta
# ===============================
def load_stock_from_pastebin():
    if not os.path.exists(STOCK_FILE):
        try:
            r = requests.get(PASTEBIN_RAW_URL, timeout=10)
            if r.status_code == 200:
                with open(STOCK_FILE, "w", encoding="utf-8") as f:
                    f.write(r.text)
                print("✅ Stock restaurado desde Pastebin.")
            else:
                print("⚠️ Error al restaurar stock:", r.status_code)
        except Exception as e:
            print("⚠️ Error al conectar con Pastebin:", e)

# ===============================
# FUNCIÓN: Subir stock actualizado a Pastebin
# ===============================
def update_pastebin():
    try:
        with open(STOCK_FILE, "r", encoding="utf-8") as f:
            data = f.read()

        payload = {
            "api_dev_key": PASTEBIN_API_KEY,
            "api_option": "paste",
            "api_paste_code": data,
            "api_paste_private": "1",  # 0=public, 1=unlisted, 2=private
            "api_paste_name": "gen_stock",
            "api_paste_expire_date": "N",
        }

        r = requests.post("https://pastebin.com/api/api_post.php", data=payload, timeout=10)
        if r.status_code == 200:
            print("✅ Stock sincronizado con Pastebin:", r.text)
        else:
            print("⚠️ Error al subir stock:", r.status_code)
    except Exception as e:
        print("⚠️ Error al actualizar Pastebin:", e)

# Cargar stock al iniciar
load_stock_from_pastebin()

# ===============================
# PANEL / subir stock
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

@app.post("/upload_stock", response_class=HTMLResponse)
async def upload_stock(password: str = Form(...), file: UploadFile = File(...)):
    if password != PASSWORD:
        return HTMLResponse("<h3>no</h3>", status_code=403)

    content = await file.read()
    with open(STOCK_FILE, "wb") as f:
        f.write(content)

    lines = [l for l in content.decode("utf-8").splitlines() if l.strip()]
    update_pastebin()  # sincroniza Pastebin
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

    update_pastebin()  # ✅ sincroniza cada vez que alguien genera

    return JSONResponse({
        "success": True,
        "account": account,
        "remaining": len(lines),
        "message": "OK"
    })
