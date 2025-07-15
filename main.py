# main.py — запуск Telegram-бота

import os
from dotenv import load_dotenv
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)
from catalog import register_catalog_handlers, catalog_command
from cart import register_cart_handlers, view_cart

# Загружаем токен из .env
load_dotenv()
TOKEN = os.getenv("TOKEN")

# Приветствие при /start или кнопке "Старт"
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [["Старт", "Каталог", "Корзина"]]  # Нижняя клавиатура
    reply_markup = ReplyKeyboardMarkup(
        keyboard, resize_keyboard=True, one_time_keyboard=False
    )

    await update.message.reply_text(
        "Добро пожаловать в наш зоомагазин! 🐶🐱\n\n"
        "Я помогу тебе выбрать товары, оформить заказ и получить быструю доставку.\n\n"
        "Нажми кнопку 'Каталог' или 'Старт', чтобы начать 🛒",
        reply_markup=reply_markup,
    )

# Обработка кнопки "Старт"
async def handle_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == "Старт":
        await start(update, context)
    elif text == "Каталог":
        await catalog_command(update, context)  # Без команды — вызываем напрямую
    elif text == "Корзина":
        await view_cart(update, context)


# Запуск бота
if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()
    register_cart_handlers(app)

    # Команды и кнопки
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_button))

    # Подключаем каталог
    register_catalog_handlers(app)

    # Старт
    print("Бот запущен...")
    app.run_polling()
