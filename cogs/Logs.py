import disnake
from disnake.ext import commands
from datetime import datetime

LOG_CHANNEL = 1266776037862412338

class Logs(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member):
        channel = self.bot.get_channel(LOG_CHANNEL)
        join_time = datetime.now().strftime('%d.%m.%Y в %H:%M')
        if channel:
            embed = disnake.Embed(
                title=None,
                description=f'{member.mention} зашел на сервер.',
                color=disnake.Color.green()
            )
            embed.set_footer(text=f'Id участника: {member.id} • {join_time}')
            await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        channel = self.bot.get_channel(LOG_CHANNEL)
        leave_time = datetime.now().strftime('%d.%m.%Y в %H:%M')
        if channel:
            embed = disnake.Embed(
                title=None,
                description=f'{member.mention} покинул сервер.',
                color=disnake.Color.red()
            )
            embed.set_footer(text=f'Id участника: {member.id} • {leave_time}')
            await channel.send(embed=embed)

def setup(bot):
    bot.add_cog(Logs(bot))