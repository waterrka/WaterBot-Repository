import os
import disnake
from disnake.ext import commands
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv('API_KEY')
MODERATOR = 1266812096209879123
CHANNEL_ID = 1277290799239004230

bot = commands.Bot(
    command_prefix='/',
    help_command=None,
    intents=disnake.Intents.all(),
    test_guilds=[1266770954806235220]
)

@bot.event
async def on_ready():
    print(f'{bot.user.name} готов к работе!')
    activity = disnake.Activity(type=disnake.ActivityType.watching, name='boosty.to/waterrka')
    await bot.change_presence(activity=activity)
    channel = bot.get_channel(CHANNEL_ID)
    embed = disnake.Embed(
        title='Бот онлайн!',
        description=None,
        color=0xFFFFFF
    )
    await channel.send(embed=embed)

@bot.slash_command(description='DEV ONLY')
@commands.has_permissions(administrator=True)
@commands.has_role(MODERATOR)
async def load(ctx: disnake.ApplicationCommandInteraction, module: str = commands.Param(name='module', description='Выберите модуль', choices=['Other', 'Economy', 'Moderator', 'Shop', 'Tickets', 'Gemini', 'Logs'])):
    ext_name = f'cogs.{module}'
    if ext_name in bot.extensions.keys():
        embed = disnake.Embed(
            title='Load Extension',
            description=f'⚠️ {module} уже загружен.',
            color=0xFFFFFF
        )
    else:
        bot.load_extension(f'cogs.{module}')
        embed = disnake.Embed(
            title='Load Extension',
            description=f'✅ {module} успешно загружен!',
            color=0xFFFFFF
        )
    await ctx.send(embed=embed)

@bot.slash_command(description='DEV ONLY')
@commands.has_permissions(administrator=True)
@commands.has_role(MODERATOR)
async def unload(ctx: disnake.ApplicationCommandInteraction, module: str = commands.Param(name='module', description='Выберите модуль', choices=['Other', 'Economy', 'Moderator', 'Shop', 'Tickets', 'Gemini', 'Logs'])):
    ext_name = f'cogs.{module}'
    if ext_name not in bot.extensions.keys():
        embed = disnake.Embed(
            title='Unload Extension',
            description=f'⚠️ {module} уже выгружен.',
            color=0xFFFFFF
        )
    else:
        bot.unload_extension(f'cogs.{module}')
        embed = disnake.Embed(
            title='Unload Extension',
            description=f'✅ {module} успешно выгружен!',
            color=0xFFFFFF
        )
    await ctx.send(embed=embed)

@bot.slash_command(description='DEV ONLY')
@commands.has_permissions(administrator=True)
@commands.has_role(MODERATOR)
async def reload(ctx: disnake.ApplicationCommandInteraction, module: str = commands.Param(name='module', description='Выберите модуль', choices=['Other', 'Economy', 'Moderator', 'Shop', 'Tickets', 'Gemini', 'Logs'])):
    bot.reload_extension(f'cogs.{module}')
    embed = disnake.Embed(
        title='Reload Extension',
        description=f'🔄 {module} успешно перезагружен!',
        color=0xFFFFFF
    )
    await ctx.send(embed=embed)

for filename in os.listdir('cogs'):
    if filename.endswith('.py'):
        bot.load_extension(f'cogs.{filename[:-3]}')

bot.run(API_KEY)