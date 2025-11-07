from flask import Flask
import threading
import os
import telebot
from telebot import types
import re

TOKEN = os.getenv("BOT_TOKEN")  # токен з Environment
CHAT_ID = -1003295755890  # ID групи

bot = telebot.TeleBot(TOKEN)
user_data = {}  # пам'ять для кожного користувача

# ============================
# Меню та посилання
# ============================
def main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("➕ Створити направлення")
    markup.add("📘 Інструкція", "❌ Скасувати")
    markup.add("🌐 Сайт", "💰 Прайс", "📸 Instagram")
    return markup

# ============================
# Перевірка на скасування
# ============================
def check_cancel (message) :
    if message.text == "❌ Скасувати":
        user_data.pop(message.from_user.id, None)
        bot.send_message(message.chat.id, "✅ Опитування скасовано.", reply_markup=main_menu())
        return True
    return False

# ============================
# Екраніруємо спецсимволи MarkdownV2
# ============================
def escape_md(text):
    return re.sub(r'([_*\[\]()~`>#+\-=|{}.!])', r'\\\1', text)

# ============================
# Flask для Render
# ============================
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

def run_web():
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

threading.Thread(target=run_web).start()

# ============================
# Хендлери основних команд
# ============================
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Вітаю! Оберіть дію:", reply_markup=main_menu())

@bot.message_handler(func=lambda message: message.text == "📘 Інструкція")
def instructions(message):
    bot.send_message(
        message.chat.id,
        "📘 *Як працювати з ботом:*\n\n"
        "1) Натисніть *'Створити направлення'*\n"
        "2) Введіть дані пацієнта\n"
        "3) Підтвердіть відправку\n\n"
        "❌ Якщо щось пішло не так, натисніть 'Скасувати'.",
        parse_mode="Markdown",
        reply_markup=main_menu()
    )

@bot.message_handler(func=lambda message: message.text == "🌐 Сайт")
def site(message):
    bot.send_message(message.chat.id, "Перейдіть на сайт: https://www.innovaart.com.ua/", reply_markup=main_menu())

@bot.message_handler(func=lambda message: message.text == "💰 Прайс")
def price(message):
    bot.send_message(message.chat.id, "Прайс: https://www.innovaart.com.ua/price_ukr/", reply_markup=main_menu())

@bot.message_handler(func=lambda message: message.text == "📸 Instagram")
def instagram(message):
    bot.send_message(message.chat.id, "Instagram: https://www.instagram.com/innovaart.od?igsh=OHh4YmVzc3lyc20y", reply_markup=main_menu())

# ============================
# Створення нового направлення
# ============================
@bot.message_handler(func=lambda message: message.text == "➕ Створити направлення")
def new(message):
    msg = bot.reply_to(message, "Введіть ім'я пацієнта:")
    bot.register_next_step_handler(msg, process_patient)

def process_patient(message):
    if check_cancel(message): return
    user_data[message.from_user.id] = {"patient": message.text}
    msg = bot.reply_to(message, "Введіть телефон пацієнта:")
    bot.register_next_step_handler(msg, process_phone)

def process_phone(message):
    if check_cancel(message): return
    user_data[message.from_user.id]["phone"] = message.text
    msg = bot.reply_to(message, "Введіть діагноз:")
    bot.register_next_step_handler(msg, process_diagnosis)

def process_diagnosis(message):
    if check_cancel(message): return
    user_data[message.from_user.id]["diagnosis"] = message.text
    msg = bot.reply_to(message, "Введіть ім'я лікаря:")
    bot.register_next_step_handler(msg, process_doctor)

def process_doctor(message):
    if check_cancel(message): return
    user_data[message.from_user.id]["doctor"] = message.text
    msg = bot.reply_to(message, "Введіть контакт лікаря:")
    bot.register_next_step_handler(msg, send_to_group)

def send_to_group (message) :
    if check_cancel(message): return
    user_data[message.from_user.id]["doctor_phone"] = message.text
    data = user_data[message.from_user.id]

    text = (
        f"🔔 *Нове направлення*\n\n"
        f"👤 Пацієнт: {escape_md(data['patient'])}\n"
        f"📞 Телефон: {escape_md(data['phone'])}\n"
        f"🩺 Діагноз: {escape_md(data['diagnosis'])}\n"
        f"👨‍⚕️ Лікар: {escape_md(data['doctor'])}\n"
        f"📳 Контакт лікаря: {escape_md(data['doctor_phone'])}"
    )

    bot.send_message(CHAT_ID, text, parse_mode='MarkdownV2')
    bot.send_message(message.chat.id, "✅ Направлення надіслано у групу.", reply_markup=main_menu())

    user_data.pop(message.from_user.id, None)  # очищаємо дані користувача

# ============================
# Старт polling
# ============================
bot.infinity_polling()







