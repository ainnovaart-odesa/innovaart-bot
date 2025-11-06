from flask import Flask
import threading
import os
import telebot
from telebot import types

TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = -1003295755890

bot = telebot.TeleBot(TOKEN)


# --- Кнопки ---
def main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton("➕ Створити направлення"))
    markup.add(types.KeyboardButton("📘 Інструкція"), types.KeyboardButton("❌ Скасувати"))
    return markup


# --- Команда /start ---
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Вітаю! Оберіть дію:", reply_markup=main_menu())


# --- Скасування ---
@bot.message_handler(func=lambda message: message.text == "❌ Скасувати")
def cancel(message):
    bot.clear_step_handler(message)  # ← зупиняє опитування
    bot.send_message(message.chat.id, "✅ Опитування зупинено.", reply_markup=main_menu())


# --- Створити направлення ---
@bot.message_handler(func=lambda message: message.text == "➕ Створити направлення")
def new(message):
    msg = bot.send_message(message.chat.id, "Введіть ім'я пацієнта:", reply_markup=main_menu())
    bot.register_next_step_handler(msg, process_patient)


def process_patient(message):
    if message.text == "❌ Скасувати": return cancel(message)
    patient = message.text
    msg = bot.send_message(message.chat.id, "Введіть телефон пацієнта:")
    bot.register_next_step_handler(msg, process_phone, patient)


def process_phone(message, patient):
    if message.text == "❌ Скасувати": return cancel(message)
    phone = message.text
    msg = bot.send_message(message.chat.id, "Введіть діагноз:")
    bot.register_next_step_handler(msg, process_diagnosis, patient, phone)


def process_diagnosis(message, patient, phone):
    if message.text == "❌ Скасувати": return cancel(message)
    diagnosis = message.text
    msg = bot.send_message(message.chat.id, "Введіть ім'я лікаря:")
    bot.register_next_step_handler(msg, process_doctor, patient, phone, diagnosis)


def process_doctor(message, patient, phone, diagnosis):
    if message.text == "❌ Скасувати": return cancel(message)
    doctor = message.text
    msg = bot.send_message(message.chat.id, "Введіть контакт лікаря:")
    bot.register_next_step_handler(msg, send_to_group, patient, phone, diagnosis, doctor)


def send_to_group(message, patient, phone, diagnosis, doctor):
    if message.text == "❌ Скасувати": return cancel(message)
    doctor_phone = message.text

    text = (
        f"🔔 *Нове направлення*\n\n"
        f"👤 Пацієнт: {patient}\n"
        f"📞 Телефон: {phone}\n"
        f"🩺 Діагноз: {diagnosis}\n"
        f"👨‍⚕️ Лікар: {doctor}\n"
        f"📳 Контакт лікаря: {doctor_phone}"
    )
    bot.send_message(CHAT_ID, text, parse_mode='Markdown')
    bot.send_message(message.chat.id, "✅ Направлення надіслано.", reply_markup=main_menu())


# --- Інструкція ---
@bot.message_handler(func=lambda message: message.text == "📘 Інструкція")
def instructions(message):
    text = (
        "📘 *Як працювати з ботом:*\n\n"
        "1) Натисніть «Створити направлення»\n"
        "2) Введіть дані пацієнта крок за кроком\n"
        "3) Бот сам надішле направлення у групу\n\n"
        "❌ Якщо потрібно зупинити — натисніть «Скасувати»."
    )
    bot.send_message(message.chat.id, text, parse_mode="Markdown", reply_markup=main_menu())


# --- Запуск веб-сервера ---
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

def run_web():
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)


threading.Thread(target=run_web).start()
bot.polling(none_stop=True)


