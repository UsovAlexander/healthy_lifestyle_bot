from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from database import get_user

router = Router()

@router.message(Command("check_progress"))
async def cmd_check_progress(message: Message):
    user = await get_user(message.from_user.id)
    
    if not user:
        await message.answer("Профиль не найден. Используйте /set_profile для создания.")
        return
    
    calorie_balance = user['logged_calories'] - user['burned_calories']
    remaining_calories = max(0, user['calorie_goal'] - calorie_balance)
    
    progress_report = (
        "Ваш прогресс за сегодня:\n\n"
        
        "ВОДА:\n"
        f"• Выпито: {user['logged_water']:.0f} мл из {user['water_goal']:.0f} мл\n"
        f"• Осталось: {max(0, user['water_goal'] - user['logged_water']):.0f} мл\n"
        f"• Прогресс: {min(100, (user['logged_water'] / user['water_goal'] * 100)):.1f}%\n\n"
        
        "КАЛОРИИ:\n"
        f"• Потреблено: {user['logged_calories']:.0f} ккал\n"
        f"• Сожжено: {user['burned_calories']:.0f} ккал\n"
        f"• Баланс: {calorie_balance:.0f} ккал\n"
        f"• Цель: {user['calorie_goal']} ккал\n"
        f"• Осталось: {remaining_calories:.0f} ккал\n"
        f"• Прогресс: {min(100, (calorie_balance / user['calorie_goal'] * 100)):.1f}%\n\n"
    )
    
    recommendations = ""
    
    if user['logged_water'] < user['water_goal'] * 0.5:
        recommendations += "Выпейте больше воды! Еще не поздно достичь цели.\n"
    
    if calorie_balance > user['calorie_goal'] * 1.1:
        recommendations += "Вы превысили дневную норму калорий.\n"
    elif calorie_balance < user['calorie_goal'] * 0.7:
        recommendations += "Не забудьте поесть! У вас большой дефицит калорий.\n"
    
    if recommendations:
        progress_report += "Рекомендации:\n" + recommendations
    
    await message.answer(progress_report)

@router.message(Command("help"))
async def cmd_help(message: Message):
    help_text = (
        "Помощь по командам бота:\n\n"
        
        "Профиль:\n"
        "/set_profile - Настроить или изменить профиль\n"
        "/profile - Просмотреть текущий профиль\n\n"
        
        "Трекинг:\n"
        "/log_water <количество> - Записать выпитую воду (в мл)\n"
        "Пример: /log_water 500\n\n"
        "/log_food <продукт> - Записать съеденную еду\n"
        "Пример: /log_food банан\n\n"
        "/log_workout <тип> <минуты> - Записать тренировку\n"
        "Пример: /log_workout бег 30\n"
        "Типы: бег, ходьба, велосипед, плавание, силовая, йога, кардио\n\n"
        
        "Прогресс:\n"
        "/check_progress - Проверить дневной прогресс\n"
        "/help - Показать это сообщение\n\n"
        
        "Бот рассчитывает нормы на основе вашего веса, роста, возраста, активности и погоды."
    )
    
    await message.answer(help_text)