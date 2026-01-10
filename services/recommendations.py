from typing import List, Dict
import random
from datetime import datetime

def get_low_calorie_recommendations(remaining_calories: float) -> List[str]:
    low_calorie_foods = {
        'огурец': 15,
        'помидор': 18,
        'салат листовой': 14,
        'редис': 16,
        'сельдерей': 12,
        'шпинат': 23,
        'капуста белокочанная': 25,
        'брокколи': 34,
        'цветная капуста': 30,
        'кабачок': 24,
        'перец болгарский': 27,
        'спаржа': 20,
        'грибы шампиньоны': 27,
        'яблоко': 52,
        'груша': 57,
        'апельсин': 43,
        'грейпфрут': 42,
        'клубника': 41,
        'малина': 52,
        'черника': 57,
        'арбуз': 30,
        'дыня': 35,
        'греческий йогурт 0%': 59,
        'творог обезжиренный': 73,
        'кефир 1%': 40,
        'яйцо вареное': 155,
        'куриная грудка': 165,
        'рыба треска': 78,
        'креветки': 99,
        'тофу': 76
    }
    
    recommendations = []
    
    if remaining_calories < 100:
        very_low_calorie = {k: v for k, v in low_calorie_foods.items() if v < 50}
        if very_low_calorie:
            for food, calories in list(very_low_calorie.items())[:3]:
                recommendations.append(f"{food}: {calories} ккал/100г")
    
    elif remaining_calories <= 300:
        for food, calories in low_calorie_foods.items():
            if calories <= remaining_calories * 0.3:
                recommendations.append(f"{food}: {calories} ккал/100г")
    
    else:
        for food, calories in low_calorie_foods.items():
            if calories <= remaining_calories * 0.2:
                recommendations.append(f"{food}: {calories} ккал/100г")
    
    if len(recommendations) < 3:
        all_foods = list(low_calorie_foods.items())
        random.shuffle(all_foods)
        for food, calories in all_foods[:3 - len(recommendations)]:
            if f"{food}: {calories} ккал/100г" not in recommendations:
                recommendations.append(f"{food}: {calories} ккал/100г")
    
    return recommendations[:3]