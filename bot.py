import os
import telebot

TOKEN = os.getenv("BOT_TOKEN")  # токен беремо з Environment (не з коду)
CHAT_ID = -1003295755890  # ID вашої групи

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Вітаю! Для створення направлення натисніть /new")

@bot.message_handler(commands=['new'])
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

def send_to_group(message, patient, phone, diagnosis, doctor):
    doctor_phone = message.text
    text = f"🔔 *Нове направлення*\n\n👤 Пацієнт: {patient}\n📞 Телефон: {phone}\n🩺 Діагноз: {diagnosis}\n👨‍⚕️ Лікар: {doctor}\n📳 Контакт лікаря: {doctor_phone}"
    bot.send_message(CHAT_ID, text, parse_mode='Markdown')
    bot.reply_to(message, "✅ Направлення надіслано у групу.")

bot.infinity_polling()