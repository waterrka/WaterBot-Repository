import disnake
from disnake import ApplicationCommandInteraction
from disnake.ext import commands
import random
import asyncio
import json
import time
from disnake import Option

class EconomyGames(commands.Cog):
    def __init__(self, bot, interaction=disnake.ApplicationCommandInteraction):
        self.bot = bot
        self.economy = self.bot.get_cog('Economy')
        with open('./cogs/economy/slots.json', encoding='utf-8') as f:
            self.slots_cfg = json.load(f)

    def format_balance(self, amount):
        return f'```{amount}📼```'
    
    async def cog_slash_command_error(self, ctx: ApplicationCommandInteraction, error: Exception):
        if isinstance(error, disnake.ext.commands.errors.CommandOnCooldown):
            embed = disnake.Embed(
                title='Ошибка',
                description='Команда на кулдауне. Пожалуйста, подождите 5 минут.',
                color=0xFFFFFF
            )
            await ctx.response.send_message(embed=embed, ephemeral=True)

    @commands.slash_command(description='Сыграть в слоты')
    @commands.cooldown(6, 300, commands.BucketType.user)
    async def slots(self, ctx, bet: int): # спасибо большое Линуксоиду за команду
        user_id = ctx.author.id
        user_balance = self.economy.get_balance(user_id)
        if user_balance < bet:
            embed = disnake.Embed(
                title='Ошибка',
                description='Недостаточно средств.',
                color=0xFFFFFF
            )
            await ctx.response.send_message(embed=embed, ephemeral=True)
            return
        elif bet < 50:
            embed = disnake.Embed(
                title='Ошибка',
                description='Ошибка, минимальная ставка 50📼.',
                color=0xFFFFFF
            )
            await ctx.response.send_message(embed=embed, ephemeral=True)
            return
        self.economy.update_balance(ctx.author.id, -bet)
        symbols = []
        weights = []
        rewards = {}
        for key, value in self.slots_cfg.items():
            symbols.append(key)
            weights.append(value['chance'])
            rewards[key] = value['reward']

        slots_embed = disnake.Embed(
            title='Слоты', 
            description='Идет рулетка...', 
            color=0xFFFFFF
        )
        slots_embed.add_field(name='Результат', value='⬛ ⬛ ⬛')
        slots_embed.set_footer(text=f'Ставка ・ {bet}📼')
        await ctx.response.send_message(embed=slots_embed)

        for _ in range(6):
            await asyncio.sleep(0.7)
            if random.random() < 0.2:
                roll = random.sample(symbols, 3)
            else:
                roll = random.choices(symbols, weights, k=3)
            slots_embed.set_field_at(0, name='Результат', value=' '.join(roll), inline=False)
            await ctx.edit_original_message(embed=slots_embed)

        symbol_count = {symbol: roll.count(symbol) for symbol in roll}
        
        total_reward = 0
        for symbol, count in symbol_count.items():
            if str(count) in rewards[symbol]:
                multiplier = rewards[symbol][str(count)]
                total_reward += bet * multiplier

        slots_embed.description = ''
        reward_text = '```Ничего, удачи в следующий раз```'
        if total_reward > 0:
            reward_text = f'```{total_reward}📼```'
            self.economy.update_balance(ctx.author.id, total_reward)
        slots_embed.add_field(name='Награда', value=reward_text, inline=False)
        await ctx.edit_original_message(embed=slots_embed)

    @commands.slash_command(description='Обычная рулетка')
    async def roullete(self, ctx, bet: int, space: str = commands.Param(name='space', description='Выберите цвет', choices=['Красный', 'Черный'])):
        user_id = ctx.author.id
        user_balance = self.economy.get_balance(user_id)

        if user_balance < bet:
            embed = disnake.Embed(
                title='Ошибка',
                description='Недостаточно средств.',
                color=0xFFFFFF
            )
            await ctx.response.send_message(embed=embed, ephemeral=True)
            return
        elif bet < 50:
            embed = disnake.Embed(
                title='Ошибка',
                description='Ошибка, минимальная ставка 50📼.',
                color=0xFFFFFF
            )

        self.economy.update_balance(user_id, -bet)

        timestamp = int(time.time()) + 10  
        time_str = f'<t:{timestamp}:R>'

        embed = disnake.Embed(
            title='Рулетка',
            description=f'Игрок - {ctx.author.mention}\nСтавка: ```{bet}📼 на {space}```\nИгра начнется через {time_str}',
            color=0xFFFFFF
        )
        embed.set_footer(text=f'Ставка ・ {bet}📼')
        await ctx.response.send_message(embed=embed)
        await asyncio.sleep(9)

        result = random.choice(['Красный', 'Черный'])

        if space == result:
            reward = bet * 2
            embed = disnake.Embed(
                title='Рулетка',
                description=f'Выпал **{space}** цвет.\nВыйгрыш:```{reward}📼```',
                color=0xFFFFFF
            )
            embed.set_footer(text=f'Ставка ・ {bet}📼')
            self.economy.update_balance(user_id, reward)
        else:
            embed = disnake.Embed(
                title='Рулетка',
                description=f'Выпал **{result}** цвет.\nВыйгрыш:```Ничего, удачи в следующий раз.```',
                color=0xFFFFFF
            )
            embed.set_footer(text=f'Ставка ・ {bet}📼')
        await ctx.edit_original_message(embed=embed)

    @commands.slash_command(description='Сыграть в русскую рулетку')
    @commands.cooldown(5, 300, commands.BucketType.user)
    async def russian_roulette(self, ctx, bet: int):
        user_id = ctx.author.id
        user_balance = self.economy.get_balance(user_id)
        
        if user_balance < bet:
            embed = disnake.Embed(
                title='Ошибка',
                description='Недостаточно средств.',
                color=0xFFFFFF
            )
            await ctx.response.send_message(embed=embed, ephemeral=True)
            return
        elif bet < 50:
            embed = disnake.Embed(
                title='Ошибка',
                description='Ошибка, минимальная ставка 50📼.',
                color=0xFFFFFF
            )

        self.economy.update_balance(user_id, -bet)

        embed = disnake.Embed(
            title='Русская рулетка',
            description=f'Участники 1/5\n{ctx.author.mention}\n\nОбщий баланс: ```{bet}📼```\nСтавка: ```{bet}📼```',
            color=0xFFFFFF
        )

        game = {
            'admin' : ctx.author,
            'players' : [ctx.author],
            'bet' : bet,
            'total_bet' : bet,
            'current_player' : None,
            'start' : True
        }
        view = RouletteView(game, self.economy)
        await ctx.response.send_message(embed=embed, view=view)

class RouletteView(disnake.ui.View):
    def __init__(self, game, economy):
        super().__init__()
        self.game = game
        self.economy = economy

    @disnake.ui.button(label='Начать', custom_id='start', style=disnake.ButtonStyle.green, disabled=True)
    async def start(self, button: disnake.ui.Button, ctx: disnake.MessageInteraction):
        game = self.game
        game['current_player'] = random.choice(game['players'])

        if ctx.author != game['admin']:
            embed = disnake.Embed(
                title='Ошибка',
                description='Только админ может начать игру.',
                color=0xFFFFFF
            )
            await ctx.response.send_message(embed=embed, ephemeral=True)
            return

        await ctx.message.delete()

        embed = disnake.Embed(
            title='Русская рулетка',
            description=f'{game["current_player"].mention} начинает стрелять первым!\n\n'
                        f'Общий баланс: ```{game["total_bet"]}📼```\nСтавка: ```{game["bet"]}📼```',
            color=0xFFFFFF
        )
        roulette_game_view = RouletteGameView(game, self.economy)

        await ctx.response.send_message(embed=embed, view=roulette_game_view)

    @disnake.ui.button(label='Зайти', custom_id='join', style=disnake.ButtonStyle.blurple)
    async def join(self, button: disnake.ui.Button, ctx: disnake.MessageInteraction):
        user = ctx.author
        game = self.game  

        if user in game['players']:
            embed = disnake.Embed(
                title='Ошибка',
                description='Вы уже в игре!',
                color=0xFFFFFF
            )
            await ctx.response.send_message(embed=embed, ephemeral=True)
            return

        if user == game['admin'] or len(game['players']) == 0:
            embed = disnake.Embed(
                title='Ошибка',
                description='Вы не можете зайти в игру, если уже один из игроков в игре.',
                color=0xFFFFFF
            )
            await ctx.response.send_message(embed=embed, ephemeral=True)
            return

        user_balance = self.economy.get_balance(user.id)
        if user_balance < game['bet']:
            embed = disnake.Embed(
                title='Ошибка',
                description='Недостаточно средств.',
                color=0xFFFFFF
            )
            await ctx.response.send_message(embed=embed, ephemeral=True)
            return

        self.economy.update_balance(user.id, -game['bet'])
        game['players'].append(user)
        game['total_bet'] += game['bet']

        embed = disnake.Embed(
            title='Русская рулетка',
            description=f'Участники {len(game["players"])} / 5\n{" ".join([p.mention for p in game["players"]])}\n\n'
                        f'Общий баланс: ```{game["total_bet"]}📼```\nСтавка: ```{game["bet"]}📼```',
            color=0xFFFFFF
        )

        if len(game['players']) > 1:
            self.children[0].disabled = False  

        await ctx.response.edit_message(embed=embed, view=self)

    @disnake.ui.button(label='Отменить', custom_id='cancel', style=disnake.ButtonStyle.red)
    async def cancel(self, button: disnake.ui.Button, ctx: disnake.MessageInteraction):
        if ctx.author != self.game['admin']:  
            embed = disnake.Embed(
                title='Ошибка',
                description='Только админ может отменить игру.',
                color=0xFFFFFF
            )
            await ctx.response.send_message(embed=embed, ephemeral=True)
            return
        
        game = self.game
        game['start'] = False
        for player in game['players']:
            self.economy.update_balance(player.id, game['bet'])
        embed = disnake.Embed(
            title='Русская рулетка',
            description='Игра отменена. Деньги возвращены на баланс.',
            color=0xFFFFFF
        )
        await ctx.message.delete()
        await ctx.response.send_message(embed=embed)

class RouletteGameView(disnake.ui.View):
    def __init__(self, game, economy):
        super().__init__()
        self.game = game
        self.economy = economy
        self.reset_chamber()

    def reset_chamber(self):
        self.shots_fired = 0
        self.bullet_position = random.randint(1, 6)

    async def next_turn(self, ctx):
        # Следующий игрок
        current_player = self.game['current_player']
        players = self.game['players']
        current_index = players.index(current_player)
        next_index = (current_index + 1) % len(players)
        self.game['current_player'] = players[next_index]

        # Отправляем Embed с информацией о ходе и кнопками
        embed = disnake.Embed(
            title='Русская рулетка',
            description=(
                f'Очередь игрока {self.game["current_player"].mention}!\n\n'
                f'Общий баланс: ```{self.game["total_bet"]}📼```\n'
                f'Ставка: ```{self.game["bet"]}📼```'
            ),
            color=0xFFFFFF
        )
        await ctx.followup.send(embed=embed, view=self)

    @disnake.ui.button(label='🔫Стрелять', custom_id='shoot', style=disnake.ButtonStyle.blurple)
    async def shoot(self, button: disnake.ui.Button, ctx: disnake.MessageInteraction):
        game = self.game
        current_player = game['current_player']

        if ctx.author != current_player:
            embed = disnake.Embed(
                title='Ошибка',
                description='Ваша очередь не наступила!',
                color=0xFFFFFF
            )
            await ctx.response.send_message(embed=embed, ephemeral=True)
            return

        self.shots_fired += 1
        is_deadly = self.shots_fired == self.bullet_position

        if is_deadly:
            # Игрок погибает
            game['players'].remove(current_player)
            embed = disnake.Embed(
                title='Русская рулетка',
                description=f'{current_player.mention} стреляет и... Погибает.',
                color=0xFFFFFF
            )
            await ctx.response.edit_message(embed=embed, view=None)
            await asyncio.sleep(5)
            await ctx.message.delete()

            # Проверяем, остался ли один победитель
            if len(game['players']) == 1:
                winner = game['players'][0]
                self.economy.update_balance(winner.id, game['total_bet'])
                embed = disnake.Embed(
                    title='Победа!',
                    description=f'{winner.mention} побеждает и выигрывает: ```{game["total_bet"]}📼```',
                    color=0xFFFFFF
                )
                game['active'] = False
                await ctx.followup.send(embed=embed)
                self.stop()
                return
            else:
                self.reset_chamber()
                # Назначаем следующего игрока после погибшего
                next_index = 0
                game['current_player'] = game['players'][next_index]
                await self.next_turn(ctx)
        else:
            # Игрок выживает
            embed = disnake.Embed(
                title='Русская рулетка',
                description=f'{current_player.mention} стреляет и... Выживает.',
                color=0xFFFFFF
            )
            await ctx.response.edit_message(embed=embed, view=None)
            await asyncio.sleep(5)
            await ctx.message.delete()

            # Следующий ход
            await self.next_turn(ctx)

    @disnake.ui.button(label='💰Повысить общий баланс', custom_id='up', style=disnake.ButtonStyle.blurple)
    async def up(self, button: disnake.ui.Button, ctx: disnake.MessageInteraction):
        game = self.game
        current_player = game['current_player']

        if ctx.author != current_player:
            embed = disnake.Embed(
                title='Ошибка',
                description='Ваша очередь не наступила!',
                color=0xFFFFFF
            )
            await ctx.response.send_message(embed=embed, ephemeral=True)
            return

        user_balance = self.economy.get_balance(ctx.author.id)
        if user_balance < game['bet']:
            embed = disnake.Embed(
                title='Ошибка',
                description='Недостаточно средств для повышения.',
                color=0xFFFFFF
            )
            await ctx.response.send_message(embed=embed, ephemeral=True)
            return

        self.economy.update_balance(ctx.author.id, -game['bet'])
        game['total_bet'] += game['bet']

        embed = disnake.Embed(
            title='Русская рулетка',
            description=(
                f'{ctx.author.mention} увеличил общий баланс и пропускает ход!\n\n'
                f'Общий баланс: ```{game["total_bet"]}📼```\n'
                f'Ставка: ```{game["bet"]}📼```'
            ),
            color=0xFFFFFF
        )
        await ctx.response.edit_message(embed=embed, view=None)
        await asyncio.sleep(5)
        await ctx.message.delete()

        # Следующий ход
        await self.next_turn(ctx)

    @disnake.ui.button(label='💤Подтолкнуть', custom_id='push', style=disnake.ButtonStyle.blurple)
    async def push(self, button: disnake.ui.Button, ctx: disnake.MessageInteraction):
        game = self.game
        current_player = game['current_player']

        if ctx.author not in game['players']:
            embed = disnake.Embed(
                title='Ошибка',
                description='Вы не можете подтолкнуть, так как не являетесь участником игры!',
                color=0xFFFFFF
            )
            await ctx.response.send_message(embed=embed, ephemeral=True)
            return

        if ctx.author == current_player:
            embed = disnake.Embed(
                title='Ошибка',
                description='Вы не можете подтолкнуть самого себя!',
                color=0xFFFFFF
            )
            await ctx.response.send_message(embed=embed, ephemeral=True)
            return

        embed = disnake.Embed(
            title='Русская рулетка',
            description=f'{ctx.author.mention} подтолкнул {current_player.mention} к выстрелу!',
            color=0xFFFFFF
        )
        await ctx.response.edit_message(embed=embed, view=None)
        await asyncio.sleep(5)
        await ctx.message.delete()

        self.shots_fired += 1
        is_deadly = self.shots_fired == self.bullet_position

        if is_deadly:
            game['players'].remove(current_player)
            embed = disnake.Embed(
                title='Русская рулетка',
                description=f'{current_player.mention} стреляет и... Погибает.',
                color=0xFFFFFF
            )
            message = await ctx.followup.send(embed=embed)
            await asyncio.sleep(5)
            await message.delete()

            if len(game['players']) == 1:
                winner = game['players'][0]
                self.economy.update_balance(winner.id, game['total_bet'])
                embed = disnake.Embed(
                    title='Победа!',
                    description=f'{winner.mention} побеждает и выигрывает: ```{game["total_bet"]}📼```',
                    color=0xFFFFFF
                )
                game['active'] = False
                await ctx.followup.send(embed=embed)
                self.stop()
                return
            else:
                self.reset_chamber()
                # Следующий ход — первый игрок в списке после удаления погибшего
                next_index = 0
                game['current_player'] = game['players'][next_index]
                await self.next_turn(ctx)
        else:
            embed = disnake.Embed(
                title='Русская рулетка',
                description=f'{current_player.mention} стреляет и... Выживает.',
                color=0xFFFFFF
            )
            await ctx.followup.send(embed=embed)
            await asyncio.sleep(5)

            # Следующий ход
            await self.next_turn(ctx)

    @disnake.ui.button(label='⬇️', custom_id='down', style=disnake.ButtonStyle.blurple)
    async def down(self, button: disnake.ui.Button, ctx: disnake.MessageInteraction):
        async for message in ctx.channel.history(limit=2):
            if message.author == ctx.bot.user:
                await message.delete()

        embed = disnake.Embed(
            title='Русская рулетка',
            description=(
                f'Очередь игрока {self.game["current_player"].mention}!\n\n'
                f'Общий баланс: ```{self.game["total_bet"]}📼```\n'
                f'Ставка: ```{self.game["bet"]}📼```'
            ),
            color=0xFFFFFF
        )
        await ctx.response.send_message(embed=embed, view=self)

def setup(bot):
    bot.add_cog(EconomyGames(bot))