import disnake
from disnake.ext import commands
import sqlite3

conn = sqlite3.connect('inventory.db')
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS inventory (
    user_id INTEGER,
    item_name TEXT,
    amount INTEGER,
    PRIMARY KEY(user_id, item_name)
)
""")

conn.commit()

class Inventory(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    def add_to_inventory(self, user_id: int, item_name: str, amount: int):
        cursor.execute(
            "SELECT amount FROM inventory WHERE user_id = ? AND item_name = ?",
            (user_id, item_name)
        )
        result = cursor.fetchone()

        if result:
            new_amount = result[0] + amount
            cursor.execute(
                "UPDATE inventory SET amount = ? WHERE user_id = ? AND item_name = ?",
                (new_amount, user_id, item_name)
            )
        else:
            cursor.execute(
                "INSERT INTO inventory (user_id, item_name, amount) VALUES (?, ?, ?)",
                (user_id, item_name, amount)
            )
        conn.commit()

    def get_inventory(self, user_id: int):
        cursor.execute(
            "SELECT item_name, amount FROM inventory WHERE user_id = ?",
            (user_id,)
        )
        return cursor.fetchall()

def setup(bot):
    bot.add_cog(Inventory(bot))