import asyncio
import logging
import datetime
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from config import config
from database import init_db, reset_daily_logs
from middleware.logging_middleware import LoggingMiddleware
from handlers.profile import router as profile_router
from handlers.tracking import router as tracking_router
from handlers.progress import router as progress_router

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

async def main():
    if not config.BOT_TOKEN:
        logger.error("BOT_TOKEN не найден в переменных окружения!")
        return
    
    await init_db()
    logger.info("База данных инициализирована")
    
    bot = Bot(token=config.BOT_TOKEN)
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)
    
    dp.update.middleware(LoggingMiddleware())
    
    dp.include_router(profile_router)
    dp.include_router(tracking_router)
    dp.include_router(progress_router)
    
    async def reset_logs_at_midnight():
        while True:
            now = datetime.datetime.now()
            next_midnight = (now + datetime.timedelta(days=1)).replace(
                hour=0, minute=0, second=0, microsecond=0
            )
            wait_seconds = (next_midnight - now).total_seconds()
            
            await asyncio.sleep(wait_seconds)
            await reset_daily_logs()
            logger.info("Дневные логи сброшены (полночь)")
    
    asyncio.create_task(reset_logs_at_midnight())
    
    logger.info("Бот запускается...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Бот остановлен")