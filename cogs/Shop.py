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

ITEM_ROLES = {
    1000: 1277235825830264912, # роль для товара "Комару фан"
    2000: 1266857840732143697, # роль для товара "Владелец блога"
    3000: 1278746391149154409, # роль для товара "Хранитель порядка"
    5000: 1371104857775411251, # роль для товара "Важный гость"
    6500: 1371104483928440852, # роль для товара "Дипломат"
    8000: 1278746179206910053, # роль для товара "Капиталист"
    10000: 1371105385917845564, # роль для товара "Аристократ"
    30000: 1371105600204701829, # роль для товара "Повелитель экономики"
}

ITEM_NAMES = {
    10: 'Воздух',
    100: 'Костюм горничной',
    1000: 'Комару фан',
    2000: 'Владелец блога',
    3000: 'Хранитель порядка',
    5000: 'Важный гость',
    6500: 'Дипломат',
    8000: 'Капиталист',
    10000: 'Аристократ',
    30000: 'Повелитель экономики'
}

ITEM_EMOJIS = {
    'Воздух': '💨',
    'Костюм горничной': '👗',
    'Комару фан': '🎧',
    'Владелец блога': '📝',
    'Хранитель порядка': '🛡',
    'Важный гость': '👔',
    'Дипломат': '💼',
    'Капиталист': '💰',
    'Аристократ': '🎩',
    'Повелитель экономики': '👑'
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
        target = member or ctx.author  
        target_name = member.display_name if member else member.display_name  
        user_id = target.id  
        items = self.get_inventory(user_id)

        if not items:
            embed = disnake.Embed(
                title=f'Инвентарь {target_name}', 
                description='📦Инвентарь пуст.',
                color=0xFFFFFF
                )
            await ctx.response.send_message(embed=embed)
            return

        embed = disnake.Embed(
            title=f'Инвентарь {ctx.author.display_name}', 
            description=None,
            color=0xFFFFFF
            )
        for item_name, amount in items:
            emoji = ITEM_EMOJIS.get(item_name, '')
            embed.add_field(name=f'{emoji} {item_name}', value=f'Количество:\n```{amount}```', inline=False)

        if ctx.author.id != target.id:
            await ctx.response.send_message(embed=embed)
            return

        view = ItemDropdownView(self.bot, user_id, items)
        await ctx.response.send_message(embed=embed, view=view)

    @commands.slash_command(name='shop', description='Магазин')
    async def shop(self, ctx):
        embed = disnake.Embed(
            title='Магазин watershop',
            color=0xFFFFFF
        )
        embed.add_field(
            name='💨 Воздух — 10📼',
            value='Чистый и полезный\n',
            inline=False
        )
        embed.add_field(
            name='👗 Костюм горничной — 100📼',
            value='Оно тебе надо?\n',
            inline=False
        )
        embed.add_field(
            name='🎧 Комару фан — 1000📼',
            value='Любишь Комару?\n',
            inline=False
        )
        embed.add_field(
            name='📝 Владелец блога — 2000📼',
            value='Блог на сервере\n',
            inline=False
        )
        embed.add_field(
            name='🛡 Хранитель Порядка — 3000📼',
            value='Не модератор, но будто им родился\n',
            inline=False
        )
        embed.add_field(
            name='👔 Важный гость — 5000📼',
            value='Открывает доступ к тайнам\n',
            inline=False
        )
        embed.add_field(
            name='💼 Дипломат — 6500📼',
            value='Умеет решать конфликты без мьютов и банов\n',
            inline=False
        )
        embed.add_field(
            name='💰 Капиталист — 8000📼',
            value='Если ты читаешь это — он уже зарабатывает на тебе\n',
            inline=False
        )
        embed.add_field(
            name='🎩 Аристократ — 15000📼',
            value='Пишет только с заглавной буквы и ставит точку в конце.\n',
            inline=False
        )
        embed.add_field(
            name='👑 Повелитель экономики — 30000📼',
            value='Богатейший человек на сервере\n',
            inline=False
        )
        embed.add_field(name='\u200b', value='\u200b', inline=True)
        embed.add_field(name='\u200b', value='\u200b', inline=True)

        view = DropdownView(self.bot)
        await ctx.response.send_message(embed=embed, view=view)

class Dropdown(disnake.ui.StringSelect):
    def __init__(self, bot):
        self.bot = bot
        options = [
            disnake.SelectOption(label='💨 Воздух — 10📼', description='Чистый и полезный', value='10'),
            disnake.SelectOption(label='👗 Костюм горничной — 100📼', description='Оно тебе надо?', value='100'),
            disnake.SelectOption(label='🎧 Комару фан — 1000📼', description='Любишь Комару?', value='1000'),
            disnake.SelectOption(label='📝 Владелец блога — 2000📼', description='Блог на сервере', value='2000'),
            disnake.SelectOption(label='🛡 Хранитель Порядка — 3000📼', description='Не модератор, но будто им родился', value='3000'),
            disnake.SelectOption(label='👔 Важный гость — 5000📼', description='Открывает доступ к тайнам', value='5000'),
            disnake.SelectOption(label='💼 Дипломат — 6500📼', description='Решает конфликты без мьютов и банов', value='6500'),
            disnake.SelectOption(label='💰 Капиталист — 8000📼', description='Он уже зарабатывает на тебе', value='8000'),
            disnake.SelectOption(label='🎩 Аристократ — 15000📼', description='Пишет только с заглавной буквы и точкой', value='10000'),
            disnake.SelectOption(label='👑 Повелитель экономики — 30000📼', description='Богатейший человек на сервере', value='30000'),
        ]
        super().__init__(
            placeholder='Выберите товар для покупки',
            options=options
        )

    async def callback(self, ctx: disnake.MessageInteraction):
        economy = self.bot.get_cog('Economy')
        price = int(self.values[0])
        user_balance = economy.get_balance(ctx.author.id)
        
        if user_balance >= price:
            formatted_balance = economy.format_balance(economy.update_balance(ctx.author.id, -price))

            item_name = ITEM_NAMES.get(price)

            shop_cog = self.bot.get_cog('Shop')
            if shop_cog:
                shop_cog.add_to_inventory(ctx.author.id, item_name, 1)

            item_name = ITEM_NAMES.get(price)
            emoji = ITEM_EMOJIS.get(item_name, '')

            embed = disnake.Embed(
                title='Покупка успешна!',
                description=f'Поздравляем с покупкой {emoji} **{item_name}**! Что бы использовать предмет /inventory\nВаш текущий баланс: ```{formatted_balance}```',
                color=0xFFFFFF
            )
            await ctx.response.send_message(embed=embed)

        else:
            formatted_balance = economy.format_balance(user_balance)
            embed = disnake.Embed(
                title='Недостаточно средств!',
                description=f'Ваш текущий баланс: ```{formatted_balance}```',
                color=0xFFFFFF
            )
            await ctx.response.send_message(embed=embed, ephemeral=True)

    async def economy_error(self, ctx, error):
        if isinstance(error, commands.CommandError):
            embed = disnake.Embed(
                title='Ошибка',
                description='Произошла ошибка при обработке вашей покупки. Попробуйте снова позже.',
                color=0xFFFFFF
            )
            await ctx.response.send_message(embed=embed, ephemeral=True)

class DropdownView(disnake.ui.View):
    def __init__(self, bot):
        super().__init__()
        self.add_item(Dropdown(bot))

class ItemDropdown(disnake.ui.StringSelect):
    def __init__(self, bot, user_id, items):
        self.bot = bot
        self.user_id = user_id

        options = [
            disnake.SelectOption(
                label=f'{ITEM_EMOJIS.get(name, "")} {name}',
                value=str(price), 
                description=f'Количество: {amount}'
            ) for name, amount in items if amount > 0 and (price := next((price for price, item in ITEM_NAMES.items() if item == name), None)) is not None
        ]

        super().__init__(
            placeholder='Использовать предмет',
            options=options
        )

    async def callback(self, ctx):
        shop_cog = self.bot.get_cog('Shop')

        if not shop_cog:
            await ctx.response.send_message("Ошибка: Shop cog не найден.", ephemeral=True)
            return

        price = int(self.values[0])  
        item_name = ITEM_NAMES.get(price)

        cursor.execute("SELECT amount FROM inventory WHERE user_id = ? AND item_name = ?", (self.user_id, item_name))
        result = cursor.fetchone()

        if result and result[0] > 0:
            new_amount = result[0] - 1

            if new_amount == 0:
                cursor.execute("DELETE FROM inventory WHERE user_id = ? AND item_name = ?", (self.user_id, item_name))
            else:
                cursor.execute("UPDATE inventory SET amount = ? WHERE user_id = ? AND item_name = ?", (new_amount, self.user_id, item_name))
            conn.commit()

            role_id = ITEM_ROLES.get(price)
            role = ctx.guild.get_role(role_id)
            if role:
                await ctx.author.add_roles(role)

            emoji = ITEM_EMOJIS.get(item_name, '')
            embed = disnake.Embed(
                title='Предмет использован',
                description=f'Вы использовали {emoji} **{item_name}**!',
                color=0xFFFFFF
            )
            await ctx.response.send_message(embed=embed)

class ItemDropdownView(disnake.ui.View):
    def __init__(self, bot, user_id, items):
        super().__init__()
        self.add_item(ItemDropdown(bot, user_id, items))

def setup(bot):
    bot.add_cog(Shop(bot))