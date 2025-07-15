import pandas as pd
import sqlite3

# Read Excel file
excel_file = "C:\\Zoobot\\Products.xlsx"
df = pd.read_excel(excel_file)

# Standardize food_type to match bot's expectations
food_type_mapping = {
    "Сухой корм для собак": "Корм сухой для собак",
    "Сухой корм для кошек": "Корм сухой для кошек",
    "Влажный корм для собак": "Влажный корм для собак",
    "Влажный корм для кошек": "Влажный корм для кошек"
}
df["food_type"] = df["food_type"].map(food_type_mapping)

# Connect to SQLite database
conn = sqlite3.connect("C:\\Zoobot\\products.db")
cursor = conn.cursor()

# Create products table
cursor.execute("""
    CREATE TABLE IF NOT EXISTS products (
        food_type TEXT,
        brand TEXT,
        animal TEXT,
        variant TEXT,
        price INTEGER,
        PRIMARY KEY (food_type, brand, animal, variant)
    )
""")

# Insert data
for _, row in df.iterrows():
    cursor.execute(
        "INSERT OR REPLACE INTO products (food_type, brand, animal, variant, price) VALUES (?, ?, ?, ?, ?)",
        (row["food_type"], row["brand"], row["animal"], row["variant"], int(row["price"]))
    )

# Commit and close
conn.commit()
conn.close()

print("Products imported to products.db successfully!")