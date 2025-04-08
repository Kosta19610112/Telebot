import os
import telebot
import requests
from datetime import datetime, timedelta
import pytz
from dotenv import load_dotenv

# Токен вашего Telegram-бота


#PORT = int(os.getenv('PORT', 8080))

# API ключ OpenWeatherMap
OPENWEATHER_API_KEY = '1f30db42752361354d4cf1f02835861e'

# Создаем экземпляр бота
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)

# Функция для получения текущей погоды
def get_weather(city):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={OPENWEATHER_API_KEY}&units=metric"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        temperature = data['main']['temp']
        return temperature
    else:
        return None

# Функция для получения прогноза погоды на завтра
def get_forecast(city):
    url = f"http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={OPENWEATHER_API_KEY}&units=metric"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        # Находим прогноз на завтра в это же время
        tomorrow = datetime.now() + timedelta(days=1)
        target_time = tomorrow.replace(hour=datetime.now().hour, minute=0, second=0, microsecond=0)
        for forecast in data['list']:
            forecast_time = datetime.strptime(forecast['dt_txt'], '%Y-%m-%d %H:%M:%S')
            if forecast_time.date() == target_time.date() and forecast_time.hour == target_time.hour:
                return forecast['main']['temp']
        return None
    else:
        return None

# Функция для получения времени в определенном часовом поясе
def get_local_time(city_timezone):
    timezone = pytz.timezone(city_timezone)
    local_time = datetime.now(timezone).strftime('%Y-%m-%d %H:%M:%S')
    return local_time

# Обработчик команды /start
@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Привет! Я могу показать текущее время, температуру и прогноз погоды в разных городах. Напишите /w.")

# Обработчик команды /w
@bot.message_handler(commands=['w'])
def weather(message):
    # Текущее время (Московское время)
    current_time_moscow = get_local_time('Europe/Moscow')

    # Рижское время
    current_time_riga = get_local_time('Europe/Riga')

    # Получаем температуру в Москве
    moscow_temp = get_weather('Moscow')
    if moscow_temp is not None:
        moscow_weather = f"Температура в Москве: {moscow_temp}°C"
    else:
        moscow_weather = "Не удалось получить данные о погоде в Москве."

    # Получаем температуру в Риге
    riga_temp = get_weather('Riga')
    if riga_temp is not None:
        riga_weather = f"Температура в Риге: {riga_temp}°C"
    else:
        riga_weather = "Не удалось получить данные о погоде в Риге."

    # Получаем температуру в Севастополе
    sevastopol_temp = get_weather('Sevastopol')
    if sevastopol_temp is not None:
        sevastopol_weather = f"Температура в Севастополе: {sevastopol_temp}°C"
    else:
        sevastopol_weather = "Не удалось получить данные о погоде в Севастополе."

    # Прогноз погоды на завтра в Москве
    moscow_forecast = get_forecast('Moscow')
    if moscow_forecast is not None:
        moscow_forecast_weather = f"Прогноз на завтра в Москве: {moscow_forecast}°C"
    else:
        moscow_forecast_weather = "Не удалось получить прогноз погоды на завтра в Москве."

    # Прогноз погоды на завтра в Риге
    riga_forecast = get_forecast('Riga')
    if riga_forecast is not None:
        riga_forecast_weather = f"Прогноз на завтра в Риге: {riga_forecast}°C"
    else:
        riga_forecast_weather = "Не удалось получить прогноз погоды на завтра в Риге."

    # Отправляем сообщение с временем и погодой
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

# Запускаем бота
if __name__ == "__main__":
    bot.polling()