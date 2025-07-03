import disnake
from disnake.ext import commands
from datetime import *
import asyncio
import io

LOG_CHANNEL = 1390278452250411088

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
        elif not before.guild:
            return
        elif before.type != disnake.MessageType.default:
            return 
        elif before.content == after.content:
            return
        
        if before.attachments:
            before_attachments = '\n'.join(attachment.url for attachment in before.attachments)
        else:
            before_attachments = 'Вложений нет.'

        if after.attachments:
            after_attachments = "\n".join(attachment.url for attachment in after.attachments)
        else:
            after_attachments = 'Вложений нет.'
        
        embed = disnake.Embed(
            title=None,
            description=f'[Сообщение]({after.jump_url}) было отредактировано',
            color=disnake.Color.yellow()
        )
        embed.add_field(name='Старое сообщение:', value=f'```{before.content}```' or '```None```', inline=False)
        embed.add_field(name='Новое сообщение:', value=f'```{after.content}```' or '```None```', inline=False)
        embed.add_field(name='Канал:', value=after.channel.mention, inline=False)
        embed.add_field(name='Вложения до редактирования:', value=before_attachments, inline=False)
        embed.add_field(name='Вложения после редактирования:', value=after_attachments, inline=False)
        embed.set_author(name=after.author.display_name, icon_url=after.author.display_avatar.url)
        embed.set_footer(text=f'ID сообщения: {after.id} • {edit_time}')
        await channel.send(embed=embed)
    
    @commands.Cog.listener()
    async def on_message_delete(self, message):
        channel = self.bot.get_channel(LOG_CHANNEL)
        delete_time = datetime.now().strftime('%d.%m.%Y в %H:%M')

        if message.author.bot:
            return
        if not message.guild:
            return
        if message.type != disnake.MessageType.default:
            return

        if message.attachments:
            message_attachments = '\n'.join(attachment.url for attachment in message.attachments)
        else:
            message_attachments = 'Вложений нет.'

        embed = disnake.Embed(
            title=None,
            description=f'Сообщение было удалено',
            color=disnake.Color.red()
        )
        embed.add_field(name='Текст сообщения:', value=f'```{message.content}```', inline=False)
        embed.add_field(name='Канал:', value=message.channel.mention, inline=False)
        embed.add_field(name='Вложения:', value=message_attachments, inline=False)
        embed.set_author(name=message.author.display_name, icon_url=message.author.display_avatar.url)
        embed.set_footer(text=f'Время удаления • {delete_time}')
        await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        channel = self.bot.get_channel(LOG_CHANNEL)
        message_time = datetime.now().strftime('%d.%m.%Y в %H:%M')
         
        if before.channel == after.channel:
            return
        
        if not before.channel and after.channel:
            embed = disnake.Embed(
                title=None,
                description=f'{member.mention} зашел в голосовой канал {after.channel.mention}',
                color=disnake.Color.dark_green()
            )
            embed.set_author(name=member.display_name, icon_url=member.display_avatar.url)
            embed.set_footer(text=f'ID: {member.id} • {message_time}')
            await channel.send(embed=embed)
        elif before.channel and not after.channel:
            embed = disnake.Embed(
                description=f'{member.mention} вышел из голосового канала {before.channel.mention}',
                color=disnake.Color.dark_red()
            )
            embed.set_author(name=member.display_name, icon_url=member.display_avatar.url)
            embed.set_footer(text=f'ID: {member.id} • {message_time}')
            await channel.send(embed=embed)
        elif before.channel != after.channel:
            embed = disnake.Embed(
                description=f'{member.mention} перешел из {before.channel.mention} в {after.channel.mention}',
                color=disnake.Color.dark_orange()
            )
            embed.set_author(name=member.display_name, icon_url=member.display_avatar.url)
            embed.set_footer(text=f'ID: {member.id} • {message_time}')
            await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        channel = self.bot.get_channel(LOG_CHANNEL)
        message_time = datetime.now().strftime('%d.%m.%Y в %H:%M')

        if not channel:
            return

        embed = disnake.Embed(
            title='Изменение профиля участника',
            description=None,
            color=disnake.Color.blurple()
        )
        embed.set_author(name=after.display_name, icon_url=after.display_avatar.url)
        embed.set_footer(text=f'ID: {after.id} • {message_time}')

        changes = False

        if before.nick != after.nick:
            embed.add_field(
                name='Ник на сервере изменён:',
                value=f'До: ```{before.nick or "Отсутствовал"}```\nПосле: ```{after.nick or "Отсутствует"}```',
                inline=False
            )
            changes = True


        if before.roles != after.roles:
            added = [r.mention for r in after.roles if r not in before.roles]
            removed = [r.mention for r in before.roles if r not in after.roles]
            if added:
                embed.add_field(name='Добавлены роли:', value=', '.join(added), inline=False)
            if removed:
                embed.add_field(name='Удалены роли:', value=', '.join(removed), inline=False)
            changes = True

            await asyncio.sleep(1) 
            async for entry in after.guild.audit_logs(limit=5, action=disnake.AuditLogAction.member_role_update):
                if entry.target.id == after.id:
                    embed.add_field(name='Кто изменил:', value=f'{entry.user.mention}', inline=False)
                    break

        if before.premium_since != after.premium_since:
            if after.premium_since:
                embed.add_field(name='Буст!', value=f'{after.mention} начал бустить сервер 🎉', inline=False)
            else:
                embed.add_field(name='Буст снят', value=f'{after.mention} больше не бустит сервер 💔', inline=False)
            changes = True

        if changes:
            await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_user_update(self, before, after):
        channel = self.bot.get_channel(LOG_CHANNEL)
        message_time = datetime.now().strftime('%d.%m.%Y в %H:%M')

        if not channel:
            return

        embed = disnake.Embed(
            title='Изменение профиля участника',
            description=None,
            color=disnake.Color.blue()
        )
        embed.set_author(name=after.name, icon_url=before.display_avatar.url)
        embed.set_footer(text=f'ID: {after.id} • {message_time}')
        
        changes = False
        
        if before.avatar.url != after.avatar.url:
            embed.set_thumbnail(url=after.avatar.url)
            embed.add_field(name='Аватар изменён', value=f'{after.mention} изменил аватар, поздравим его!', inline=False)
            changes = True

        if changes:
            await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_bulk_message_delete(self, messages):
        channel = self.bot.get_channel(LOG_CHANNEL)
        message_time = datetime.now().strftime('%d.%m.%Y в %H:%M')

        if not channel:
            return

        sorted_messages = sorted(messages, key=lambda m: m.created_at)

        log_lines = []
        for message in sorted_messages:
            timestamp = message.created_at.strftime("[%b %d, %Y, %H:%M:%S]")
            author = f"{message.author} ({message.author.display_name}):"
            content = message.content if message.content else ""
            log_lines.append(f"{timestamp} {author} {content}")

        log_text = '\n'.join(log_lines)
        log_file = disnake.File(
            io.BytesIO(log_text.encode("utf-8")),
            filename=f"{messages[0].channel.id}.log"
        )

        embed = disnake.Embed(
            title=None,
            description=f'Очищено **{len(messages)}** сообщений\n**Канал:** {messages[0].channel.mention}',
            color=disnake.Color.red()
        )
        embed.set_footer(text=f"{message_time}")
        await channel.send(embed=embed, file=log_file)

def setup(bot):
    bot.add_cog(Logs(bot))