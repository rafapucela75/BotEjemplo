import os, json, datetime
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
import gspread
from google.oauth2.service_account import Credentials

# --- Tokens y credenciales ---
BOT_TOKEN = os.getenv("BOT_TOKEN")
SHEET_ID = os.getenv("SHEET_ID")
GOOGLE_CREDENTIALS = os.getenv("GOOGLE_CREDENTIALS")  # JSON completo como string

# --- Cliente de Google Sheets ---
creds_info = json.loads(GOOGLE_CREDENTIALS)
scopes = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]
creds = Credentials.from_service_account_info(creds_info, scopes=scopes)
gc = gspread.authorize(creds)
sheet = gc.open_by_key(SHEET_ID).sheet1  # primera pestaña de la hoja

# --- Handlers del bot ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /start"""
    await update.message.reply_text("¡Hola! Estoy vivo en Render 🤖")
    now = datetime.datetime.utcnow().isoformat()
    user = update.effective_user
    sheet.append_row([now, user.id, user.username or "", "/start"])

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Responde a cualquier texto y lo guarda en Sheets"""
    text = update.message.text
    now = datetime.datetime.utcnow().isoformat()
    user = update.effective_user
    sheet.append_row([now, user.id, user.username or "", text])
    await update.message.reply_text("¡Guardado en Google Sheets! 🗂️")

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    print("✅ Bot corriendo en Render (long polling)…")
    app.run_polling()

if __name__ == "__main__":
    main()
