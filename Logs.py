import disnake
from disnake.ext import commands
from datetime import datetime

LOG_CHANNEL = 1266776037862412338

class Logs(commands.cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member):
        channel = self.bot.get_channel(LOG_CHANNEL)
        join_time = datetime.now().strftime('%d.%m.%Y в %H:%M')
        if channel:
            embed = disnake.Embed(
                title='Новый участник!',
                description=f'{member.mention} зашел на сервер.',
                color=disnake.Color.green()
            )
            embed.set_footer(f'Id участника: {member.id} • {join_time}')
            await channel.send(embed=embed)

def setup(bot):
    bot.add_cog(Logs(bot))