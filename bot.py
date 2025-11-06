from flask import Flask
import threading
import os
import telebot

TOKEN = os.getenv("BOT_TOKEN")  # токен беремо з Environment (не з коду)
CHAT_ID = -1003295755890  # ID вашої групи

bot = telebot.TeleBot(TOKEN)
from telebot import types

# Головне меню
def main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("➕ Створити направлення")
    btn2 = types.KeyboardButton("📘 Інструкція")
    btn3 = types.KeyboardButton("❌ Скасувати")
    markup.add(btn1)
    markup.add(btn2, btn3)
    return markup
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Вітаю! Оберіть дію:", reply_markup=main_menu())
    
# --- Додаємо мінівебсервер ---
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

def run_web():
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

@bot.message_handler(func=lambda message: message.text == "➕ Створити направлення")
def new(message):
    msg = bot.reply_to(message, "Введіть ім'я пацієнта:")
    bot.register_next_step_handler(msg, process_patient)

def process_patient(message):
    patient = message.text
    msg = bot.reply_to(message, "Введіть телефон пацієнта:")
    bot.register_next_step_handler(msg, process_phone, patient)

def process_phone(message, patient):
    phone = message.text
    msg = bot.reply_to(message, "Введіть діагноз:")
    bot.register_next_step_handler(msg, process_diagnosis, patient, phone)

def process_diagnosis(message, patient, phone):
    diagnosis = message.text
    msg = bot.reply_to(message, "Введіть ім'я лікаря:")
    bot.register_next_step_handler(msg, process_doctor, patient, phone, diagnosis)

def process_doctor(message, patient, phone, diagnosis):
    doctor = message.text
    msg = bot.reply_to(message, "Введіть контакт лікаря:")
    bot.register_next_step_handler(msg, send_to_group, patient, phone, diagnosis, doctor)
@bot.message_handler(commands=['скасувати'])
@bot.message_handler(func=lambda message: message.text == "❌ Скасувати")
def cancel(message):
    bot.send_message(message.chat.id, "Операцію скасовано ✅", reply_markup=main_menu())
def send_to_group(message, patient, phone, diagnosis, doctor):
    doctor_phone = message.text
    text = f"🔔 *Нове направлення*\n\n👤 Пацієнт: {patient}\n📞 Телефон: {phone}\n🩺 Діагноз: {diagnosis}\n👨‍⚕️ Лікар: {doctor}\n📳 Контакт лікаря: {doctor_phone}"
    bot.send_message(CHAT_ID, text, parse_mode='Markdown')
    bot.reply_to(message, "✅ Направлення надіслано у групу.")
@bot.message_handler(commands=['інструкція'])
@bot.message_handler(func=lambda message: message.text == "📘 Інструкція")
def instructions(message):
    text = (
        "📘 *Як працювати з ботом:*\n\n"
        "1) Натисніть *'Створити направлення'*\n"
        "2) Введіть дані пацієнта\n"
        "3) Підтвердіть відправку\n\n"
        "❌ Якщо щось пішло не так, натисніть 'Скасувати'."
    )
    bot.send_message(message.chat.id, text, parse_mode="Markdown", reply_markup=main_menu())

threading.Thread(target=run_web).start()
bot.polling(none_stop=True)




