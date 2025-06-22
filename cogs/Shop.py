import disnake
from disnake.ext import commands
import sqlite3
import random

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

SHOP_ITEMS = {
    10: {
        "name": "Воздух",
        "emoji": "💨",
        "desc": "Чистый и полезный"
    },
    100: {
        "name": "Бананчеке",
        "emoji": "🍌",
        "desc": "Просто бананчеке. Но они могут понадобиться позже..."
    },
    200: {
        "name": "Лотерейный билет",
        "emoji": "🎟",
        "desc": "Может принести от 100 до 1000📼",
        "effect": "lottery"
    },
    1000: {
        "name": "Комару фан",
        "emoji": "🎧",
        "desc": "Любишь Комару?",
        "role_id": 1277235825830264912
    },
    2000: {
        "name": "Владелец блога",
        "emoji": "📝",
        "desc": "Блог на сервере",
        "role_id": 1266857840732143697
    },
    3000: {
        "name": "Хранитель порядка",
        "emoji": "🛡",
        "desc": "Не модератор, но будто им родился",
        "role_id": 1278746391149154409
    },
    5000: {
        "name": "Важный гость",
        "emoji": "👔",
        "desc": "Открывает доступ к тайнам",
        "role_id": 1371104857775411251
    },
    8000: {
        "name": "Капиталист",
        "emoji": "💰",
        "desc": "Он уже зарабатывает на тебе",
        "role_id": 1278746179206910053
    },
    30000: {
        "name": "Повелитель экономики",
        "emoji": "👑",
        "desc": "Богатейший человек на сервере",
        "role_id": 1371105600204701829
    }
}

class Shop(commands.Cog):

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

    @commands.slash_command(name='inventory', description='Показать ваш инвентарь')
    async def inventory(self, ctx, member: disnake.Member = None):
        target = member or ctx.author
        items = self.get_inventory(target.id)
        if not items:
            await ctx.send(embed=disnake.Embed(title=f"Инвентарь {target.display_name}", description="📦Инвентарь пуст.", color=0xFFFFFF))
            return
        embed = disnake.Embed(title=f"Инвентарь {target.display_name}", color=0xFFFFFF)
        for item_name, amount in items:
            emoji = next((info["emoji"] for info in SHOP_ITEMS.values() if info["name"] == item_name), '')
            embed.add_field(name=f"{emoji} {item_name}", value=f"Количество:\n```{amount}```", inline=False)
        if ctx.author.id == target.id:
            await ctx.send(embed=embed, view=ItemDropdownView(self.bot, target.id, items))
        else:
            await ctx.send(embed=embed)

    @commands.slash_command(name='shop', description='Магазин')
    async def shop(self, ctx):
        embed = disnake.Embed(title='Магазин watershop', color=0xFFFFFF)
        for price, info in SHOP_ITEMS.items():
            embed.add_field(
                name=f"{info['emoji']} {info['name']} — {price}📼",
                value=info['desc'],
                inline=False
            )
        await ctx.send(embed=embed, view=DropdownView(self.bot))

class Dropdown(disnake.ui.StringSelect):
    def __init__(self, bot):
        self.bot = bot
        options = [
            disnake.SelectOption(
                label=f"{item['emoji']} {item['name']} — {price}📼",
                description=item['desc'],
                value=str(price)
            ) for price, item in SHOP_ITEMS.items()
        ]
        super().__init__(placeholder='Выберите товар для покупки', options=options)

    async def callback(self, ctx: disnake.MessageInteraction):
        price = int(self.values[0])
        item = SHOP_ITEMS[price]

        view = ConfirmPurchaseView(self.bot, ctx.author.id, price, item)
        embed = disnake.Embed(
            title='Потверждение покупки',
            description=f"Вы уверены, что хотите купить {item['emoji']} **{item['name']}**?",
            color=0xFFFFFF
        )
        await ctx.response.send_message(embed=embed, view=view, ephemeral=True)

class DropdownView(disnake.ui.View):
    def __init__(self, bot):
        super().__init__()
        self.add_item(Dropdown(bot))

class ItemDropdown(disnake.ui.StringSelect):
    def __init__(self, bot, user_id, items):
        self.bot = bot
        self.user_id = user_id
        options = []
        for item_name, amount in items:
            for price, info in SHOP_ITEMS.items():
                if info['name'] == item_name:
                    options.append(disnake.SelectOption(
                        label=f"{info['emoji']} {item_name}",
                        value=str(price),
                        description=f"Количество: {amount}"
                    ))
                    break
        super().__init__(placeholder='Использовать предмет', options=options)

    async def callback(self, ctx):
        price = int(self.values[0])
        item = SHOP_ITEMS[price]
        cursor.execute("SELECT amount FROM inventory WHERE user_id = ? AND item_name = ?", (self.user_id, item['name']))
        result = cursor.fetchone()
        if result and result[0] > 0:
            new_amount = result[0] - 1
            if new_amount == 0:
                cursor.execute("DELETE FROM inventory WHERE user_id = ? AND item_name = ?", (self.user_id, item['name']))
            else:
                cursor.execute("UPDATE inventory SET amount = ? WHERE user_id = ? AND item_name = ?", (new_amount, self.user_id, item['name']))
            conn.commit()

            effect = item.get("effect")
            if effect == "lottery":
                lottery_rewards = [
                    (100, 54),
                    (200, 30),
                    (500, 10),
                    (700, 5),
                    (1000, 1)
                ]
                roll = random.randint(1, 100)
                current = 0
                reward = 0

                for amount, chance in lottery_rewards:
                    current += chance
                    if roll <= current:
                        reward = amount
                        break

                economy = self.bot.get_cog('Economy')
                economy.update_balance(self.user_id, reward)

                embed = disnake.Embed(
                    title="Лотерея",
                    description=f"Вы использовали {item['emoji']} **{item['name']}** и выиграли **{reward}📼**!",
                    color=0xFFFFFF
                )
                await ctx.response.send_message(embed=embed)
                return

            role_id = item.get('role_id')
            if role_id:
                role = ctx.guild.get_role(role_id)
                if role:
                    await ctx.author.add_roles(role)
            embed = disnake.Embed(
                title='Предмет использован',
                description=f'Вы использовали {item["emoji"]} **{item["name"]}**!',
                color=0xFFFFFF
            )
            await ctx.response.send_message(embed=embed)

class ItemDropdownView(disnake.ui.View):
    def __init__(self, bot, user_id, items):
        super().__init__()
        self.add_item(ItemDropdown(bot, user_id, items))

class ConfirmPurchaseView(disnake.ui.View):
    def __init__(self, bot, user_id, item_price, item_info):
        super().__init__(timeout=60)
        self.bot = bot
        self.user_id = user_id
        self.item_price = item_price
        self.item_info = item_info

    async def purchase(self, ctx: disnake.MessageInteraction, amount: int):
        economy = self.bot.get_cog('Economy')
        total_price = self.item_price * amount
        user_balance = economy.get_balance(self.user_id)

        if user_balance < total_price:
            await ctx.response.edit_message(content=f'Недостаточно средств для покупки {amount} предмет{"ов" if amount > 1 else ""} за {total_price}📼.', view=None)
            self.stop()
            return

        economy.update_balance(self.user_id, -total_price)
        shop_cog = self.bot.get_cog('Shop')
        shop_cog.add_to_inventory(self.user_id, self.item_info['name'], amount)

        embed = disnake.Embed(
            title='Поздравляем с покупкой!',
            description=f"Вы купили {amount} × {self.item_info['emoji']} **{self.item_info['name']}** за {total_price}📼. ```Чтобы использовать предмет, напишите /inventory```",
            color=0xFFFFFF
        )
        await ctx.channel.send(embed=embed)
        self.stop()

    @disnake.ui.button(label='Подтвердить', style=disnake.ButtonStyle.green)
    async def confirm(self, button: disnake.ui.Button, ctx: disnake.MessageInteraction):
        await self.purchase(ctx, 1)

    @disnake.ui.button(label='Купить x5', style=disnake.ButtonStyle.blurple)
    async def buy_five(self, button: disnake.ui.Button, ctx: disnake.MessageInteraction):
        await self.purchase(ctx, 5)

    @disnake.ui.button(label='Отмена', style=disnake.ButtonStyle.red)
    async def cancel(self, button: disnake.ui.Button, ctx: disnake.MessageInteraction):
        await ctx.response.edit_message(content='Покупка отменена.', view=None)
        self.stop()

def setup(bot):
    bot.add_cog(Shop(bot))