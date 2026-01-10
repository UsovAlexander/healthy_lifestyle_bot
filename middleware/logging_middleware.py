import logging
from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import Message

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class LoggingMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any]
    ) -> Any:
        user = event.from_user
        logger.info(
            f"User: {user.id} (@{user.username}) | "
            f"Command: {event.text} | "
            f"Chat: {event.chat.id}"
        )
        
        try:
            result = await handler(event, data)
            logger.info(f"Command {event.text} processed successfully")
            return result
        except Exception as e:
            logger.error(f"Error processing {event.text}: {e}")
            raise