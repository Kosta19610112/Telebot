import os
import telebot
import requests
from datetime import datetime, timedelta
import pytz
from dotenv import load_dotenv
from flask import Flask, request

# Загружаем переменные окружения
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENWEATHER_API_KEY = '1f30db42752361354d4cf1f02835861e'

WEBHOOK_URL = os.getenv("https://telebot-gpg6.onrender.com")  # например, https://yourappname.onrender.com


bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

# ========== ТВОИ ФУНКЦИИ ==========

def get_weather(city):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={OPENWEATHER_API_KEY}&units=metric"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data['main']['temp']
    return None

def get_forecast(city):
    url = f"http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={OPENWEATHER_API_KEY}&units=metric"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        tomorrow = datetime.now() + timedelta(days=1)
        target_time = tomorrow.replace(hour=datetime.now().hour, minute=0, second=0, microsecond=0)
        for forecast in data['list']:
            forecast_time = datetime.strptime(forecast['dt_txt'], '%Y-%m-%d %H:%M:%S')
            if forecast_time.date() == target_time.date() and forecast_time.hour == target_time.hour:
                return forecast['main']['temp']
    return None

def get_local_time(city_timezone):
    timezone = pytz.timezone(city_timezone)
    return datetime.now(timezone).strftime('%Y-%m-%d %H:%M:%S')

# ========== ХЕНДЛЕРЫ ==========

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Привет! Я могу показать текущее время, температуру и прогноз погоды в разных городах. Напишите /w.")

@bot.message_handler(commands=['w'])
def weather(message):
    current_time_moscow = get_local_time('Europe/Moscow')
    current_time_riga = get_local_time('Europe/Riga')

    moscow_temp = get_weather('Moscow')
    moscow_weather = f"Температура в Москве: {moscow_temp}°C" if moscow_temp is not None else "Не удалось получить данные о погоде в Москве."

    riga_temp = get_weather('Riga')
    riga_weather = f"Температура в Риге: {riga_temp}°C" if riga_temp is not None else "Не удалось получить данные о погоде в Риге."

    sevastopol_temp = get_weather('Sevastopol')
    sevastopol_weather = f"Температура в Севастополе: {sevastopol_temp}°C" if sevastopol_temp is not None else "Не удалось получить данные о погоде в Севастополе."

    moscow_forecast = get_forecast('Moscow')
    moscow_forecast_weather = f"Прогноз на завтра в Москве: {moscow_forecast}°C" if moscow_forecast is not None else "Не удалось получить прогноз погоды на завтра в Москве."

    riga_forecast = get_forecast('Riga')
    riga_forecast_weather = f"Прогноз на завтра в Риге: {riga_forecast}°C" if riga_forecast is not None else "Не удалось получить прогноз погоды на завтра в Риге."

    response = (
        f"Текущее время:\n"
        f"  - Москва: {current_time_moscow}\n"
        f"  - Рига: {current_time_riga}\n\n"
        f"{moscow_weather}\n"
        f"{riga_weather}\n"
        f"{sevastopol_weather}\n\n"
        f"{moscow_forecast_weather}\n"
        f"{riga_forecast_weather}"
    )
    bot.send_message(message.chat.id, response)

# ========== WEBHOOK ОБРАБОТКА ==========

@app.route('/', methods=['POST'])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        json_str = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_str)
        bot.process_new_updates([update])
        return 'OK', 200
    else:
        return 'Unsupported Media Type', 415

@app.before_first_request
def setup_webhook():
    bot.remove_webhook()
    bot.set_webhook(url=WEBHOOK_URL)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
