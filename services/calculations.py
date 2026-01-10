from config import config

def calculate_bmr(weight: float, height: float, age: int, gender: str = 'male') -> float:
    if gender.lower() == 'мужчина':
        bmr = 10 * weight + 6.25 * height - 5 * age + 5
    else:
        bmr = 10 * weight + 6.25 * height - 5 * age - 161
    return bmr

def calculate_calorie_goal(bmr: float, activity_minutes: int, goal: str = 'поддерживать') -> float:
    activity_factor = 1.2 + (activity_minutes / 60) * 0.2
    daily_calories = bmr * activity_factor
    
    if goal == 'похудеть':
        daily_calories *= 0.85
    elif goal == 'набрать':
        daily_calories *= 1.15
    
    return round(daily_calories)

def calculate_water_goal(weight: float, activity_minutes: int, temperature: float = 20) -> float:
    base_water = weight * config.WATER_PER_KG
    
    activity_water = (activity_minutes // 30) * config.WATER_PER_30_MIN
    
    weather_water = config.WATER_FOR_HOT_WEATHER if temperature > 25 else 0
    
    total_water = base_water + activity_water + weather_water
    return round(total_water)

def calculate_workout_calories(workout_type: str, duration: int, weight: float) -> float:
    met_values = {
        'бег': 8.0,
        'ходьба': 3.5,
        'велосипед': 7.5,
        'плавание': 6.0,
        'силовая': 5.0,
        'йога': 3.0,
        'кардио': 7.0,
        'танцы': 5.5,
        'футбол': 7.0,
        'баскетбол': 6.5
    }
    
    met = met_values.get(workout_type.lower(), 5.0)

    calories_burned = met * weight * (duration / 60)
    return round(calories_burned)

def get_workout_water_recommendation(duration: int) -> float:
    return (duration // 30) * 200