import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
    
    WATER_PER_KG = 30
    WATER_PER_30_MIN = 500
    WATER_FOR_HOT_WEATHER = 750
    
config = Config()