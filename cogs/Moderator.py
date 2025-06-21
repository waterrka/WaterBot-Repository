import disnake
from disnake.ext import commands
from datetime import *
from disnake.ui import Button, View
import sqlite3

conn = sqlite3.connect("warns.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS warns (
    guild_id INTEGER,
    user_id INTEGER,
    warns INTEGER,
    PRIMARY KEY (guild_id, user_id)
)
""")

conn.commit()
conn.close()

MODERATORS = [1266823503823241299, 1266812096209879123]
HELPERS = [1266805974585446506]
LOG_CHANNEL = 1266798131337498665
WARN_ROLES = [1271408406938386474, 1271408553890156564, 1271408682101510205]

class LeaderboardView(View):
    def __init__(self, bot, leaderboard_command, page, leaderboard_type):
        super().__init__(timeout=300)  # тайм-аут 5 минут
        self.bot = bot
        self.leaderboard_command = leaderboard_command
        self.page = page
        self.leaderboard_type = leaderboard_type 
        self.total_pages = 1
        self.message = None

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
        if self.leaderboard_type == 'warns':
            embed, total_pages = await self.leaderboard_command.show_warns_leaderboard(interaction, self.page)
        else:
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

class Moderator(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def get_warns(self, guild_id, user_id):
        with sqlite3.connect("warns.db") as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT warns FROM warns WHERE guild_id=? AND user_id=?", (guild_id, user_id))
            row = cursor.fetchone()
            return row[0] if row else 0

    def set_warns(self, guild_id, user_id, warns):
        with sqlite3.connect("warns.db") as conn:
            cursor = conn.cursor()
            if warns > 0:
                cursor.execute("REPLACE INTO warns (guild_id, user_id, warns) VALUES (?, ?, ?)", (guild_id, user_id, warns))
            else:
                cursor.execute("DELETE FROM warns WHERE guild_id=? AND user_id=?", (guild_id, user_id))
            conn.commit()

    def get_all_warns(self, guild_id):
        with sqlite3.connect("warns.db") as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT user_id, warns FROM warns WHERE guild_id=? ORDER BY warns DESC", (guild_id,))
            return cursor.fetchall()
        
    def embed_message(self, ctx, member, reason, action_title):
        embed = disnake.Embed(
            description=(
                f'**Модератор:** {ctx.author.mention}\n'
                f'**Пользователь:** {member.mention}\n'
                f'**Причина:**\n```\n{reason}\n```'
            ),
            color=0xFFFFFF
        )
        embed.set_author(
            name=action_title,
            icon_url=member.display_avatar.url
        )
        embed.set_footer(
            text=f'{self.bot.user.name} ・ {datetime.now().strftime("%d.%m.%Y %H:%M")}',
            icon_url=self.bot.user.display_avatar.url
        )
        return embed

    @commands.slash_command(description='Очистить сообщения в чате')
    @commands.has_any_role(*(MODERATORS + HELPERS))
    async def clear(self, ctx, count: int, member: disnake.Member = None):
        if count <= 0:
            embed = disnake.Embed(
                title='Ошибка',
                description='Укажите положительное количество сообщений для удаления.',
                color=0xFFFFFF
            )
            await ctx.response.send_message(embed=embed, ephemeral=True)
            return

        def check_message(message):
            return message.author == member if member else True

        deleted = await ctx.channel.purge(limit=count, check=check_message)

        embed = disnake.Embed(
            title='Очистка сообщений',
            description=f'Удалено **{len(deleted)}** сообщений.',
            color=0xFFFFFF
        )
        embed.set_footer(
            text=f'{self.bot.user.name} ・ {datetime.now().strftime("%d.%m.%Y %H:%M")}',
            icon_url=self.bot.user.display_avatar.url
        )
        await ctx.response.send_message(embed=embed)

    @commands.slash_command(description='Замутить пользователя')
    @commands.has_any_role(*(MODERATORS + HELPERS))
    async def mute(self, ctx, member: disnake.Member, time: str, reason: str):
        time_multiplier = {'h': 3600, 'd': 86400}
        time_suffix = time[-1]
        if time_suffix not in time_multiplier or not time[:-1].isdigit():
            embed = disnake.Embed(
                title='Ошибка',
                description='Неверный формат времени. Пример: "1h", "2d".',
                color=0xFFFFFF
            )
            await ctx.response.send_message(embed=embed, ephemeral=True)
            return

        duration = int(time[:-1]) * time_multiplier[time_suffix]
        await member.timeout(duration=timedelta(seconds=duration), reason=reason)

        log_embed = self.embed_message(ctx, member, reason, f'{member.display_name} замучен на {time}')

        log_channel = self.bot.get_channel(LOG_CHANNEL)
        if log_channel:
            await log_channel.send(embed=log_embed)

        await ctx.response.send_message(embed=disnake.Embed(
            description=f'Участник {member.mention} замучен!',
            color=0xFFFFFF
        ), ephemeral=True)

    @commands.slash_command(description='Размутить пользователя')
    @commands.has_any_role(*(MODERATORS + HELPERS))
    async def unmute(self, ctx, member: disnake.Member, reason: str):
        await member.timeout(duration=None, reason=reason)

        log_embed = self.embed_message(ctx, member, reason, f'{member.display_name} размучен')
        log_channel = self.bot.get_channel(LOG_CHANNEL)
        if log_channel:
            await log_channel.send(embed=log_embed)

        await ctx.response.send_message(embed=disnake.Embed(
            description=f'Участник {member.mention} размучен!',
            color=0xFFFFFF
        ), ephemeral=True)

    @commands.slash_command(description='Забанить пользователя')
    @commands.has_any_role(*MODERATORS)
    async def ban(self, ctx, member: disnake.Member, reason: str):
        await member.ban(reason=reason)

        log_embed = self.embed_message(ctx, member, reason, f'{member.display_name} забанен')
        log_channel = self.bot.get_channel(LOG_CHANNEL)
        if log_channel:
            await log_channel.send(embed=log_embed)

        await ctx.response.send_message(embed=disnake.Embed(
            description=f'Участник {member.mention} забанен!',
            color=0xFFFFFF
        ), ephemeral=True)

    @commands.slash_command(description='Разбанить пользователя')
    @commands.has_any_role(*MODERATORS)
    async def unban(self, ctx, user_id: str, reason: str):
        user = await self.bot.fetch_user(user_id)
        await ctx.guild.unban(user, reason=reason)

        log_embed = self.embed_message(ctx, user, reason, f'{user.display_name} разбанен')
        log_channel = self.bot.get_channel(LOG_CHANNEL)
        if log_channel:
            await log_channel.send(embed=log_embed)

        await ctx.response.send_message(embed=disnake.Embed(
            description=f'Участник {user.mention} разбанен!',
            color=0xFFFFFF
        ), ephemeral=True)

    @commands.slash_command(description='Выдать варн пользователю')
    @commands.has_any_role(*(MODERATORS + HELPERS))
    async def warn(self, ctx, member: disnake.Member, reason: str):
        guild_id = ctx.guild.id
        warns = self.get_warns(guild_id, member.id) + 1
        self.set_warns(guild_id, member.id, warns)

        if warns > 3:
            await member.timeout(duration=timedelta(days=3), reason='Автоматический мут за 3+ варна')
            title = f'{member.display_name} автоматически замучен на 3 дня'
            reason = 'Превышение лимита варнов'
        else:
            await self.update_warn_roles(member)
            title = f'{member.display_name} получил варн'

        log_embed = self.embed_message(ctx, member, reason, title)
        log_embed.add_field(name='Текущий варн', value=str(f"```{warns}```"), inline=False)
        log_channel = self.bot.get_channel(LOG_CHANNEL)
        if log_channel:
            await log_channel.send(embed=log_embed)

        await ctx.response.send_message(embed=disnake.Embed(
            description=f'Участник {member.mention} получил варн!',
            color=0xFFFFFF
        ), ephemeral=True)

    @commands.slash_command(description='Снять варн')
    @commands.has_any_role(*(MODERATORS + HELPERS))
    async def rewarn(self, ctx, member: disnake.Member, reason: str):
        guild_id = ctx.guild.id

        warns = self.get_warns(guild_id, member.id)
        if warns > 0:
            warns -= 1
            self.set_warns(guild_id, member.id, warns)

            await self.update_warn_roles(member)

            log_embed = self.embed_message(ctx, member, reason, f'{member.display_name} снят варн')
            log_embed.add_field(name='Оставшиеся варны', value=str(f"```{warns}```"), inline=False)

            log_channel = self.bot.get_channel(LOG_CHANNEL)
            if log_channel:
                await log_channel.send(embed=log_embed)

            await ctx.response.send_message(embed=disnake.Embed(
                description=f'Участнику {member.mention} снят варн!',
                color=0xFFFFFF
            ), ephemeral=True)
        else:
            await ctx.response.send_message(embed=disnake.Embed(
                description=f'У {member.mention} нет варнов.',
                color=0xFFFFFF
            ), ephemeral=True)

    @commands.slash_command(description='Посмотреть лидерборд варнов')
    @commands.has_any_role(*(MODERATORS + HELPERS))
    async def warns(self, ctx):
        embed, total_pages = await self.show_warns_leaderboard(ctx, 1)
        view = LeaderboardView(self.bot, self, 1, leaderboard_type='warns')  
        view.total_pages = total_pages
        await ctx.response.send_message(embed=embed, view=view)

    async def show_warns_leaderboard(self, ctx, page):
        guild_id = ctx.guild.id
        embed = disnake.Embed(title='Лидерборд варнов:', color=0xFFFFFF)

        all_warns = self.get_all_warns(guild_id)
        if not all_warns:
            embed.description = 'Нет варнов.'
            return embed, 1

        total_pages = (len(all_warns) + 9) // 10
        start_index = (page - 1) * 10
        end_index = start_index + 10
        page_warns = all_warns[start_index:end_index]

        for index, (user_id, warn_count) in enumerate(page_warns, start=start_index + 1):
            member = ctx.guild.get_member(user_id)
            member_name = member.display_name if member else f'<@{user_id}>'
            embed.add_field(name=f'{index}. {member_name}', value=f'{warn_count} варн(ов)', inline=False)

        embed.set_footer(text=f'Страница {page}/{total_pages}')
        return embed, total_pages

    async def update_warn_roles(self, member: disnake.Member):
        warns = self.get_warns(member.guild.id, member.id)
        roles_to_add, roles_to_remove = [], []

        for i, role_id in enumerate(WARN_ROLES):
            if warns >= (i + 1) and role_id not in [r.id for r in member.roles]:
                roles_to_add.append(disnake.Object(id=role_id))
            elif warns < (i + 1) and role_id in [r.id for r in member.roles]:
                roles_to_remove.append(disnake.Object(id=role_id))

        if roles_to_add or roles_to_remove:
            await member.edit(roles=[
                r for r in member.roles if r.id not in [rm.id for rm in roles_to_remove]
            ] + roles_to_add)

    @clear.error
    @mute.error
    @unmute.error
    @ban.error
    @unban.error
    @warn.error
    @rewarn.error
    async def moderation_error(self, ctx, error):
        if isinstance(error, commands.MissingAnyRole):
            await ctx.response.send_message(embed=disnake.Embed(
                title='Ошибка',
                description='У вас нет нужной роли для этой команды.',
                color=0xFFFFFF
            ), ephemeral=True)
        elif isinstance(error, commands.MissingPermissions):
            await ctx.response.send_message(embed=disnake.Embed(
                title='Ошибка',
                description='У вас нет нужных прав для этой команды.',
                color=0xFFFFFF
            ), ephemeral=True)

def setup(bot):
    bot.add_cog(Moderator(bot))