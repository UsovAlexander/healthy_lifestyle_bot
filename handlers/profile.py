from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message
from services.calculations import calculate_calorie_goal, calculate_water_goal, calculate_bmr
from services.weather import get_weather
from database import create_or_update_user, get_user

router = Router()

class ProfileStates(StatesGroup):
    weight = State()
    height = State()
    age = State()
    gender = State()
    activity = State()
    city = State()
    goal_type = State()
    calorie_confirmation = State()

@router.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer(
        "Добро пожаловать в Healthy Lifestyle Bot!\n\n"
        "Я помогу вам отслеживать:\n"
        "• Норму воды и калорий\n"
        "• Питание и тренировки\n"
        "• Прогресс по целям\n\n"
        "Основные команды:\n"
        "/set_profile - Настроить профиль\n"
        "/log_water <количество> - Записать выпитую воду\n"
        "/log_food <продукт> - Записать съеденную еду\n"
        "/log_workout <тип> <минуты> - Записать тренировку\n"
        "/check_progress - Проверить прогресс\n"
        "/food_tips - Рекомендации продуктов с калорийностью\n"
        "/help - Помощь"
    )

@router.message(Command("set_profile"))
async def cmd_set_profile(message: Message, state: FSMContext):
    await message.answer("Давайте настроим ваш профиль!\nВведите ваш вес (в кг):")
    await state.set_state(ProfileStates.weight)

@router.message(ProfileStates.weight)
async def process_weight(message: Message, state: FSMContext):
    try:
        weight = float(message.text)
        if weight <= 0 or weight > 300:
            await message.answer("Пожалуйста, введите корректный вес (1-300 кг):")
            return
        await state.update_data(weight=weight, user_id=message.from_user.id)
        await message.answer("Введите ваш рост (в см):")
        await state.set_state(ProfileStates.height)
    except ValueError:
        await message.answer("Пожалуйста, введите число для веса (например: 75):")

@router.message(ProfileStates.height)
async def process_height(message: Message, state: FSMContext):
    try:
        height = float(message.text)
        if height <= 0 or height > 250:
            await message.answer("Пожалуйста, введите корректный рост (50-250 см):")
            return
        await state.update_data(height=height)
        await message.answer("Введите ваш возраст:")
        await state.set_state(ProfileStates.age)
    except ValueError:
        await message.answer("Пожалуйста, введите число для роста (например: 180):")

@router.message(ProfileStates.age)
async def process_age(message: Message, state: FSMContext):
    try:
        age = int(message.text)
        if age <= 0 or age > 120:
            await message.answer("Пожалуйста, введите корректный возраст (1-120 лет):")
            return
        await state.update_data(age=age)
        await message.answer("Введите ваш пол (мужчина/женщина):")
        await state.set_state(ProfileStates.gender)
    except ValueError:
        await message.answer("Пожалуйста, введите целое число для возраста:")

@router.message(ProfileStates.gender)
async def process_gender(message: Message, state: FSMContext):
    gender = message.text.lower()
    if gender not in ['мужчина', 'женщина']:
        await message.answer("Пожалуйста, введите 'мужчина' или 'женщина':")
        return
    
    await state.update_data(gender=gender)
    await message.answer("Сколько минут активности у вас в день (в среднем)?")
    await state.set_state(ProfileStates.activity)

@router.message(ProfileStates.activity)
async def process_activity(message: Message, state: FSMContext):
    try:
        activity = int(message.text)
        if activity < 0 or activity > 600:
            await message.answer("Пожалуйста, введите корректное количество минут (0-600):")
            return
        await state.update_data(activity_minutes=activity)
        await message.answer("В каком городе вы находитесь?")
        await state.set_state(ProfileStates.city)
    except ValueError:
        await message.answer("Пожалуйста, введите целое число для минут активности:")

@router.message(ProfileStates.city)
async def process_city(message: Message, state: FSMContext):
    city = message.text
    await state.update_data(city=city)
    
    weather_data = await get_weather(city)
    
    if weather_data.get('success', False):
        temperature = weather_data['temperature']
        weather_desc = weather_data['description']
        await message.answer(f"Погода в {city}: {weather_desc}, {temperature}°C")
        await state.update_data(temperature=temperature)
    else:
        await message.answer(f"Не удалось получить погоду для {city}. Используем температуру 20°C.")
        await state.update_data(temperature=20)
    
    await message.answer("Введите вашу цель по калориям (похудеть/поддерживать/набрать):")
    await state.set_state(ProfileStates.goal_type)

@router.message(ProfileStates.goal_type)
async def process_goal_type(message: Message, state: FSMContext):
    goal = message.text.lower()
    if goal not in ['похудеть', 'поддерживать', 'набрать']:
        await message.answer("Пожалуйста, введите: похудеть/поддерживать/набрать:")
        return
    
    await state.update_data(goal_type=goal)
    
    user_data = await state.get_data()
    
    bmr = calculate_bmr(
        user_data['weight'],
        user_data['height'],
        user_data['age'],
        user_data['gender']
    )
    
    recommended_calories = calculate_calorie_goal(
        bmr,
        user_data['activity_minutes'],
        goal
    )
    

    await state.update_data(
        bmr=bmr,
        recommended_calories=recommended_calories
    )
    
    await message.answer(
        f"На основе ваших данных:\n"
        f"• Вес: {user_data['weight']} кг\n"
        f"• Рост: {user_data['height']} см\n"
        f"• Возраст: {user_data['age']} лет\n"
        f"• Активность: {user_data['activity_minutes']} мин/день\n"
        f"• Цель: {user_data['goal_type']}\n\n"
        f"Рекомендуемая дневная норма калорий: {recommended_calories} ккал\n\n"
        f"Вы согласны с целью в калориях?\n"
        f"Введите:\n"
        f"• \"Да\" - принять расчет\n"
        f"• Любое число - ваша собственная цель в Ккал\n"
        f"• \"Нет\" - отменить настройку профиля"
    )
    
    await state.set_state(ProfileStates.calorie_confirmation)

@router.message(ProfileStates.calorie_confirmation)
async def process_calorie_confirmation(message: Message, state: FSMContext):
    user_input = message.text.strip().lower()
    
    user_data = await state.get_data()
    recommended_calories = user_data.get('recommended_calories', 2000)
    
    if user_input == 'да':
        final_calories = recommended_calories
        confirmation_msg = f"Принята рекомендуемая норма: {final_calories} Ккал"
    
    elif user_input == 'нет':
        await message.answer("Настройка профиля отменена. Используйте /set_profile для начала заново.")
        await state.clear()
        return
    
    else:
        try:
            custom_calories = float(user_input)
            
            min_reasonable = 500
            max_reasonable = 5000
            
            if custom_calories < min_reasonable or custom_calories > max_reasonable:
                await message.answer(
                    f"Пожалуйста, введите разумное значение ({min_reasonable}-{max_reasonable} Ккал).\n"
                    f"Введите число или \"Да\" для принятия расчета ({recommended_calories} Ккал):"
                )
                return
            
            final_calories = custom_calories
            diff = final_calories - recommended_calories
            diff_percent = (diff / recommended_calories) * 100
            
            confirmation_msg = (
                f"Установлена ваша цель: {final_calories} Ккал\n"
                f"(расчет был {recommended_calories} Ккал, разница: {diff:+.0f} Ккал, {diff_percent:+.1f}%)"
            )
            
        except ValueError:
            await message.answer(
                f"Не понял ваш ответ.\n"
                f"Введите:\n"
                f"• \"Да\" - принять {recommended_calories} Ккал\n"
                f"• Число - ваша цель в Ккал\n"
                f"• \"Нет\" - отменить"
            )
            return
    
    await state.update_data(calorie_goal=final_calories)
    
    water_goal = calculate_water_goal(
        user_data['weight'],
        user_data['activity_minutes'],
        user_data.get('temperature', 20)
    )
    
    db_data = {
        'user_id': user_data['user_id'],
        'weight': user_data['weight'],
        'height': user_data['height'],
        'age': user_data['age'],
        'gender': user_data['gender'],
        'activity_minutes': user_data['activity_minutes'],
        'city': user_data['city'],
        'calorie_goal': final_calories,
        'water_goal': water_goal,
        'logged_water': 0,
        'logged_calories': 0,
        'burned_calories': 0
    }
    
    await create_or_update_user(db_data)
    
    response = (
        "Профиль успешно сохранен!\n\n"
        f"Ваши данные:\n"
        f"• Вес: {user_data['weight']} кг\n"
        f"• Рост: {user_data['height']} см\n"
        f"• Возраст: {user_data['age']} лет\n"
        f"• Пол: {user_data['gender']}\n"
        f"• Активность: {user_data['activity_minutes']} мин/день\n"
        f"• Город: {user_data['city']}\n"
        f"• Цель: {user_data['goal_type']}\n\n"
        f"Ваши дневные цели:\n"
        f"• Калории: {final_calories} ккал ({confirmation_msg.split(':')[0]})\n"
        f"• Вода: {water_goal} мл\n\n"
        f"Основные команды:\n"
        f"/log_water <количество> - записать воду\n"
        f"/log_food <продукт> - записать еду\n"
        f"/log_workout <тип> <минуты> - записать тренировку\n"
        f"/check_progress - проверить прогресс\n"
        f"/food_tips - Рекомендации продуктов с калорийностью\n"
        f"/profile - посмотреть профиль"
    )
    
    await message.answer(response)
    await state.clear()

@router.message(Command("profile"))
async def cmd_profile(message: Message):
    user = await get_user(message.from_user.id)
    
    if not user:
        await message.answer("Профиль не найден. Используйте /set_profile для создания.")
        return
    
    response = (
        f"Ваш профиль:\n"
        f"• Вес: {user['weight']} кг\n"
        f"• Рост: {user['height']} см\n"
        f"• Возраст: {user['age']} лет\n"
        f"• Пол: {user['gender']}\n"
        f"• Активность: {user['activity_minutes']} мин/день\n"
        f"• Город: {user['city']}\n"
        f"• Цель по калориям: {user['calorie_goal']} ккал\n"
        f"• Цель по воде: {user['water_goal']} мл"
    )
    
    await message.answer(response)