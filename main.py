# main.py
import telebot
from telebot import types
import config
from pocketoptionapi.stable_api import PocketOption

# Инициализируем Telegram-бота
bot = telebot.TeleBot(config.TELEGRAM_TOKEN)

# Подключаемся к платформе Pocket Option напрямую через API
print("[Система] Авторизация в Pocket Option...")
api = PocketOption(config.PO_EMAIL, config.PO_PASSWORD)
is_connected, message = api.connect()

if is_connected:
    # Устанавливаем тип счета из настроек (демо или реал)
    account_mode = "PRACTICE" if config.BALANCE_TYPE == "demo" else "REAL"
    api.change_balance(account_mode)
    print(f"[Система] Успешно подключено! Режим: {config.BALANCE_TYPE.upper()}")
else:
    print(f"[Ошибка] Не удалось войти на платформу: {message}")

@bot.message_handler(commands=['start'])
def send_welcome(message):
    # Проверка владельца бота
    if message.chat.id != config.MY_CHAT_ID:
        bot.reply_to(message, "Доступ к торговому пульту ограничен.")
        return

    # Создаем удобные кнопки пульта в Telegram
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn_up = types.KeyboardButton("🟢 ОТКРЫТЬ ВВЕРХ (CALL)")
    btn_down = types.KeyboardButton("🔴 ОТКРЫТЬ ВНИЗ (PUT)")
    markup.add(btn_up, btn_down)

    bot.send_message(
        message.chat.id, 
        f"🎮 Пульт управления Pocket Option готов!\n"
        f"Актив: BTCUSDT\n"
        f"Сумма: ${config.TRADE_AMOUNT} | Время: {config.EXPIRATION_TIME} сек.\n"
        f"Баланс: {config.BALANCE_TYPE.upper()}", 
        reply_markup=markup
    )

@bot.message_handler(func=lambda message: True)
def handle_trade_buttons(message):
    if message.chat.id != config.MY_CHAT_ID:
        return

    if not api.check_connect():
        bot.send_message(message.chat.id, "⚠️ Соединение потеряно! Переподключаюсь...")
        api.connect()
        return

    # Обработка кнопки ВВЕРХ
    if message.text == "🟢 ОТКРЫТЬ ВВЕРХ (CALL)":
        bot.send_message(message.chat.id, "⏳ Отправляю приказ ВВЕРХ...")
        success, trade_id = api.buy(config.TRADE_AMOUNT, "BTCUSDT_OTC", "call", config.EXPIRATION_TIME)
        
        if success:
            bot.send_message(message.chat.id, f"✅ Сделка ВВЕРХ открыта! ID: {trade_id}")
        else:
            bot.send_message(message.chat.id, f"❌ Ошибка открытия сделки: {trade_id}")

    # Обработка кнопки ВНИЗ
    elif message.text == "🔴 ОТКРЫТЬ ВНИЗ (PUT)":
        bot.send_message(message.chat.id, "⏳ Отправляю приказ ВНИЗ...")
        success, trade_id = api.buy(config.TRADE_AMOUNT, "BTCUSDT_OTC", "put", config.EXPIRATION_TIME)
        
        if success:
            bot.send_message(message.chat.id, f"✅ Сделка ВНИЗ открыта! ID: {trade_id}")
        else:
            bot.send_message(message.chat.id, f"❌ Ошибка открытия сделки: {trade_id}")

if __name__ == "__main__":
    print("[Telegram] Ручной пульт запущен. Нажмите /start в вашем боте.")
    bot.infinity_polling()
