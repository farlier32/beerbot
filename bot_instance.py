from aiogram import Bot
import config
from aiogram.enums.parse_mode import ParseMode
from aiogram.client.bot import DefaultBotProperties

bot = Bot(token=config.BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))