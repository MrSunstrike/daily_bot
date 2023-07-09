import os

import logging
import requests
import xmltodict
from dotenv import load_dotenv
from geopy.geocoders import Nominatim

import astronum

load_dotenv()

logger = logging.getLogger('content_logger')
logger.setLevel(logging.DEBUG)
file_handler = logging.FileHandler('content_logs.log')
file_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

ERROR = '<данные не получены>'

WEATHER_DB = {}

DICT_NUM_SMILE = {
    1: '1⃣',
    2: '2⃣',
    3: '3⃣',
    4: '4⃣',
    5: '5⃣',
    6: '6⃣',
    7: '7⃣',
    8: '8⃣',
    9: '9⃣'
}

def get_quote():
    url = 'http://api.forismatic.com/api/1.0/'
    params = {
        'method': 'getQuote',
        'format': 'json',
    }
    response = requests.get(url=url, params=params)
    if response.status_code == 200:
        data = response.json()
        quote = data.get("quoteText")
        author = data.get("quoteAuthor")
        logger.info(f'Успешно получен контет из {url}\n'
                    f'Контент: цитата - {quote}, автор - {author}')
        return {
            'quote': quote.strip(),
            'author': author
        }
    else:
        logger.error(f'Ошибка запроса к серверу "{url}"\n'
                     f'Код ошибки:{response.status_code}')
        return None
    
def get_weather(city):
    CONDITION_DICT = {
        'clear': ['☀️', 'Ясно'],
        'partly-cloudy': ['⛅', 'Малооблачно'],
        'cloudy': ['⛅', 'Облачно с прояснениями'],
        'overcast': ['☁️', 'Пасмурно'],
        'drizzle': ['🌧️', 'Морось'],
        'light-rain': ['🌧️', 'Небольшой дождь'],
        'rain': ['🌧️', 'Дождь'],
        'moderate-rain': ['🌧️', 'Умеренно сильный дождь'],
        'heavy-rain': ['🌧️', 'Сильный дождь'],
        'continuous-heavy-rain': ['🌧️', 'Длительный сильный дождь'],
        'showers': ['🌧️', 'Ливень'],
        'wet-snow': ['🌧️🌨️', 'Дождь со снегом'],
        'light-snow': ['🌨️', 'Небольшой снег'],
        'snow': ['🌨️', 'Снег'],
        'snow-showers': ['🌨️', 'Снегопад'],
        'hail': ['🌧️', 'Град'],
        'thunderstorm': ['⛈️', 'Гроза'],
        'thunderstorm-with-rain': ['⛈️', 'Дождь с грозой'],
        'thunderstorm-with-hail': ['⛈️', 'Гроза с градом']
    }
    geolocator = Nominatim(user_agent="my_app")
    location = geolocator.geocode(city)
    url = "https://api.weather.yandex.ru/v2/informers"
    params = {
        'lat': str(location.latitude),
        'lon': str(location.longitude),
        'lang': "ru_RU"
    }
    headers = {"X-Yandex-API-Key": os.getenv('X_YANDEX_API_KEY')}
    if city not in WEATHER_DB:
        response = requests.get(url=url, headers=headers, params=params)
        if response.status_code == 200:
            data = response.json()
            parts = data.get('forecast', {}).get('parts', [])
            if parts:
                temp_avg = parts[0].get('temp_avg', ERROR)
                feels_like = parts[0].get('feels_like', ERROR)
                condition = CONDITION_DICT.get(
                    parts[0].get('condition', ERROR)
                )
                temp_water = parts[0].get('temp_water', ERROR)
                sunrise = data.get('forecast', {}).get('sunrise', ERROR)
                sunset = data.get('forecast', {}).get('sunset', ERROR)
                wind_speed = parts[0].get('wind_speed', ERROR)
                wind_gust = parts[0].get('wind_gust', ERROR)
                dict_weather = {
                    'temp_avg': temp_avg, # Средняя температура
                    'feels_like': feels_like, # Ощущается как
                    'condition': condition, # Описание погоды
                    'temp_water': temp_water, # Температура воды
                    'sunrise': sunrise, # Время восхода
                    'sunset': sunset, # Время заката
                    'wind_speed': wind_speed, # Скорость ветра
                    'wind_gust': wind_gust # Скорость порывов ветра
                }
                WEATHER_DB[city] = dict_weather
                logger.info(f'Успешно получен контет из {url}\n'
                            f'Контент: погода - {dict_weather} в городе - '
                            f'{city}({location})')
                return dict_weather
            else:
                logger.error(f'Ошибка структуры словаря. Словарь - {data}')
                return None
        else:
            logger.error(f'Ошибка запроса к серверу "{url}"\n'
                         f'Код ошибки:{response.status_code}')
            dict_weather = {
                'temp_avg': ERROR,
                'feels_like': ERROR,
                'condition': ERROR,
                'temp_water': ERROR,
                'sunrise': ERROR,
                'sunset': ERROR,
                'wind_speed': ERROR,
                'wind_gust': ERROR,
            }
            return dict_weather
    else:
        city_weather_db = WEATHER_DB.get(city)
        dict_weather = {
            'temp_avg': city_weather_db['temp_avg'],
            'feels_like': city_weather_db['feels_like'],
            'condition': city_weather_db['condition'],
            'temp_water': city_weather_db['temp_water'],
            'sunrise': city_weather_db['sunrise'],
            'sunset': city_weather_db['sunset'],
            'wind_speed': city_weather_db['wind_speed'],
            'wind_gust': city_weather_db['wind_gust']
        }
        logger.info(f'Успешно переиспользована погода в городе {city}')
        return dict_weather

def get_random_film():
    url = 'https://api.kinopoisk.dev/v1.3/movie/random'
    headers = {
        'accept': 'application/json',
        'X-API-KEY': os.getenv('SECRET_KEY_API_KINOPOISK')
    }
    response = requests.get(url=url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        title = data.get('name')
        description = data.get('description')
        genres = [i.get('name') for i in data.get('genres')]
        year = data.get('year')
        rating = data.get('rating').get('kp')
        link = f'https://www.kinopoisk.ru/film/{data.get("id")}'
        dict_response = {
            'title': title,
            'description': description,
            'genres': genres,
            'year': year,
            'rating': rating,
            'link': link
        }
        logger.info(f'Успешно получен контет из {url}\n'
                    f'Контент: Фильм - {dict_response}')
        return dict_response
    else:
        logger.error(f'Ошибка запроса к серверу "{url}"\n'
                     f'Код ошибки: {response.status_code}')
        return None

def get_horoscope(zodiac):
    zodiac = zodiac.lower()
    url = 'https://ignio.com/r/export/utf/xml/daily/com.xml'
    response = requests.get(url)
    if response.status_code == 200:
        xml_string = response.content.decode('utf-8')
        data_dict = xmltodict.parse(xml_string)
        horoscope = data_dict.get('horo').get(zodiac).get('today')
        logger.info(f'Успешно получен контет из {url}\n'
                    f'Контент: Гороскоп - {horoscope}')
        return horoscope
    else:
        logger.error(f'Ошибка запроса к серверу "{url}"\n'
                     f'Код ошибки: {response.status_code}')
        return None

def get_psychomatrix(fullname: str, birthdate: str):
    '''Функция для рассчета психоматрицы'''
    name_num = astronum.get_name_number(fullname)
    date_num = astronum.get_birthdate_number(birthdate)
    # Возвращаем результат в виде словаря
    return {
        "name_num": DICT_NUM_SMILE[name_num],
        "name_num_desc": astronum.NAME_NUMBERS_DICT[name_num],
        "date_num": DICT_NUM_SMILE[date_num],
        "date_num_desc": astronum.BIRTH_NUMBERS_DICT[date_num]
    }
