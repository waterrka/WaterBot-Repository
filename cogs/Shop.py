import disnake
from disnake.ext import commands
import sqlite3
import random
from cogs.services.BalanceService import BalanceService

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
        "desc": "Чистый и полезный",
        "use_text": "Вы глубоко вдохнули воздух... и ничего не произошло. Но стало легче на душе."
    },
    100: {
        "name": "Резиновая утка",
        "emoji": "🦆",
        "desc": "Ква-Ква",
        "use_text": "🦆 Ква-ква! Утка одобряет ваш выбор. Теперь вы на 5% счастливее!"
    },
    200: {
        "name": "Лотерейный билет",
        "emoji": "🎟",
        "desc": "Может принести от 100 до 1000📼",
        "effect": "lottery",
    },
    500: {
        "name": "Костюм горничной",
        "emoji": "👗",
        "desc": "Лучший товар, японского качества.",
        "role_id": 1386386401779646464,
        "use_text": "👗 Вы облачились в костюм горничной. Выдана новая роль."
    },
    700: {
        "name": "Комару фан",
        "emoji": "🎧",
        "desc": "Любишь Комару?",
        "role_id": 1277235825830264912,
        "use_text": "🎧 Вы надели наушники и погрузились в мир Комару. Выдана новая роль."
    },
    1000: {
        "name": "Счастливая монета",
        "emoji": "🪙 ",
        "desc": "Ходят слухи, что оно дает деньги",
        "role_id": 1398213186137751632,
        "use_text": "🪙 Удача будет явно на вашей стороне. Выдана новая роль."
    },
    3000: {
        "name": "Важный гость",
        "emoji": "👔",
        "desc": "Открывает доступ к тайнам",
        "role_id": 1371104857775411251,
        "use_text": "👔 Вас проводят через потайные двери... Вы — Важный гость. Выдана новая роль."
    },
    4000: {
        "name": "Владелец блога",
        "emoji": "📝",
        "desc": "Блог на сервере",
        "role_id": 1266857840732143697,
        "use_text": "📝 Вы стали владельцем блога, обязательно пинганите об этом <@679722204144992262>. Выдана новая роль."
    },
    5000: {
        "name": "Кастомная роль",
        "emoji": "🎨",
        "desc": "Позволяет получить уникальную кастомную роль с цветом и названием по вашему выбору.",
        "role_id": 1266857840732143697,
        "use_text": "🎨 Вы приобрели кастомную роль! Пожалуйста, упомяните <@&1266812096209879123> и укажите желаемое имя и цвет роли."
    },
    6000: {
        "name": "Капиталист",
        "emoji": "💰",
        "desc": "Он уже зарабатывает на тебе",
        "role_id": 1278746179206910053,
        "use_text": "💰 Деньги текут в ваших венах. Вы стали настоящим капиталистом! Выдана новая роль."
    },
    30000: {
        "name": "Повелитель экономики",
        "emoji": "👑",
        "desc": "Богатейший человек на сервере",
        "role_id": 1371105600204701829,
        "use_text": "👑 Вся экономика склоняется перед вами. Поздравляем, Вы — Повелитель богатства! Выдана новая роль."
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
            embed.add_field(name=f"{emoji} {item_name}", value=f"Количество:\n{amount}", inline=False)
        if ctx.author.id == target.id:
            await ctx.send(embed=embed, view=ItemDropdownView(self.bot, target.id, items))
        else:
            await ctx.send(embed=embed)

    @commands.slash_command(name='shop', description='Магазин')
    async def shop(self, ctx):
        embed = disnake.Embed(title='Магазин watershop', color=0xFFFFFF)
        for idx, (price, info) in enumerate(SHOP_ITEMS.items(), start=1):
            prefix = "★" if "role_id" in info else ""
            embed.add_field(
                name=f"{prefix}{idx}. {info['emoji']} {info['name']} — {price}📼",
                value=info['desc'],
                inline=False
            )
            embed.set_footer(text='★ — предметы с ролью и доходом')
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
        if ctx.author.id != self.user_id:
            embed = disnake.Embed(
                title='Ошибка',
                description='Вы не можете использовать чужой инвентарь.',
                color=0xFFFFFF
            )
            await ctx.response.send_message(embed=embed, ephemeral=True)
            return
        
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
                    (100, 50),
                    (200, 25),
                    (500, 15),
                    (700, 7),
                    (1000, 3)
                ]
                roll = random.randint(1, 100)
                current = 0
                reward = 0

                for amount, chance in lottery_rewards:
                    current += chance
                    if roll <= current:
                        reward = amount
                        break

                balance_service = BalanceService()
                balance_service.update_balance(self.user_id, reward)

                embed = disnake.Embed(
                    title='Лотерея',
                    description=f"Вы использовали {item['emoji']} **{item['name']}** и выиграли ||**{reward}📼**||!",
                    color=0xFFFFFF
                )
                embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.display_avatar.url)

                if new_amount > 0:
                    view = disnake.ui.View()
                    view.add_item(UseAgainButton(self.bot, self.user_id, price, item["name"], new_amount))
                    await ctx.response.send_message(embed=embed, view=view)
                else:
                    await ctx.response.send_message(embed=embed)
                return

            role_id = item.get('role_id')
            if role_id:
                role = ctx.guild.get_role(role_id)
                if role:
                    await ctx.author.add_roles(role)
            embed = disnake.Embed(
                title=None,
                description=item.get('use_text'),
                color=0xFFFFFF
            )
            embed.set_author(name=f'{ctx.author.display_name} использовал {item["emoji"]} {item["name"]}', icon_url=ctx.author.display_avatar.url)
            
            if not item.get("role_id") and new_amount > 0:
                view = disnake.ui.View()
                view.add_item(UseAgainButton(self.bot, self.user_id, price, item["name"], new_amount))
                await ctx.response.send_message(embed=embed, view=view)
            else:
                await ctx.response.send_message(embed=embed)

class ItemSellDropdown(disnake.ui.StringSelect):
    def __init__(self, bot, user_id, items):
        self.bot = bot
        self.user_id = user_id
        self.items = items

        options = []
        for item_name, amount in items:
            for price, info in SHOP_ITEMS.items():
                if info['name'] == item_name:
                    options.append(disnake.SelectOption(
                        label=f"{info['emoji']} {item_name} x {amount}",
                        value=f"{price}|{item_name}|{amount}",
                        description=f"{info['name']} x {amount} - {price // 2}📼 за шт"
                    ))
                    break

        super().__init__(
            placeholder='Выберите предметы для продажи',
            options=options,
            min_values=1,
            max_values=len(options)  
        )

    async def callback(self, ctx):
        if ctx.author.id != self.user_id:
            embed = disnake.Embed(
                title='Ошибка',
                description='Вы не можете использовать чужой инвентарь.',
                color=0xFFFFFF
            )
            await ctx.response.send_message(embed=embed, ephemeral=True)
            return

        total_reward = 0
        balance_service = BalanceService()

        for selection in self.values:
            price_str, item_name, amount_str = selection.split("|")
            price = int(price_str)
            amount = int(amount_str)

            cursor.execute(
                "SELECT amount FROM inventory WHERE user_id = ? AND item_name = ?",
                (self.user_id, item_name)
            )
            result = cursor.fetchone()

            if result:
                cursor.execute("DELETE FROM inventory WHERE user_id = ? AND item_name = ?", (self.user_id, item_name))
                reward = (price // 2) * amount
                total_reward += reward

        conn.commit()
        balance_service.update_balance(self.user_id, total_reward)

        embed = disnake.Embed(
            title='Продажа завершена',
            description=f'Вы продали {len(self.values)} предметов и получили **{total_reward}📼**.',
            color=0xFFFFFF
        )
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.display_avatar.url)
        await ctx.response.send_message(embed=embed)

class ItemDropdownView(disnake.ui.View):
    def __init__(self, bot, user_id, items):
        super().__init__()
        self.add_item(ItemDropdown(bot, user_id, items))
        self.add_item(ItemSellDropdown(bot, user_id, items))

class ConfirmPurchaseView(disnake.ui.View):
    def __init__(self, bot, user_id, item_price, item_info):
        super().__init__(timeout=60)
        self.bot = bot
        self.user_id = user_id
        self.item_price = item_price
        self.item_info = item_info

    async def purchase(self, ctx: disnake.MessageInteraction, amount: int):
        await ctx.response.defer()
        
        balance_service = BalanceService()
        total_price = self.item_price * amount
        user_balance = balance_service.get_balance(self.user_id)

        if user_balance < total_price:
            embed = disnake.Embed(
                title='Ошибка',
                description='Недостаточно средств для покупки.',
                color=0xFFFFFF
            )
            await ctx.response.edit_message(embed=embed, view=None)
            self.stop()
            return

        balance_service.update_balance(self.user_id, -total_price)
        shop_cog = self.bot.get_cog('Shop')
        shop_cog.add_to_inventory(self.user_id, self.item_info['name'], amount)

        embed = disnake.Embed(
            title='Поздравляем с покупкой!',
            description=f"Вы купили {amount} × {self.item_info['emoji']} **{self.item_info['name']}** за {total_price}📼. Чтобы использовать предмет, напишите /inventory",
            color=0xFFFFFF
        )
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.display_avatar.url)
        await ctx.channel.send(embed=embed)

    @disnake.ui.button(label='Подтвердить', style=disnake.ButtonStyle.green)
    async def confirm(self, button: disnake.ui.Button, ctx: disnake.MessageInteraction):
        await self.purchase(ctx, 1)

    @disnake.ui.button(label='Купить x5', style=disnake.ButtonStyle.blurple)
    async def buy_five(self, button: disnake.ui.Button, ctx: disnake.MessageInteraction):
        await self.purchase(ctx, 5)

    @disnake.ui.button(label='Отмена', style=disnake.ButtonStyle.red)
    async def cancel(self, button: disnake.ui.Button, ctx: disnake.MessageInteraction):
        embed = disnake.Embed(
            title='Отмена покупки',
            description='Покупка отменена.'
        )
        await ctx.response.edit_message(embed=embed, view=None)
        self.stop()

class UseAgainButton(disnake.ui.Button):
    def __init__(self, bot, user_id, item_price, item_name, remaining_amount):
        super().__init__(
            label=f'Использовать ещё [{remaining_amount}]',
            style=disnake.ButtonStyle.green
        )
        self.bot = bot
        self.user_id = user_id
        self.item_price = item_price
        self.item_name = item_name

    async def callback(self, ctx: disnake.MessageInteraction):
        if ctx.author.id != self.user_id:
            await ctx.response.send_message("Вы не можете использовать чужой инвентарь.", ephemeral=True)
            return

        item = SHOP_ITEMS[self.item_price]

        cursor.execute("SELECT amount FROM inventory WHERE user_id = ? AND item_name = ?", (self.user_id, self.item_name))
        result = cursor.fetchone()
        if not result or result[0] <= 0:
            await ctx.response.send_message("У вас больше нет этого предмета.", ephemeral=True)
            return

        new_amount = result[0] - 1
        if new_amount == 0:
            cursor.execute("DELETE FROM inventory WHERE user_id = ? AND item_name = ?", (self.user_id, self.item_name))
        else:
            cursor.execute("UPDATE inventory SET amount = ? WHERE user_id = ? AND item_name = ?", (new_amount, self.user_id, self.item_name))
        conn.commit()

        balance_service = BalanceService()

        if item.get("effect") == "lottery":
            lottery_rewards = [
                (100, 50),
                (200, 25),
                (500, 15),
                (700, 7),
                (1000, 3)
            ]
            roll = random.randint(1, 100)
            current = 0
            reward = 0

            for amount, chance in lottery_rewards:
                current += chance
                if roll <= current:
                    reward = amount
                    break

            balance_service.update_balance(self.user_id, reward)

            embed = disnake.Embed(
                title='Лотерея',
                description=f"Вы использовали {item['emoji']} **{item['name']}** и выиграли ||**{reward}📼**||!",
                color=0xFFFFFF
            )
        else:
            embed = disnake.Embed(
                description=item.get("use_text"),
                color=0xFFFFFF
            )

        embed.set_author(name=f'{ctx.author.display_name} использовал {item["emoji"]} {item["name"]}', icon_url=ctx.author.display_avatar.url)

        if new_amount > 0:
            view = disnake.ui.View()
            view.add_item(UseAgainButton(self.bot, self.user_id, self.item_price, self.item_name, new_amount))
            await ctx.response.edit_message(embed=embed, view=view)
        else:
            await ctx.response.edit_message(embed=embed, view=None)

def setup(bot):
    bot.add_cog(Shop(bot))