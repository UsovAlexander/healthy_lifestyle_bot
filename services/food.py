import aiohttp
import logging

async def get_food_info(product_name: str):
    """
    Получение информации о продукте через OpenFoodFacts API
    """
    url = "https://world.openfoodfacts.org/cgi/search.pl"
    params = {
        'action': 'process',
        'search_terms': product_name,
        'json': 'true',
        'page_size': '1'
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    products = data.get('products', [])
                    
                    if products:
                        product = products[0]
                        return {
                            'name': product.get('product_name', product_name),
                            'calories': product.get('nutriments', {}).get('energy-kcal_100g', 0),
                            'brand': product.get('brands', ''),
                            'success': True
                        }
                    else:
                        return {
                            'name': product_name,
                            'calories': 0,
                            'error': 'Продукт не найден',
                            'success': False
                        }
                else:
                    return {
                        'name': product_name,
                        'calories': 0,
                        'error': f'Ошибка API: {response.status}',
                        'success': False
                    }
    except Exception as e:
        logging.error(f"Ошибка API: {e}")
        return {
            'name': product_name,
            'calories': 0,
            'error': str(e),
            'success': False
        }