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

@bot.command(name='load')
@commands.has_permissions(administrator=True)
async def load_module(ctx, module: str):
    ext_name = f'cogs.{module}'
    if ext_name in bot.extensions:
        await ctx.send(f'⚠️ Модуль `{module}` уже загружен.')
    else:
        try:
            bot.load_extension(ext_name)
            await ctx.send(f'✅ Модуль `{module}` успешно загружен!')
        except Exception as e:
            await ctx.send(f'❌ Ошибка при загрузке модуля `{module}`:\n```{e}```')

@bot.command(name='unload')
@commands.has_permissions(administrator=True)
async def unload_module(ctx, module: str):
    ext_name = f'cogs.{module}'
    if ext_name not in bot.extensions:
        await ctx.send(f'⚠️ Модуль `{module}` уже выгружен.')
    else:
        try:
            bot.unload_extension(ext_name)
            await ctx.send(f'✅ Модуль `{module}` успешно выгружен!')
        except Exception as e:
            await ctx.send(f'❌ Ошибка при выгрузке модуля `{module}`:\n```{e}```')

@bot.command(name='reload')
@commands.has_permissions(administrator=True)
async def reload_module(ctx, module: str):
    ext_name = f'cogs.{module}'
    try:
        bot.reload_extension(ext_name)
        await ctx.send(f'🔄 Модуль `{module}` успешно перезагружен!')
    except Exception as e:
        await ctx.send(f'❌ Ошибка при перезагрузке модуля `{module}`:\n```{e}```')

for filename in os.listdir('cogs'):
    if filename.endswith('.py'):
        try:
            bot.load_extension(f'cogs.{filename[:-3]}')
        except Exception as e:
            print(f'Ошибка загрузки {filename}: {e}')

bot.run(API_KEY)