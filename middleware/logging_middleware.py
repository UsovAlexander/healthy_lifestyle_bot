import logging
from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import Update, Message, CallbackQuery

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
        handler: Callable[[Update, Dict[str, Any]], Awaitable[Any]],
        event: Update,
        data: Dict[str, Any]
    ) -> Any:
        
        user = event.message.from_user
        chat_id = event.message.chat.id
        text = event.message.text or ""
        
        if user:
            logger.info(
                f"User: {user.id} (@{user.username}) | "
                f"Text/Data: {text[:50]} | "
                f"Chat: {chat_id}"
            )
        else:
            logger.info(f"Update without user: {event.update_id}")
        
        try:
            result = await handler(event, data)
            if text:
                logger.info(f"Command {text} processed successfully")
            return result
        except Exception as e:
            logger.error(f"Error processing update: {e}")
            raise