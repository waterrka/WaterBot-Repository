import importlib
import disnake
from disnake.ext import commands
import random
import time
import sqlite3
from disnake.ui import Button, View
import cogs.economy.EconomyGames as EconomyGames
import cogs.economy.EconomyModeration as EconomyModeration

conn = sqlite3.connect('inventory.db')
cursor = conn.cursor()

WORK_COOLDOWN = commands.CooldownMapping.from_cooldown(1, 14400, commands.BucketType.user)
COLLECT_COOLDOWN = commands.CooldownMapping.from_cooldown(1, 86400, commands.BucketType.user)

ROLE_EARNINGS = {
    1271408406938386474: {
        "min": -5,
        "max": -5,
        "name": "пред-1",
        "negative": True
    },
    1271408553890156564: {
        "min": -10,
        "max": -10,
        "name": "пред-2",
        "negative": True
    },
    1271408682101510205: {
        "min": -15,
        "max": -15,
        "name": "пред-3",
        "negative": True
    },
    1271121264051752990: {
        "min": 5,
        "max": 5,
        "name": "оповещение изменений",
        "negative": False
    },
    1266857840732143697: {
        "min": 15,
        "max": 15,
        "name": "Владелец блога",
        "negative": False
    },
    1267517777904668712: {
        "min": 15,
        "max": 20,
        "name": "Ивент-менеджер",
        "negative": False
    },
    1371104857775411251: {
        "min": 20,
        "max": 30,
        "name": "Важный гость",
        "negative": False
    },
    1266859426707538041: {
        "min": 30,
        "max": 30,
        "name": "Крутышка",
        "negative": False
    },
    1266855152900509788: {
        "min": 25,
        "max": 25,
        "name": "Tiny Games Studio Team",
        "negative": False
    },
    1266805974585446506: {
        "min": 30,
        "max": 40,
        "name": "Хелперы",
        "negative": False
    },
    1266812096209879123: {
        "min": 40,
        "max": 60,
        "name": "Модерация",
        "negative": False
    },
    1278746179206910053: {
        "min": 40,
        "max": 60,
        "name": "Капиталист",
        "negative": False
    },
    1266856249559879713: {
        "min": 30,
        "max": 40,
        "name": "Sponsor",
        "negative": False
    },
    1270702225370382346: {
        "min": 30,
        "max": 40,
        "name": "Booster",
        "negative": False
    },
    1371105600204701829: {
        "min": 70,
        "max": 100,
        "name": "Повелитель экономики",
        "negative": False
    },
    1371105600204701829: {
        "min": 500,
        "max": 500,
        "name": "хэппи берсдэй",
        "negative": False
    }
}

OWNER_ID = 679722204144992262

class LeaderboardView(View):
    def __init__(self, bot, leaderboard_command, page):
        super().__init__(timeout=300)  # тайм-аут 5 минут
        self.bot = bot
        self.leaderboard_command = leaderboard_command
        self.page = page

    @disnake.ui.button(label="<", style=disnake.ButtonStyle.blurple, disabled=True, custom_id="prev_page")
    async def prev_page(self, button: Button, inter: disnake.Interaction):
        if self.page > 1:
            self.page -= 1
            await self.update_message(inter)

    @disnake.ui.button(label=">", style=disnake.ButtonStyle.blurple, custom_id="next_page")
    async def next_page(self, button: Button, inter: disnake.Interaction):
        if self.page < self.total_pages:
            self.page += 1
            await self.update_message(inter)

    async def update_message(self, interaction: disnake.Interaction):
        embed, total_pages = await self.leaderboard_command.show_leaderboard(interaction, self.page)
        self.total_pages = total_pages
        self.children[0].disabled = (self.page == 1)
        self.children[1].disabled = (self.page == self.total_pages)
        await interaction.response.edit_message(embed=embed, view=self)

    async def on_timeout(self):
        self.stop()
        for button in self.children:
            button.disabled = True
        if self.message:
            await self.message.edit(view=self)

class Economy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = sqlite3.connect('economy.db')
        self.cursor = self.db.cursor()

        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS balances (
            user_id INTEGER PRIMARY KEY,
            balance INTEGER NOT NULL DEFAULT 0
        )
        ''')

        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS leaderboard (
            user_id INTEGER PRIMARY KEY,
            balance INTEGER NOT NULL DEFAULT 0,
            rank INTEGER
        )
        ''')
        self.db.commit()

    def format_balance(self, balance):
        if balance == float('inf'):
            return "∞📼"
        return f"{balance}📼"

    def get_balance(self, user_id: int):
        if user_id == OWNER_ID:
            return float('inf')
        
        self.cursor.execute("SELECT balance FROM balances WHERE user_id = ?", (user_id,))
        result = self.cursor.fetchone()
        if result:
            return result[0]
        return 0

    def update_balance(self, user_id: int, amount: int):
        if user_id == OWNER_ID:
            return float('inf')
    
        current_balance = self.get_balance(user_id)
        new_balance = max(current_balance + amount, 0)

        self.cursor.execute("INSERT OR REPLACE INTO balances (user_id, balance) VALUES (?, ?)", (user_id, new_balance))
        self.db.commit()
        return new_balance

    def get_all_users(self):
        self.cursor.execute("SELECT user_id FROM balances WHERE user_id != ?", (OWNER_ID,))
        return [row[0] for row in self.cursor.fetchall()]
    
    @commands.slash_command(description='Баланс пользователя')
    async def balance(self, ctx, member: disnake.Member = None):
        if member is None:
            member = ctx.author

        balance = self.get_balance(member.id)

        if balance == float('inf'):
            balance_display = "∞📼"
        else:
            balance_display = f"{balance}📼"
        
        embed = disnake.Embed(
            title=f'Баланс пользователя - {member.name}',
            description=f'### 📼Кассеты\n```{balance_display}```',
            color=0xFFFFFF
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        await ctx.response.send_message(embed=embed)

    @commands.slash_command(description='Работааать')
    async def work(self, ctx):
        bucket = WORK_COOLDOWN.get_bucket(ctx)
        retry_after = bucket.update_rate_limit()
        if retry_after:
            retry_time = int(time.time() + retry_after)
            time_left = f'<t:{retry_time}:R>'
            
            embed = disnake.Embed(
                title='Ожидание',
                description=f'Вы сможете использовать /work {time_left}.',
                color=0xFFFFFF
            )
            embed.set_thumbnail(url=ctx.author.display_avatar.url)
            await ctx.response.send_message(embed=embed, ephemeral=True)
            return
        
        earnings = random.randint(30, 60)
        self.update_balance(ctx.author.id, earnings)
        
        embed = disnake.Embed(
            title='Работа',
            description=f'Вы заработали {earnings}📼',
            color=0xFFFFFF
        )
        embed.set_thumbnail(url=ctx.author.display_avatar.url)
        await ctx.response.send_message(embed=embed)
    
    @commands.slash_command(description='Собрать урожай')
    async def collect(self, ctx):
        earning_roles = []
        total_earnings = 0

        for role in ctx.author.roles:
            if role.id in ROLE_EARNINGS:
                data = ROLE_EARNINGS[role.id]
                earning = random.randint(data["min"], data["max"])
                earning_roles.append((role, earning))
                total_earnings += earning

        earning_roles.sort(key=lambda x: x[1], reverse=True)

        bucket = COLLECT_COOLDOWN.get_bucket(ctx)
        retry_after = bucket.update_rate_limit()
        if retry_after:
            retry_time = int(time.time() + retry_after)
            time_left = f'<t:{retry_time}:R>'
            
            embed = disnake.Embed(
                title='Ожидание',
                description=f'Вы сможете использовать /collect {time_left}.',
                color=0xFFFFFF
            )
            embed.set_thumbnail(url=ctx.author.display_avatar.url)
            await ctx.response.send_message(embed=embed, ephemeral=True)
            return

        if total_earnings == 0:
            embed = disnake.Embed(
                title='Доход ролей',
                description=f'Вы собрали: {total_earnings}📼',
                color=0xFFFFFF
            )
            embed.set_thumbnail(url=ctx.author.display_avatar.url)
            await ctx.response.send_message(embed=embed)
            return
        
        self.update_balance(ctx.author.id, total_earnings)
        
        description_lines = [f'**Общий заработок: {total_earnings}📼**']
        if earning_roles:
            description_lines.append("\n**Доход от ролей:**")
            for role, earning in earning_roles:
                description_lines.append(f'{role.mention} | {earning}📼')

        embed = disnake.Embed(
            title='Доход ролей',
            description='\n'.join(description_lines),
            color=0xFFFFFF
        )
        embed.set_thumbnail(url=ctx.author.display_avatar.url)
        await ctx.response.send_message(embed=embed)

    @commands.slash_command(description='Доход ролей')
    async def list_collect(self, ctx):
        description_lines = ["**Роли:**"]

        for role_id, info in ROLE_EARNINGS.items():
            role = ctx.guild.get_role(role_id)
            if role:
                if info["min"] == info["max"]:
                    earning_text = f"{info['min']}📼"
                else:
                    earning_text = f"{info['min']}–{info['max']}📼"
                description_lines.append(f'{role.mention} | {earning_text}')

        embed = disnake.Embed(
            title='Заработок ролей',
            description='\n'.join(description_lines) if description_lines else 'Нет данных.',
            color=0xFFFFFF
        )
        embed.set_thumbnail(url=ctx.author.display_avatar.url)
        await ctx.response.send_message(embed=embed)

    @commands.slash_command(description='Показать лидерборд пользователей по балансу')
    async def leaderboard(self, ctx):
        embed, total_pages = await self.show_leaderboard(ctx, 1)
        view = LeaderboardView(self.bot, self, 1)
        view.total_pages = total_pages
        await ctx.response.send_message(embed=embed, view=view)

    async def show_leaderboard(self, ctx, page):
        self.cursor.execute("SELECT user_id, balance FROM balances WHERE user_id != ? ORDER BY balance DESC", (OWNER_ID,))
        all_users = self.cursor.fetchall()
        
        total_pages = (len(all_users) + 9) // 10
        page = max(1, min(page, total_pages)) 
        start_index = (page - 1) * 10
        end_index = start_index + 10
        page_users = all_users[start_index:end_index]

        embed = disnake.Embed(
            title='📼 Топ пользователей по балансу',
            color=0xFFFFFF
        )

        for index, (user_id, balance) in enumerate(page_users, start=start_index + 1):
            member = ctx.guild.get_member(user_id)
            if member:
                name = member.display_name
            else:
                name = f'<@{user_id}>'
            embed.add_field(
                name=f'{index}. {name}',
                value=f'```{balance}📼```',
                inline=False
            )

        embed.set_footer(text=f'Страница {page}/{total_pages}')
        return embed, total_pages
    
    @commands.slash_command(description='Перевести деньги пользователю')
    async def pay(self, ctx, member: disnake.Member, amount: int):
        if amount <= 0:
            embed = disnake.Embed(
                title='Ошибка',
                description='Сумма должна быть больше 0.',
                color=0xFFFFFF
            )
            embed.set_thumbnail(url=ctx.author.display_avatar.url)
            await ctx.response.send_message(embed=embed, ephemeral=True)
            return
    
        user_balance = self.get_balance(ctx.author.id)
        if user_balance < amount:
            embed = disnake.Embed(
                title='Ошибка',
                description='У вас недостаточно средств.',
                color=0xFFFFFF
            )
            embed.set_thumbnail(url=ctx.author.display_avatar.url)
            await ctx.response.send_message(embed=embed, ephemeral=True)
            return
        
        self.update_balance(ctx.author.id, -amount)
        self.update_balance(member.id, amount)

        embed = disnake.Embed(
            title=None,
            description=f'Вы перевели {amount}📼 пользователю {member.mention}.',
            color=0xFFFFFF
        )
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.display_avatar.url)
        await ctx.response.send_message(embed=embed)
    
def setup(bot: commands.Bot):
    importlib.reload(EconomyModeration)
    importlib.reload(EconomyGames)
    bot.add_cog(Economy(bot))
    bot.add_cog(EconomyModeration.EconomyModeration(bot))
    bot.add_cog(EconomyGames.EconomyGames(bot))

def teardown(bot: commands.Bot):
    bot.remove_cog('Economy')
    bot.remove_cog('EconomyModeration')
    bot.remove_cog('EconomyGames')