import os, json, datetime
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
import gspread
from google.oauth2.service_account import Credentials
from flask import Flask
from threading import Thread

# --- Variables de entorno ---
BOT_TOKEN = os.getenv("BOT_TOKEN")
SHEET_ID = os.getenv("SHEET_ID")
GOOGLE_CREDENTIALS = os.getenv("GOOGLE_CREDENTIALS")

# --- Conexión Google Sheets ---
creds_info = json.loads(GOOGLE_CREDENTIALS)
scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
creds = Credentials.from_service_account_info(creds_info, scopes=scopes)
gc = gspread.authorize(creds)
# sheet = gc.open_by_key(SHEET_ID).sheet1
sheet = gc.open_by_key(SHEET_ID).worksheet("CHAT")

# --- Handlers ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("¡Hola! Estoy vivo 🤖")
    now = datetime.datetime.utcnow().isoformat()
    user = update.effective_user
    sheet.append_row([now, user.id, user.username or "", "/start"])

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    now = datetime.datetime.utcnow().isoformat()
    user = update.effective_user
    sheet.append_row([now, user.id, user.username or "", text])
    await update.message.reply_text("¡Guardado en Google Sheets! 🗂️")

# --- Bot ---
def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
    print("✅ Bot corriendo en long polling…")
    app.run_polling()

# --- Servidor Flask para mantener vivo el bot ---
app_server = Flask("")

@app_server.route("/")
def home():
    return "El bot está vivo ✅"

def run():
    app_server.run(host="0.0.0.0", port=8080)

Thread(target=run).start()

# --- Lanzar bot ---
if __name__ == "__main__":
    main()

