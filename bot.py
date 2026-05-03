import os
import telebot
import requests
from dotenv import load_dotenv
from telebot import types

load_dotenv()
bot_TOKEN = os.environ.get("BOT_TOKEN")
if not bot_TOKEN:
    raise ValueError("BOT_TOKEN not found!")

bot = telebot.TeleBot(bot_TOKEN)

# Map Open-Meteo codes to human-readable text
WMO_CODES = {
    0: "Clear sky ☀️", 1: "Mainly clear 🌤", 2: "Partly cloudy ⛅", 3: "Overcast ☁️",
    45: "Fog 🌫️", 48: "Depositing rime fog 🌫️",
    51: "Light drizzle 🌧️", 53: "Moderate drizzle 🌧️", 55: "Dense drizzle 🌧️",
    61: "Slight rain 🌦️", 63: "Moderate rain 🌧️", 65: "Heavy rain ⛈️",
    71: "Slight snow ❄️", 73: "Moderate snow ❄️", 75: "Heavy snow ❄️",
    95: "Thunderstorm 🌩️"
}

def get_weather(lat, lon, location_name="your location"):
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,weather_code"
    response = requests.get(url).json()
    
    temp = response['current']['temperature_2m']
    code = response['current']['weather_code']
    condition = WMO_CODES.get(code, "Unknown")
    
    return f"📍 Weather in {location_name}:\n🌡️ Temp: {temp}°C\n☁️ Condition: {condition}"

# --- HANDLERS ---

@bot.message_handler(commands=['weather'])
def ask_location(message):
    # Check if user provided a city name: /weather London
    args = message.text.split(maxsplit=1)
    
    if len(args) > 1:
        city = args[1]
        # Use Open-Meteo Geocoding API to find lat/lon of the city
        geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1"
        geo_res = requests.get(geo_url).json()
        
        if 'results' in geo_res:
            res = geo_res['results'][0]
            weather_text = get_weather(res['latitude'], res['longitude'], res['name'])
            bot.reply_to(message, weather_text)
        else:
            bot.reply_to(message, "❌ City not found.")
    else:
        # No city provided, ask for GPS location via button
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        button = types.KeyboardButton("Share my location 📍", request_location=True)
        markup.add(button)
        bot.send_message(message.chat.id, "Please share your location or type '/weather CityName'", reply_markup=markup)

@bot.message_handler(content_types=['location'])
def handle_location(message):
    lat = message.location.latitude
    lon = message.location.longitude
    weather_text = get_weather(lat, lon)
    bot.reply_to(message, weather_text, reply_markup=types.ReplyKeyboardRemove())

print("Bot is running...")
bot.infinity_polling()