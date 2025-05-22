import disnake
from disnake.ext import commands

BOTOVOD = 1276916412547338303

class EconomyModeration(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.economy = self.bot.get_cog('Economy')

    @commands.slash_command(description='Добавить деньги пользователю')
    @commands.has_any_role(BOTOVOD)
    async def add(self, ctx, member: disnake.Member, amount: int):
        self.economy.update_balance(member.id, amount)
        embed = disnake.Embed(
            title='Баланс обновлен',
            description=f'{ctx.author.mention} добавил {amount}📼 к балансу {member.mention}.',
            color=0xFFFFFF
        )
        await ctx.response.send_message(embed=embed)

    @commands.slash_command(description='Удалить деньги у пользователя')
    @commands.has_any_role(BOTOVOD)
    async def remove(self, ctx, member: disnake.Member, amount: int):
        self.economy.update_balance(member.id, -amount)
        embed = disnake.Embed(
            title='Баланс обновлен',
            description=f'{ctx.author.mention} удалил {amount}📼 с баланса {member.mention}.',
            color=0xFFFFFF
        )
        await ctx.response.send_message(embed=embed)

    @commands.slash_command(description='ПЛАТИ НАЛОГ')
    @commands.has_any_role(BOTOVOD)
    async def nalog(self, ctx, percent: int):
        members = self.economy.get_all_users()
        total_collected = 0
        percent = percent / 100
        for user in members:
            balance = self.economy.get_balance(user)
            nalog_amount = int(balance * percent)
            self.economy.update_balance(user, -nalog_amount)
            total_collected += nalog_amount

        embed = disnake.Embed(
            title='Налоговое взыскание завершено',
            description=f'Со всех пользователей собрано:\n```{total_collected}📼```',
            color=0xFFFFFF
        )
        await ctx.response.send_message(embed=embed)
        self.economy.update_balance(ctx.author.id, total_collected)

    @add.error
    @remove.error
    @nalog.error
    async def moderation_error(self, ctx, error):
        if isinstance(error, commands.MissingAnyRole):
            embed = disnake.Embed(
                title='Ошибка',
                description='У вас нет нужной роли для использования этой команды.',
                color=0xFFFFFF
            )
            await ctx.response.send_message(embed=embed, ephemeral=True)

        elif isinstance(error, commands.MissingPermissions):
            embed = disnake.Embed(
                title='Ошибка',
                description='У вас нет нужных прав для использования этой команды.',
                color=0xFFFFFF
            )
            await ctx.response.send_message(embed=embed, ephemeral=True)

def setup(bot):
    bot.add_cog(EconomyModeration(bot))