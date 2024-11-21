import os
from dotenv import load_dotenv


from aiogram import Bot
from aiogram.enums.parse_mode import ParseMode
from aiogram.client.bot import DefaultBotProperties


load_dotenv()
BOT_TOKEN = os.getenv('TG_API')
bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
