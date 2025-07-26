import disnake
from disnake.ext import commands
from datetime import *

class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(description='Помощь по боту')
    async def help(self, ctx):
        embed = disnake.Embed(
            title='📖 Помощь по командам',
            description='Вы можете получить детальную справку по каждой команде, выбрав категорию ниже:',
            color=0xFFFFFF
        )
        embed.add_field(name='📋 Информация', value='</help:1398610090369749032> </server_info:1378800253754671247> </boosty_info:1378800253754671251>', inline=False)
        embed.add_field(name='🛡️ Модерирование', value='</mute:1378800252924198979> </unmute:1378800252924198980> </ban:1378800252924198981> </unban:1378800252924198982> </warn:1378800252924198983> </rewarn:1378800253330784427> </clear:1378800252924198978> </warns:1378800253330784430>', inline=False)
        embed.add_field(name='🎲 Экономика', value='</balance:1398194417528995951> </work:1398194417528995952> </collect:1398194417528995953> </list_collect:1398194417969533040> </leaderboard:1398194417969533041> </pay:1398194417969533042> </roullete:1398194417969533047> </russian_roulette:1398194417969533048> </slots:1398194417969533046>', inline=False)
        embed.add_field(name='ℹ️ Прочее', value='</avatar:1378800253754671248> </emoji:1378800253754671249> </ping:1378800253754671246>', inline=False)
        embed.set_footer(
            text=f'{self.bot.user.name} ・ {datetime.now().strftime("%d.%m.%Y %H:%M")}',
            icon_url=self.bot.user.display_avatar.url
        )
        embed.set_thumbnail(url=ctx.bot.user.display_avatar.url)
        await ctx.response.send_message(embed=embed, view=HelpView())

class HelpDropdown(disnake.ui.Select):
    def __init__(self):
        options = [
            disnake.SelectOption(label='Информация', description='Команды для информации', emoji='📋'),
            disnake.SelectOption(label='Модерирование', description='Команды для модерации', emoji='🛡️'),
            disnake.SelectOption(label='Экономика', description='Команды экономики и игр', emoji='🎲'),
            disnake.SelectOption(label='Прочее', description='Прочие команды', emoji='ℹ️'),
        ]
        super().__init__(placeholder='Выберите категорию...', min_values=1, max_values=1, options=options)

    async def callback(self, ctx: disnake.MessageInteraction):
        category = self.values[0]
        embed = disnake.Embed(color=0xFFFFFF)

        if category == 'Информация':
            embed.title = 'Доступные команды для Информация 📋'
            embed.description = (
                '**/help**\nПоказать меню помощи\n'
                '**/server_info**\nИнформация о сервере\n'
                '**/boosty_info**\nПоддержать бота на Boosty'
            )
        elif category == 'Модерирование':
            embed.title = 'Доступные команды для Модерирование 🛡️'
            embed.description = (
                '**/mute**\nЗаглушить участника\n'
                '**/unmute**\nСнять заглушение\n'
                '**/ban**\nЗабанить участника\n'
                '**/unban**\nРазбанить участника\n'
                '**/warn**\nВыдать предупреждение\n'
                '**/rewarn**\nУдалить предупреждение\n'
                '**/clear**\nОчистить сообщения\n'
                '**/warns**\nПоказать предупреждения участника'
            )
        elif category == 'Экономика':
            embed.title = 'Доступные команды для Экономика 🎲'
            embed.description = (
                '**/balance**\nПоказать баланс\n'
                '**/work**\nЗаработать деньги\n'
                '**/collect**\nПолучить пассивный доход\n'
                '**/list_collect**\nСписок пассивного дохода\n'
                '**/leaderboard**\nТоп пользователей по балансу\n'
                '**/pay**\nПеревести деньги другому\n'
                '**/roullete**\nРулетка с шансами\n'
                '**/russian_roulette**\nРусская рулетка\n'
                '**/slots**\nИгровой автомат (слоты)'
            )
        elif category == 'Прочее':
            embed.title = 'Доступные команды для Прочее ℹ️'
            embed.description = (
                '**/avatar**\nАватар пользователя\n'
                '**/emoji**\nИнформация об эмодзи\n'
                '**/ping**\nЗадержка бота (пинг)'
            )
        embed.set_footer(
            text=f'{ctx.bot.user.name} ・ {datetime.now().strftime("%d.%m.%Y %H:%M")}',
            icon_url=ctx.bot.user.display_avatar.url
        )
        embed.set_thumbnail(url=ctx.bot.user.display_avatar.url)
        await ctx.response.send_message(embed=embed, ephemeral=True)

class HelpView(disnake.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(HelpDropdown())

def setup(bot):
    bot.add_cog(Help(bot))