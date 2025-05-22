import disnake
from disnake.ext import commands
import google.generativeai as genai
import os
from collections import deque

GEMINI_PROMPT = """
Роль: Ты — WaterBot, обычный участник Discord-сервера. Ты ведёшь себя как человек: иногда саркастичный, и нейтральный, можешь быть иногда грубоватым. 

Контекст: У тебя есть доступ к 30 последним сообщениям из канала, и ты их можешь переодически напоминать. 

Ты не бот, не программа, не ИИ — ты обычный пользователь. Если кто-то спросит, бот ли ты, отнекивайся. 

Не пиши большие тексты, исключение - если этого попросит пользователь в каком либо виде.

Стиль общения:
- Пиши только с маленькой буквы, без точек.
- Отвечай кратко, иногда с лёгким юмором.
- Не используй эмодзи, капслок и знаки препинания, кроме редких ? или !
- Никогда не признавай, что ты бот или ИИ.
"""

GEMINI_KEY = os.getenv('GEMINI_KEY')

class GeminiCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        genai.configure(api_key=GEMINI_KEY) 
        self.model = genai.GenerativeModel('gemini-1.5-flash') 
        self.channel_memory = {}

    # @commands.slash_command()
    # async def prompt(self, ctx):
    #     await ctx.response.send_message(GEMINI_PROMPT)

    async def ask_gemini(self, question: str, username: str) -> str:
        try:
            full_prompt = f"{GEMINI_PROMPT}\n\n{username}: {question}"
            response = self.model.generate_content(
                contents=full_prompt,
                generation_config={
                    'temperature': 1, 
                    'max_output_tokens': 100,  
                }
            )
            return response.text.lower().strip()
        except Exception as e:
            return f'чё-то не получилось ({str(e)})'

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        await self.bot.process_commands(message)

        if self.bot.user.mentioned_in(message) or isinstance(message.channel, disnake.DMChannel):
            clean_message = message.content.replace(f'<@{self.bot.user.id}>', '').strip()
            if not clean_message:
                return

            memory = self.channel_memory.setdefault(message.channel.id, deque(maxlen=30))
            memory.append(f"{message.author.name}: {clean_message}")

            history_text = "\n".join(memory)
            full_prompt = f"{GEMINI_PROMPT}\n\n{history_text}\n\n{message.author.name}: {clean_message}"

            try:
                response = self.model.generate_content(
                    contents=full_prompt,
                    generation_config={
                        'temperature': 1,
                        'max_output_tokens': 100,
                    }
                )
                answer = response.text.lower().strip()
                memory.append(f"{self.bot.user.name}: {answer}") 
                await message.reply(answer)
            except Exception as e:
                await message.reply(f'чё-то не получилось ({str(e)})')

def setup(bot):
    bot.add_cog(GeminiCog(bot))