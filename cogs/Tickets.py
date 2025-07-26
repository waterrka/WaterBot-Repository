import disnake
from disnake.ext import commands
from datetime import datetime
import io

TICKET_CATEGORY = 1266797507145629836
MODERAITON = [1266812096209879123, 1266805974585446506]
LOG_CHANNEL = 1390278452250411088

class Tickets(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        self.bot.add_view(TicketView(self.bot))
        self.bot.add_view(ManageTicketView(self.bot))

    @commands.command()
    @commands.has_any_role(*MODERAITON)
    async def ticket_setup(self, ctx):
        embed = disnake.Embed(
            title='Система Тикетов',
            description=(
                'С помощью тикетов вы можете подать заявку на какую-либо роль, '
                'написать репорт на человека, либо задать вопрос администрации.\n' \
                'За шуточный тикет, предупреждение/мут 1 час.\n\n'
                'Чтобы открыть тикет, нажмите на одну из интересующих кнопок ниже.'
            ),
            color=0xFFFFFF
        )
        view = TicketView(self.bot)
        await ctx.send(embed=embed, view=view)
    
    async def ticket_create(self, ctx, ticket_type, message):
        await ctx.response.defer()
        category = disnake.utils.get(ctx.guild.categories, id=TICKET_CATEGORY)

        overwrites = {
            ctx.guild.default_role: disnake.PermissionOverwrite(view_channel=False),
            ctx.author: disnake.PermissionOverwrite(view_channel=True)
        }
        
        for role_id in MODERAITON:
            role = ctx.guild.get_role(role_id)
            if role:
                overwrites[role] = disnake.PermissionOverwrite(view_channel=True)

        channel = await ctx.guild.create_text_channel(
            name=f'{ticket_type}-{ctx.author.name}',
            topic=f'{ticket_type} тикет от {ctx.author}',
            category=category,
            overwrites=overwrites,
            reason='Создан новый тикет'
        )

        embed = disnake.Embed(
            title=f'{ticket_type} Тикет от {ctx.author}',
            description=message,
            color=0xFFFFFF
        )
        view = ManageTicketView(self.bot)
        await channel.send(embed=embed, view=view)

        embed_initial = disnake.Embed(
            title='Тикет создан',
            description=f'Ваш тикет: {channel.mention}.',
            color=0xFFFFFF
        )
        await ctx.followup.send(embed=embed_initial, ephemeral=True)

    async def ticket_close_with_reason(self, ctx: disnake.ModalInteraction, reason):
        if ctx.channel.category and ctx.channel.category.id == TICKET_CATEGORY:
            log_channel = self.bot.get_channel(LOG_CHANNEL)
            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            log_text = f'📁 Тикет: {ctx.channel.name}\n' \
                       f'Закрыл: {ctx.user} ({ctx.user.id})\n' \
                       f'Причина: {reason}\n' \
                       f'Время закрытия: {now}\n\n' \
                       f'Подробности:\n'

            messages = await ctx.channel.history(limit=None, oldest_first=True).flatten()

            for msg in messages:
                author = f'{msg.author.display_name} ({msg.author.id})'
                content = msg.content.strip() or '[вложение/эмбед]'
                log_text += f"[{msg.created_at.strftime('%H:%M:%S')}] {author}: {content}\n"

            file = disnake.File(fp=io.StringIO(log_text), filename=f'ticket_log_{ctx.channel.name}.txt')
            await log_channel.send(content=f'📄 Лог тикета `{ctx.channel.name}`', file=file)

            await ctx.channel.delete(reason=f'Тикет закрыт с причиной: {reason}')
        else:
            await ctx.response.send_message(
                embed=disnake.Embed(
                    title='Ошибка',
                    description='Этот канал не является тикетом.',
                    color=0xFFFFFF
                ),
                ephemeral=True
            )

    async def take_ticket(self, ctx):
        await ctx.response.defer()
        if ctx.channel.category and ctx.channel.category.id == TICKET_CATEGORY:
            embed = disnake.Embed(
                title='Тикет взят на рассмотрение',
                description=f'Модератор {ctx.author.mention} взял тикет на рассмотрение.',
                color=0xFFFFFF
            )
            await ctx.channel.send(embed=embed)
        else:
            embed = disnake.Embed(
                title='Ошибка',
                description='Этот канал не является тикетом.',
                color=0xFFFFFF
            )
            await ctx.response.send_message(embed=embed, ephemeral=True)

class TicketView(disnake.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot

    @disnake.ui.button(label='📊Заявка', style=disnake.ButtonStyle.primary, custom_id='ticket_request')
    async def ticket_request(self, button: disnake.ui.Button, ctx: disnake.MessageInteraction):
        message = (
            'Форма заявки\n\n'
            'Тип заявок:\n'
            '- Модератор.\n'
            '- Хелпер.\n'
            '- Ивент-менеджер.\n'
            '- Редактор газеты.\n\n'
            'Форма заявки:\n'
            '1. Как долго вы активите на сервере?\n'
            '2. Почему вы хотите данную роль, и почему именно вы?\n'
            '3. Ваш возраст (13+, если боитесь).\n'
            '4. Расскажите о себе на этом сервере (Имеется в виду личность на сервере).\n'
            '5. Сколько времени вы можете уделить серверу?\n'
            '6. Есть ли у вас опыт?\n'
            '7. Насколько вы надежны, и не будете ли вы злоупотреблять этим?\n'
            '8. Ваш часовой пояс (необязательно).\n'
        )
        await ctx.client.get_cog('Tickets').ticket_create(ctx, 'Заявка', message)

    @disnake.ui.button(label='😈Репорт', style=disnake.ButtonStyle.primary, custom_id='ticket_report')
    async def ticket_report(self, button: disnake.ui.Button, ctx: disnake.MessageInteraction):
        message = (
            'Форма репорта\n\n'
            '1. На кого репорт?\n'
            '2. Причина.\n'
            '3. Доказательства.\n'
            '4. Вы уверены в этом?'
        )
        await ctx.client.get_cog('Tickets').ticket_create(ctx, 'Репорт', message)

    @disnake.ui.button(label='🧑‍⚖️ Апелляция наказания', style=disnake.ButtonStyle.primary, custom_id='ticket_appeal')
    async def ticket_appeal(self, button: disnake.ui.Button, ctx: disnake.MessageInteraction):
        message = (
            'Форма апелляции наказания\n\n'
            '1. Какое наказание вы получили? (мут, бан, варн и т.д.)\n'
            '2. Когда это произошло?\n'
            '3. Кто выдал наказание (если знаете)?\n'
            '4. Почему вы считаете наказание несправедливым?\n'
            '5. Прикрепите доказательства или объяснение.\n'
            '6. Ваше обещание/комментарий для администрации (по желанию).'
        )
        await ctx.client.get_cog('Tickets').ticket_create(ctx, 'Апелляция', message)

    @disnake.ui.button(label='🤖Отчет-об-ошибках', style=disnake.ButtonStyle.primary, custom_id='ticket_error_report')
    async def ticket_error_report(self, button: disnake.ui.Button, ctx: disnake.MessageInteraction):
        message = (
            'Форма отчета-об-ошибках\n\n'
            '1. Опишите вашу проблему кратко.\n'
            '2. Загрузите скриншоты или видео(если возможно).\n'
            '3. Любая другая информация, которая может помочь разработчикам.'
        )
        await ctx.client.get_cog('Tickets').ticket_create(ctx, 'Отчет-об-ошибках', message)

    @disnake.ui.button(label='📚 FAQ — задать вопрос', style=disnake.ButtonStyle.primary, custom_id='ticket_question')
    async def ticket_question(self, button: disnake.ui.Button, ctx: disnake.MessageInteraction):
        message = (
            'Форма для вопроса\n\n'
            '1. Расскажите о вашем вопросе кратко.\n'
            '2. Расскажите подробнее.'
        )
        await ctx.client.get_cog('Tickets').ticket_create(ctx, 'Вопрос', message)

    @disnake.ui.button(label='❔️Репорт на модератора', style=disnake.ButtonStyle.primary, custom_id='ticket_mod_report')
    async def ticket_mod_report(self, button: disnake.ui.Button, ctx: disnake.MessageInteraction):
        message = (
            'Форма репорта на модератора\n\n'
            '1. На какого модератора репорт?\n'
            '2. Причина (как можно подробнее).\n'
            '3. Доказательства.\n'
            '4. Вы уверены в этом?'
        )
        await ctx.client.get_cog('Tickets').ticket_create(ctx, 'Репорт-на-модератора', message)

    @disnake.ui.button(label='🎟Другое', style=disnake.ButtonStyle.primary, custom_id='ticket_other')
    async def ticket_other(self, button: disnake.ui.Button, ctx: disnake.MessageInteraction):
        message = 'Пожалуйста, опишите ваш запрос подробнее.'
        await ctx.client.get_cog('Tickets').ticket_create(ctx, 'Другое', message)

class ManageTicketView(disnake.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot

    @disnake.ui.button(label='Закрыть Тикет с Причиной', style=disnake.ButtonStyle.danger, custom_id='close_ticket_with_reason')
    async def close_ticket_with_reason(self, button: disnake.ui.Button, ctx: disnake.MessageInteraction):
        modal = CloseTicketReasonModal(bot=self.bot, ctx=ctx)
        await ctx.response.send_modal(modal)

    @disnake.ui.button(label='Взять на Рассмотрение', style=disnake.ButtonStyle.success, custom_id='take_ticket')
    async def take_ticket(self, button: disnake.ui.Button, ctx: disnake.MessageInteraction):
        if any(role.id in MODERAITON for role in ctx.author.roles):
            await ctx.client.get_cog('Tickets').take_ticket(ctx)
        else:
            embed = disnake.Embed(
                title='Ошибка',
                description='У вас нет прав для выполнения этого действия.',
                color=0xFFFFFF
            )
            await ctx.response.send_message(embed=embed, ephemeral=True)

class CloseTicketReasonModal(disnake.ui.Modal):
    def __init__(self, bot, ctx: disnake.MessageInteraction):
        self.bot = bot
        components = [
            disnake.ui.TextInput(
                label='Причина',
                placeholder='Введите текст...',
                custom_id='reason_input',
                style=disnake.TextInputStyle.paragraph,
                max_length=500
            )
        ]
        super().__init__(title='Закрыть тикет с причиной', components=components)

    async def callback(self, ctx: disnake.ModalInteraction):
        await ctx.response.defer() 
        reason = ctx.text_values["reason_input"]
        await self.bot.get_cog("Tickets").ticket_close_with_reason(ctx, reason)

def setup(bot):
    bot.add_cog(Tickets(bot))