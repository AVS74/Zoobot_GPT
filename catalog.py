import sqlite3
from telegram import InlineKeyboardMarkup, InlineKeyboardButton, Update
from telegram.ext import CallbackQueryHandler, CommandHandler, ContextTypes

DB_PATH = "products.db"

# Команда /catalog — показать категории (по food_type)
async def catalog_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    categories = get_unique_values("food_type")
    context.user_data["categories"] = categories  # сохраняем список

    keyboard = [
        [InlineKeyboardButton(cat, callback_data=f"category:{i}")]
        for i, cat in enumerate(categories)
    ]

    await update.message.reply_text("Выберите категорию:", reply_markup=InlineKeyboardMarkup(keyboard))


# Обработка выбора категории — показать подкатегории (animal)
async def handle_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    index = int(query.data.split(":")[1])
    category = context.user_data["categories"][index]
    context.user_data["selected_category"] = category

    subcategories = get_unique_values("animal", "food_type", category)
    context.user_data["subcategories"] = subcategories

    keyboard = [
        [InlineKeyboardButton(subcat, callback_data=f"subcategory:{i}")]
        for i, subcat in enumerate(subcategories)
    ]

    await query.edit_message_text(
        f"Вы выбрали категорию: *{category}*\nВыберите животное:",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# Обработка выбора подкатегории — показать товары
async def handle_subcategory(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    index = int(query.data.split(":")[1])
    subcategory = context.user_data["subcategories"][index]
    category = context.user_data["selected_category"]

    products = get_products(category, subcategory)

    if not products:
        await query.edit_message_text("Нет товаров в этой категории.")
        return

    for product in products:
        brand = product["brand"]
        variant = product["variant"]
        price = product["price"]

        text = f"*{brand}*\nФасовка: {variant}\nЦена: {price} ₽"
        button = InlineKeyboardMarkup([
            [InlineKeyboardButton("🛒 В корзину", callback_data=f"add_to_cart:{brand}")]
        ])

        await query.message.reply_text(text, reply_markup=button, parse_mode="Markdown")

# Вспомогательные функции

def get_unique_values(column: str, where_column=None, where_value=None):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    if where_column and where_value:
        cursor.execute(f"SELECT DISTINCT {column} FROM products WHERE {where_column} = ?", (where_value,))
    else:
        cursor.execute(f"SELECT DISTINCT {column} FROM products")

    rows = cursor.fetchall()
    conn.close()
    return [row[0] for row in rows]

def get_products(category: str, subcategory: str):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM products WHERE food_type = ? AND animal = ?",
        (category, subcategory)
    )
    rows = cursor.fetchall()
    conn.close()
    return rows

# Регистрация обработчиков
def register_catalog_handlers(app):
    app.add_handler(CommandHandler("catalog", catalog_command))
    app.add_handler(CallbackQueryHandler(handle_category, pattern=r"^category:"))
    app.add_handler(CallbackQueryHandler(handle_subcategory, pattern=r"^subcategory:"))
