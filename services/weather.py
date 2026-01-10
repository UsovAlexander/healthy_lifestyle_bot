import aiohttp
from config import config

async def get_weather(city: str) -> dict:    
    url = "http://api.openweathermap.org/data/2.5/weather"
    params = {
        'q': city,
        'appid': config.WEATHER_API_KEY,
        'units': 'metric',
        'lang': 'ru'
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        'temperature': data['main']['temp'],
                        'description': data['weather'][0]['description'],
                        'city': data['name'],
                        'success': True
                    }
                else:
                    return {"temperature": 20, "error": f"API error: {response.status}"}
    except Exception as e:
        return {"temperature": 20, "error": str(e)}