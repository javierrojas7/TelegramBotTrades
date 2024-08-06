import telebot
from pyfiglet import Figlet

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

# Comando /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.chat.id
    user_data[user_id] = {}  # Inicializa los datos del usuario
    bot.reply_to(message, "¡Bienvenido! ¿Con cuántos dólares deseas hacer el trade?")

# Función para manejar la cantidad en dólares
@bot.message_handler(func=lambda message: True)
def handle_amount(message):
    user_id = message.chat.id

    # Si aún no se ha ingresado el monto en USD
    if 'amount_in_usd' not in user_data[user_id]:
        try:
            # Guardar la cantidad en USD ingresada por el usuario
            user_data[user_id]['amount_in_usd'] = float(message.text)
            bot.reply_to(message, "Por favor, ingresa el precio actual del BTC en USD:")
        except ValueError:
            bot.reply_to(message, "Por favor, ingresa un número válido.")
    
    # Si se ha ingresado el monto en USD, preguntar el precio de BTC
    elif 'btc_price' not in user_data[user_id]:
        try:
            # Guardar el precio de BTC ingresado por el usuario
            user_data[user_id]['btc_price'] = float(message.text)
            bot.reply_to(message, "¿Quieres hacer un trade 'long' o 'short'?")
        except ValueError:
            bot.reply_to(message, "Por favor, ingresa un número válido para el precio del BTC.")
    
    # Si se ha ingresado el monto en USD y el precio de BTC, preguntar el tipo de trade
    elif 'trade_type' not in user_data[user_id]:
        trade_type = message.text.lower()
        if trade_type in ["long", "short"]:
            user_data[user_id]['trade_type'] = trade_type
            
            # Obtener los valores ingresados
            amount_in_usd = user_data[user_id]['amount_in_usd']
            btc_price = user_data[user_id]['btc_price']
            
            # Calcular take profit y stop loss
            take_profit, stop_loss = calculate_trade(btc_price, amount_in_usd, trade_type=trade_type)
            
            # Formatear el mensaje
            formatted_message = f"""
            {'🟩 Long' if trade_type == 'long' else '🟥 Short'}
            BTC/USD
            Price                      {btc_price:.2f}
            Stoploss(50usdt)           {stop_loss:.2f}
            Take Profit(100usdt)       {take_profit:.2f}
            """
            print("trade:",formatted_message)
            bot.reply_to(message, formatted_message)
        else:
            bot.reply_to(message, "Por favor, ingresa 'long' o 'short' para el tipo de trade.")

if __name__ == "__main__":
    print("Bot iniciado")
    bot.infinity_polling()