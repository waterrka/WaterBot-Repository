import disnake
from disnake.ext import commands
import time
from disnake.ui import View, Button
from disnake import ButtonStyle

class Other(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(description='Справка по боту')
    async def help(self, ctx):
        embed = disnake.Embed(
            title='📖 Помощь по командам',
            description='Ниже приведён список доступных категорий команд:',
            color=0xFFFFFF
        )
        embed.add_field(name='💰 Экономика', value='`/balance`, `/work`, `/collect`, `/list_collect`, `/shop`, `/leaderboard`, `/pay`,', inline=False)
        embed.add_field(name='🎮 Казино', value='`/slots`, `/roulette`, `/russian_roulette`', inline=False)
        embed.add_field(name='🛠️ Модерация', value='`/mute`, `/unmute`, `/ban`, `/unban`, `/warn`, `/rewarn`, `/warns`', inline=False)
        embed.add_field(name='ℹ️ Прочее', value='`/help`, `/avatar`, `/emoji`, `/ping`, `/server_info`, `/boosty_info`', inline=False)
        embed.add_field(name='🤖 Эксклюзив', value='Так же у нас есть **Искуственный Интелект**, с которым можно поговорить(<пинг бота> ваш текст).', inline=False)
        embed.set_footer(text='Используй /<команда> для вызова команды.')

        await ctx.response.send_message(embed=embed)
    @commands.slash_command(description = 'Скорость отправки сообщения бота')
    async def ping(self, ctx):
        latency = round(self.bot.latency * 1000)
        embed = disnake.Embed(
            title = 'Ping',
            description = (f'🏓 Pong! Задержка: {latency}ms'),
            color = 0xFFFFFF
        )
        await ctx.response.send_message(embed=embed)
    @commands.slash_command(description = 'Информация о сервере')
    async def server_info(self, ctx):
        guild = ctx.guild
        timestamp = int(time.mktime(guild.created_at.timetuple()))

        total_members = guild.member_count
        bots_count = sum(1 for member in guild.members if member.bot)
        users_count = total_members - bots_count

        online_count = sum(1 for member in guild.members if member.status == disnake.Status.online)
        idle_count = sum(1 for member in guild.members if member.status == disnake.Status.idle)
        dnd_count = sum(1 for member in guild.members if member.status == disnake.Status.dnd)
        offline_count = total_members - (online_count + idle_count + dnd_count)

        text_channels = sum(isinstance(c, disnake.TextChannel) for c in guild.channels)
        voice_channels = sum(isinstance(c, disnake.VoiceChannel) for c in guild.channels)
        stage_channels = sum(isinstance(c, disnake.StageChannel) for c in guild.channels)
        forum_channels = sum(isinstance(c, disnake.ForumChannel) for c in guild.channels)

        total_channels = text_channels + voice_channels + stage_channels + forum_channels

        boost_count = guild.premium_subscription_count
        boost_level = guild.premium_tier

        owner_id = guild.owner
        
        embed = disnake.Embed(
            title = (f'Информация о сервере {guild.name}'),
            description = None,
            color = 0xFFFFFF,
        )

        embed.add_field(name='Участники:',
        value=(f'Всего: **{total_members}**\n'
        f'Люди: **{users_count}**\n'
        f'Боты: **{bots_count}**'),
        inline=False)

        embed.add_field(name='По статусам:', 
        value=(f'Онлайн: **{online_count}**\n'
        f'Неактивен: **{idle_count}**\n'
        f'Небеспокоить: **{dnd_count}**\n'
        f'Не в сети: **{offline_count}**\n'),
        inline=False)
        
        embed.add_field(name='Каналы:', 
        value=(f'Всего: **{total_channels}**\n'
        f'Текстовых: **{text_channels}**\n'
        f'Голосовых: **{voice_channels}**\n'
        f'Форумов: **{forum_channels}**\n'),
        inline=False)

        embed.add_field(name='Бусты сервера:', 
        value=(f'Количество бустов: **{boost_count}**\n'
        f'Уровень сервера: **{boost_level}**'),
        inline=False)

        embed.add_field(name='Владедец:', value=(f'{owner_id}'))

        embed.add_field(name='Дата создания',
        value=(f'<t:{timestamp}:D> (<t:{timestamp}:R>)'),
        inline=False)

        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)  
        else:
            embed.set_thumbnail(url='https://via.placeholder.com/128') 
        await ctx.response.send_message(embed=embed)

    @commands.slash_command(description = 'Аватар участника')
    async def avatar(self, ctx, member: disnake.Member = None):
        if member is None:
            member = ctx.author

        embed = disnake.Embed(
            title = f'Аватар участника {member}',
            description = None,
            color = 0xFFFFFF
        )

        if member.display_avatar.url:
            embed.set_image(url=member.display_avatar.url)
        else:
            embed.set_image(url='https://via.placeholder.com/128')
        await ctx.response.send_message(embed=embed)
    
    @commands.slash_command(description = 'Показать эмодзи')
    async def emoji(self, ctx, emoji: disnake.Emoji):
        embed = disnake.Embed(
            title = f'Эмоция "{emoji.name}"',
            description = None,
            color = 0xFFFFFF
        )

        if emoji.url:
            embed.set_image(url=emoji.url)
        else:
            embed.set_image(url='https://via.placeholder.com/128')
        await ctx.response.send_message(embed=embed)

    @commands.slash_command(description='DEV ONLY')
    @commands.has_permissions(administrator=True)
    async def update(self, ctx):
        embed = disnake.Embed(
            title='БОТ ВОЗВРАЩАЕТСЯ!',
            description=f'Да, спустя большое время, бот вернулся. За это время в бота добавились много новых функций, ну и конечно улучшились и другие.'
            f'Вы также можете и пообщаться с ботом, просто пинганув его и написать текст. Все команды бота доступны командой `/help`. Удачи!',
            color=0xFFFFFF
        )
        await ctx.response.send_message(embed=embed)
    
    @commands.slash_command(description='Информация о бусти waterrka')
    async def boosty_info(self, ctx):
        embed = disnake.Embed(
            title='Boosty',
            description='Boosty — это способ поддержать разработку этого Discord-бота и принять участие в его развитии.'
            ' Подписчики получают бонусы: от доступа к закрытым материалам, до возможности влиять на новые функции.'
            ' Поддержка на Boosty ускоряет разработку и открывает доступ к привилегиям.', 
            color=0xFFFFFF
        )
        view = View()
        view.add_item(Button(label='Перейти на Boosty', url='https://boosty.to/waterrka', style=ButtonStyle.link))
        await ctx.response.send_message(embed=embed, view=view)

def setup(bot):
    bot.add_cog(Other(bot))