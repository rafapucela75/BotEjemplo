import os
import json
import datetime
import gspread
from google.oauth2.service_account import Credentials
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

# --- Variables de entorno ---
BOT_TOKEN = os.getenv("BOT_TOKEN")
SHEET_ID = os.getenv("SHEET_ID")
GOOGLE_CREDENTIALS = os.getenv("GOOGLE_CREDENTIALS")

# --- Validación de entorno ---
if not GOOGLE_CREDENTIALS:
    raise ValueError("GOOGLE_CREDENTIALS environment variable is required")
if not SHEET_ID:
    raise ValueError("SHEET_ID environment variable is required")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN environment variable is required")

# --- Procesamiento de credenciales ---
try:
    credentials_str = GOOGLE_CREDENTIALS.strip()

    if not credentials_str.startswith('{'):
        raise ValueError(f"GOOGLE_CREDENTIALS must be a JSON object starting with '{{', but got: {credentials_str[:50]}...")

    if credentials_str.startswith('"') and credentials_str.endswith('"') and credentials_str.count('"') > 2:
        credentials_str = credentials_str[1:-1]

    credentials_str = credentials_str.replace('\\"', '"')
    creds_info = json.loads(credentials_str)

    required_fields = ['type', 'project_id', 'private_key_id', 'private_key', 'client_email']
    for field in required_fields:
        if field not in creds_info:
            raise ValueError(f"Missing required field '{field}' in Google credentials")

except json.JSONDecodeError as e:
    print(f"DEBUG: GOOGLE_CREDENTIALS content (first 100 chars): {GOOGLE_CREDENTIALS[:100]}")
    raise ValueError(f"Invalid JSON in GOOGLE_CREDENTIALS: {e}. Please check that your credentials are a valid JSON object.")

# --- Conexión a Google Sheets ---
scopes = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]
creds = Credentials.from_service_account_info(creds_info, scopes=scopes)
gc = gspread.authorize(creds)
sheet = gc.open_by_key(SHEET_ID).worksheet("CHAT")  # hoja llamada "CHAT"

# --- Handlers ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("¡Hola! Estoy vivo en Replit 🤖")
    now = datetime.datetime.utcnow().isoformat()
    user = update.effective_user

    user_id = str(user.id)
    username = user.username if user.username and user.username.strip() else "Sin Identificar"
    first = user.first_name or ""
    last = user.last_name or ""
    full_name = f"{first} {last}".strip() or "Sin Identificar"
    message = "/start"

    row = [now, user_id, username, full_name, message]
    sheet.append_row(row)

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    now = datetime.datetime.utcnow().isoformat()
    user = update.effective_user

    user_id = str(user.id)
    username = user.username if user.username and user.username.strip() else "Sin Identificar"
    first = user.first_name or ""
    last = user.last_name or ""
    full_name = f"{first} {last}".strip() or "Sin Identificar"
    message = text

    row = [now, user_id, username, full_name, message]
    sheet.append_row(row)

    await update.message.reply_text("¡Guardado en Google Sheets! 🗂️")

async def ayuda(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📚 *Comandos disponibles:*\n"
        "/start – Inicia el bot\n"
        "/ayuda – Muestra esta ayuda\n"
        "Escribe cualquier mensaje y lo guardaré en Google Sheets 🗂️",
        parse_mode="Markdown"
    )

# --- Función principal ---
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("ayuda", ayuda))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    print("✅ Bot corriendo en Replit (long polling)…")
    app.run_polling()

if __name__ == "__main__":
    main()
