import os
import json
import datetime
import gspread
from google.oauth2.service_account import Credentials
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

# --- Configuración ---
BOT_TOKEN = os.getenv("BOT_TOKEN")
SHEET_ID = os.getenv("SHEET_ID")
GOOGLE_CREDENTIALS = os.getenv("GOOGLE_CREDENTIALS")  # JSON completo como string

# --- Cliente Google Sheets ---
creds_info = json.loads(GOOGLE_CREDENTIALS)
scopes = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]
creds = Credentials.from_service_account_info(creds_info, scopes=scopes)
gc = gspread.authorize(creds)
sheet = gc.open_by_key(SHEET_ID).sheet1  # primera pestaña

# --- Handlers ---
def start(update, context):
    update.message.reply_text("¡Hola! Estoy vivo en Render 🤖")
    now = datetime.datetime.utcnow().isoformat()
    user = update.effective_user
    sheet.append_row([now, user.id, user.username or "", "/start"])

def echo(update, context):
    text = update.message.text
    now = datetime.datetime.utcnow().isoformat()
    user = update.effective_user
    sheet.append_row([now, user.id, user.username or "", text])
    update.message.reply_text("¡Guardado en Google Sheets! 🗂️")

# --- Función principal ---
def main():
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))

    print("✅ Bot corriendo en Render Free (long polling)…")
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
