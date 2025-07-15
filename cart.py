from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackQueryHandler, ContextTypes

# Добавить товар в корзину
async def add_to_cart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    # Получаем название товара из callback_data
    _, product_name = query.data.split(":", 1)

    # Инициализируем корзину, если её ещё нет
    cart = context.user_data.setdefault("cart", {})

    # Увеличиваем количество или создаём новую позицию
    if product_name in cart:
        cart[product_name] += 1
    else:
        cart[product_name] = 1

    await query.message.reply_text(f"🛒 {product_name} добавлен в корзину.")

# Команда "Корзина"
async def view_cart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cart = context.user_data.get("cart", {})

    if not cart:
        await update.message.reply_text("🧺 Ваша корзина пуста.")
        return

    text = "🛒 *Ваша корзина:*\n"
    total = 0
    keyboard = []

    for name, qty in cart.items():
        text += f"• {name} — {qty} шт.\n"
        keyboard.append([
            InlineKeyboardButton("➖", callback_data=f"decrease:{name}"),
            InlineKeyboardButton("Удалить", callback_data=f"remove:{name}"),
            InlineKeyboardButton("➕", callback_data=f"increase:{name}")
        ])

    keyboard.append([
        InlineKeyboardButton("🧹 Очистить", callback_data="clear_cart")
    ])

    await update.message.reply_text(
        text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard)
    )

# Удаление, изменение и очистка
async def handle_cart_actions(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data
    cart = context.user_data.get("cart", {})

    if data.startswith("increase:"):
        name = data.split(":", 1)[1]
        cart[name] += 1

    elif data.startswith("decrease:"):
        name = data.split(":", 1)[1]
        if cart[name] > 1:
            cart[name] -= 1
        else:
            del cart[name]

    elif data.startswith("remove:"):
        name = data.split(":", 1)[1]
        if name in cart:
            del cart[name]

    elif data == "clear_cart":
        cart.clear()

    await query.message.delete()
    await view_cart(query, context)

# Подключение к приложению
def register_cart_handlers(app):
    app.add_handler(CallbackQueryHandler(add_to_cart, pattern=r"^add_to_cart:"))
    app.add_handler(CallbackQueryHandler(handle_cart_actions, pattern=r"^(increase|decrease|remove|clear_cart)"))
