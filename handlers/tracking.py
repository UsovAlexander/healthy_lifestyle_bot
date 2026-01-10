from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from services.food import get_food_info
from services.calculations import calculate_workout_calories, get_workout_water_recommendation
from database import log_water, log_food, log_workout, get_user

router = Router()

class FoodStates(StatesGroup):
    waiting_for_grams = State()

@router.message(Command("log_water"))
async def cmd_log_water(message: Message):
    try:
        args = message.text.split()
        if len(args) < 2:
            await message.answer("Используйте: /log_water <количество в мл>\nПример: /log_water 500")
            return
        
        amount = float(args[1])
        if amount <= 0:
            await message.answer("Пожалуйста, введите положительное количество.")
            return
        
        await log_water(message.from_user.id, amount)
        
        user = await get_user(message.from_user.id)
        if user:
            remaining = max(0, user['water_goal'] - user['logged_water'])
            
            await message.answer(
                f"💧 Записано: {amount} мл воды.\n"
                f"Всего сегодня: {user['logged_water']} мл\n"
                f"Цель: {user['water_goal']} мл\n"
                f"Осталось: {remaining} мл"
            )
        else:
            await message.answer("💧 Вода записана. Сначала настройте профиль /set_profile")
            
    except ValueError:
        await message.answer("Пожалуйста, введите число для количества воды.\nПример: /log_water 500")

@router.message(Command("log_food"))
async def cmd_log_food(message: Message, state: FSMContext):
    try:
        args = message.text.split(maxsplit=1)
        if len(args) < 2:
            await message.answer("Используйте: /log_food <название продукта>\nПример: /log_food банан")
            return
        
        product_name = args[1]
        
        food_info = await get_food_info(product_name)
        
        if not food_info.get('success', False):
            await message.answer(
                f"Не удалось получить информацию о продукте '{product_name}'.\n"
                f"Ошибка: {food_info.get('error', 'Неизвестная ошибка')}\n\n"
                f"Пожалуйста, введите количество калорий вручную на 100г:"
            )
            await state.update_data(
                food_name=product_name,
                calories_per_100g=None
            )
            await state.set_state(FoodStates.waiting_for_grams)
            return
        
        await state.update_data(
            food_name=food_info['name'],
            calories_per_100g=food_info['calories']
        )
        
        await message.answer(
            f"{food_info['name']} — {food_info['calories']} Ккал на 100 г.\n"
            f"Сколько грамм вы съели?"
        )
        await state.set_state(FoodStates.waiting_for_grams)
        
    except Exception as e:
        await message.answer(f"Ошибка: {str(e)}")

@router.message(FoodStates.waiting_for_grams)
async def process_food_grams(message: Message, state: FSMContext):
    try:
        grams = float(message.text)
        if grams <= 0:
            await message.answer("Пожалуйста, введите положительное количество грамм.")
            return
        
        data = await state.get_data()
        food_name = data['food_name']
        calories_per_100g = data.get('calories_per_100g')
        
        if calories_per_100g is None:
            await message.answer("Введите калорийность продукта на 100г:")
            await state.update_data(grams=grams)
            return
        
        calories = (calories_per_100g * grams) / 100
        
        await log_food(
            user_id=message.from_user.id,
            food_name=food_name,
            calories=calories,
            grams=grams
        )
        
        user = await get_user(message.from_user.id)
        if user:
            remaining = max(0, user['calorie_goal'] - user['logged_calories'])
            
            await message.answer(
                f"Записано: {food_name} — {calories:.1f} Ккал ({grams} г)\n"
                f"Всего сегодня: {user['logged_calories']:.0f} Ккал\n"
                f"Цель: {user['calorie_goal']} Ккал\n"
                f"Осталось: {remaining:.0f} Ккал"
            )
        else:
            await message.answer(f"Записано: {food_name} — {calories:.1f} Ккал")
        
        await state.clear()
        
    except ValueError:
        await message.answer("Пожалуйста, введите число для количества грамм.")

@router.message(Command("log_workout"))
async def cmd_log_workout(message: Message):
    try:
        args = message.text.split()
        if len(args) < 3:
            await message.answer(
                "Используйте: /log_workout <тип тренировки> <время в минутах>\n"
                "Пример: /log_workout бег 30\n\n"
                "Доступные типы: бег, ходьба, велосипед, плавание, силовая, йога, кардио, танцы"
            )
            return
        
        workout_type = args[1]
        duration = int(args[2])
        
        if duration <= 0:
            await message.answer("Пожалуйста, введите положительное время тренировки.")
            return
        
        user = await get_user(message.from_user.id)
        if not user:
            await message.answer("Сначала настройте профиль: /set_profile")
            return
        
        burned_calories = calculate_workout_calories(
            workout_type,
            duration,
            user['weight']
        )
        
        water_recommendation = get_workout_water_recommendation(duration)
        
        await log_workout(
            user_id=message.from_user.id,
            workout_type=workout_type,
            duration=duration,
            burned_calories=burned_calories
        )
        
        response = (
            f"{workout_type.capitalize()} {duration} минут — {burned_calories} Ккал.\n"
            f"Рекомендуется выпить дополнительно: {water_recommendation} мл воды.\n\n"
            f"Всего сожжено сегодня: {user['burned_calories'] + burned_calories} Ккал"
        )
        
        await message.answer(response)
        
    except ValueError:
        await message.answer("Пожалуйста, введите корректное время тренировки (целое число).")
    except Exception as e:
        await message.answer(f"Ошибка: {str(e)}")