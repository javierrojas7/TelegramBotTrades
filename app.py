import telebot
from pyfiglet import Figlet
from flask import Flask,render_template
import threading
import asciistarwars
from randomUrl import obtener_url_aleatoria

app = Flask(__name__)

bot = telebot.TeleBot("7495043047:AAG9eZnni5Plh9d9xii8lb-gPutb3EX0L-M", parse_mode=None)

f = Figlet(font='slant')
print(f.renderText('TelegramBot'))

# Variables globales para almacenar el estado de la conversación
user_data = {}

# Función para calcular el take profit y stop loss
def calculate_trade(btc_price, amount_in_usd, profit_target=100, stop_loss_amount=50, trade_type="long"):
    btc_acquired = amount_in_usd / btc_price
    
    if trade_type.lower() == "long":
        sell_price_for_profit = (amount_in_usd + profit_target) / btc_acquired
        sell_price_for_loss = (amount_in_usd - stop_loss_amount) / btc_acquired
    elif trade_type.lower() == "short":
        sell_price_for_profit = (amount_in_usd - profit_target) / btc_acquired
        sell_price_for_loss = (amount_in_usd + stop_loss_amount) / btc_acquired

    return sell_price_for_profit, sell_price_for_loss

# Función para manejar la conversión de divisas
def convert_currency(amount, rate):
    return amount * rate

# Comando /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.chat.id
    user_data[user_id] = {'command': 'start'}  # Inicializa los datos del usuario
    bot.reply_to(message, "¡Bienvenido! ¿Con cuántos dólares deseas hacer el trade?")

# Comando /transform
@bot.message_handler(commands=['transform'])
def convert_currency_command(message):
    user_id = message.chat.id
    user_data[user_id] = {'command': 'transform'}  # Inicializa los datos del usuario
    bot.reply_to(message, "¿Cuánto tienes de la divisa inicial?")
    
# Inicial-Función para manejar la cantidad en dólares o la conversión de divisas
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_id = message.chat.id

    # Verifica cuál comando fue utilizado
    command = user_data.get(user_id, {}).get('command')

    if command == 'start':
        handle_amount(message)
    elif command == 'transform':
        handle_currency_conversion(message, user_id)
        
def handle_amount(message):
    user_id = message.chat.id

    # Si aún no se ha ingresado el monto en USD
    if 'amount_in_usd' not in user_data[user_id]:
        try:
            # Guardar la cantidad en USD ingresada por el usuario
            user_data[user_id]['amount_in_usd'] = float(message.text)
            bot.reply_to(message, "Por favor, ingresa el precio actual del activo:")
        except ValueError:
            bot.reply_to(message, "Por favor, ingresa un número válido.")
    
    # Si se ha ingresado el monto en USD, preguntar el precio de BTC
    elif 'btc_price' not in user_data[user_id]:
        try:
            # Guardar el precio de BTC ingresado por el usuario
            user_data[user_id]['btc_price'] = float(message.text)
            bot.reply_to(message, "¿Quieres hacer un trade 'long' o 'short'?")
        except ValueError:
            bot.reply_to(message, "Por favor, ingresa un número válido para el precio del activo.")
    
    # Si se ha ingresado el monto en USD y el precio de BTC, preguntar el tipo de trade
    elif 'trade_type' not in user_data[user_id]:
        trade_type = message.text.lower()
        if trade_type in ["long", "short"]:
            user_data[user_id]['trade_type'] = trade_type
            bot.reply_to(message, "¿Cuántos decimales deseas utilizar para los resultados?")
        else:
            bot.reply_to(message, "Por favor, ingresa 'long' o 'short' para el tipo de trade.")
    
    # Si se ha ingresado el tipo de trade, preguntar por los decimales
    elif 'decimals' not in user_data[user_id]:
        try:
            # Guardar la cantidad de decimales
            user_data[user_id]['decimals'] = int(message.text)
            bot.reply_to(message, "Por favor, ingresa el par de trading (por ejemplo, BTC/USD):")
        except ValueError:
            bot.reply_to(message, "Por favor, ingresa un número válido para los decimales.")
    
    # Si se ha ingresado la cantidad de decimales, preguntar por el par de trading
    elif 'trading_pair' not in user_data[user_id]:
        trading_pair = message.text.upper()
        user_data[user_id]['trading_pair'] = trading_pair

        # Obtener los valores ingresados
        amount_in_usd = user_data[user_id]['amount_in_usd']
        btc_price = user_data[user_id]['btc_price']
        trade_type = user_data[user_id]['trade_type']
        decimals = user_data[user_id]['decimals']
        
        # Calcular take profit y stop loss
        take_profit, stop_loss = calculate_trade(btc_price, amount_in_usd, trade_type=trade_type)
        
        # Formatear el mensaje
        formatted_message = f"""\n 
                        ⠀⠀⠀⠀⣿⡇⠀⢸⣿⡇⠀⠀⠀⠀
                        ⠸⠿⣿⣿⣿⡿⠿⠿⣿⣿⣿⣶⣄⠀
                        ⠀⠀⢸⣿⣿⡇⠀⠀⠀⠈⣿⣿⣿⠀
                        ⠀⠀⢸⣿⣿⡇⠀⠀⢀⣠⣿⣿⠟⠀
                        ⠀⠀⢸⣿⣿⡿⠿⠿⠿⣿⣿⣥⣄⠀
                        ⠀⠀⢸⣿⣿⡇⠀⠀⠀⠀⢻⣿⣿⣧
                        ⠀⠀⢸⣿⣿⡇⠀⠀⠀⠀⣼⣿⣿⣿
                        ⢰⣶⣿⣿⣿⣷⣶⣶⣾⣿⣿⠿⠛⠁
                        ⠀⠀⠀⠀⣿⡇⠀⢸⣿⡇⠀
        \n    
        {'🟩 Long' if trade_type == 'long' else '🟥 Short'}
        {trading_pair}
        Price                      {btc_price:.{decimals}f}
        Stoploss(50usdt)           {stop_loss:.{decimals}f}
        Take Profit(100usdt)       {take_profit:.{decimals}f}
        """
        print(formatted_message)
        bot.reply_to(message, formatted_message)
        try:
            inurl = obtener_url_aleatoria()
            bot.send_animation(message.chat.id, inurl)
        except Exception as e:
            print(f"Error al enviar el GIF: {e}")

# Función para manejar la conversión de divisas
def handle_currency_conversion(message, user_id):
    if 'amount_in_currency' not in user_data[user_id]:
        try:
            amount_in_currency = float(message.text)
            user_data[user_id]['amount_in_currency'] = amount_in_currency
            bot.reply_to(message, "Por favor, ingresa el tipo de cambio actual para la conversión:")
        except ValueError:
            bot.reply_to(message, "Por favor, ingresa un número válido.")
    elif 'exchange_rate' not in user_data[user_id]:
        try:
            exchange_rate = float(message.text)
            amount_in_currency = user_data[user_id]['amount_in_currency']
            converted_amount = convert_currency(amount_in_currency, exchange_rate)
            bot.reply_to(message, f"Con una tasa de cambio de {exchange_rate}, tienes un total de {converted_amount:.2f} en la divisa objetivo.")
            user_data[user_id] = {}  # Limpiar los datos del usuario después de procesar
        except ValueError:
            bot.reply_to(message, "Por favor, ingresa un número válido para el tipo de cambio.")


@app.route('/')
def index():
    formatted_message = f"""{asciistarwars.rnd_character()}"""
    print(formatted_message)
    return render_template("index.html")

# Función para ejecutar el bot de Telegram
def run_telegram_bot():
    bot.infinity_polling()

# Función para ejecutar la aplicación Flask
def run_flask_app():
    app.run(host="0.0.0.0", port=5000)

if __name__ == "__main__":
    print("Bot iniciado")
    
    # Crear un hilo para el bot de Telegram
    telegram_thread = threading.Thread(target=run_telegram_bot)
    
    # Iniciar el hilo del bot de Telegram
    telegram_thread.start()
    
    # Ejecutar la aplicación Flask
    run_flask_app()