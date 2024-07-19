import asyncio
import logging
from aiogram import Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from bot_instance import bot
from commands.admin_commands import router as admin_router
from commands.user_commands import router as user_router
from aiogram import Router


router = Router()

async def main():
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(admin_router)
    dp.include_router(user_router)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
