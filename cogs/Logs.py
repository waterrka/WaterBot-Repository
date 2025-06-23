import disnake
from disnake.ext import commands
from datetime import *

LOG_CHANNEL = 1266776037862412338

class Logs(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member):
        channel = self.bot.get_channel(LOG_CHANNEL)
        join_time = datetime.now().strftime('%d.%m.%Y в %H:%M')
        if channel:
            if member.created_at:
                created_at = (member.created_at.strftime('%d.%m.%Y в %H:%M'))
                created_info = created_at
            else:
                created_info = 'Неизвестно'

            embed = disnake.Embed(
                title=None,
                description=f'{member.mention} зашел на сервер.',
                color=disnake.Color.green()
            )
            embed.add_field(name='Дата регистрации аккаунта:', value=created_info, inline=False)
            embed.set_thumbnail(url=member.display_avatar.url)
            embed.set_footer(text=f'Id участника: {member.id} • {join_time}')
            await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        channel = self.bot.get_channel(LOG_CHANNEL)
        leave_time = datetime.now().strftime('%d.%m.%Y в %H:%M')

        if channel:
            roles = [role.mention for role in member.roles if role != member.guild.default_role]
            roles_info = ', '.join(roles) if roles else 'Нет ролей'

            if member.joined_at:
                joined_at = member.joined_at.strftime('%d.%m.%Y в %H:%M')
                days_on_server = (datetime.utcnow() - member.joined_at.replace(tzinfo=None)).days
                joined_info = f'{joined_at} ({days_on_server} дней на сервере)'
            else:
                joined_info = 'Неизвестно'

            economy = self.bot.get_cog('Economy')
            balance = economy.get_balance(member.id)
            balance_info = "```∞📼```" if balance == float('inf') else f"```{balance}📼```"

            embed = disnake.Embed(
                title=None,
                description=f'{member.mention} покинул сервер.',
                color=disnake.Color.red()
            )
            embed.add_field(name='Присоединился:', value=joined_info, inline=False)
            embed.add_field(name='Роли:', value=roles_info, inline=False)
            embed.add_field(name='Баланс при выходе:', value=balance_info, inline=False)
            embed.set_thumbnail(url=member.display_avatar.url)
            embed.set_footer(text=f'ID участника: {member.id} • {leave_time}')
        await channel.send(embed=embed)
    
    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        channel = self.bot.get_channel(LOG_CHANNEL)
        edit_time = datetime.now().strftime('%d.%m.%Y в %H:%M')

        if after.author.bot:
            return
        elif before.content == after.content:
            return
        elif not before.guild:
            return
        
        if before.attachments:
            before_attachments = "\n".join(attachment.url for attachment in before.attachments)
        else:
            before_attachments = "Вложений нет."

        if after.attachments:
            after_attachments = "\n".join(attachment.url for attachment in after.attachments)
        else:
            after_attachments = "Вложений нет."
        
        embed = disnake.Embed(
            title=None,
            description=f'[Сообщение]({after.jump_url}) было отредактировано',
            color=disnake.Color.yellow()
        )
        embed.add_field(name='Старое сообщение:', value=f'```{before.content}```', inline=False)
        embed.add_field(name='Новое сообщение:', value=f'```{after.content}```', inline=False)
        embed.add_field(name='Канал:', value=after.channel.mention, inline=False)
        embed.add_field(name="Вложения до редактирования", value=before_attachments, inline=False)
        embed.add_field(name="Вложения после редактирования", value=after_attachments, inline=False)
        embed.set_author(name=after.author.display_name, icon_url=after.author.display_avatar.url)
        embed.set_footer(text=f'ID сообщения: {after.id} • {edit_time}')
        await channel.send(embed=embed)
    
    @commands.Cog.listener()
    async def on_message_delete(self, message):
        channel = self.bot.get_channel(LOG_CHANNEL)
        delete_time = datetime.now().strftime('%d.%m.%Y в %H:%M')

        if message.author.bot:
            return
        elif not message.guild:
            return
        
        if message.attachments:
            message_attachments = "\n".join(attachment.url for attachment in message.attachments)
        else:
            message_attachments = "Вложений нет."

        embed = disnake.Embed(
            title=None,
            description=f'Сообщение было удалено',
            color=disnake.Color.yellow()
        )
        embed.add_field(name='Текст сообщения:', value=f'```{message.content}```', inline=False)
        embed.add_field(name='Канал:', value=message.channel.mention, inline=False)
        embed.add_field(name='Вложения', value=message_attachments, inline=False)
        embed.set_author(name=message.author.display_name, icon_url=message.author.display_avatar.url)
        embed.set_footer(text=f'Время удаления • {delete_time}')
        await channel.send(embed=embed)

def setup(bot):
    bot.add_cog(Logs(bot))