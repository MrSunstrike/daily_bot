import requests
import xmltodict
import os
from dotenv import load_dotenv
import astronum, utils
from geopy.geocoders import Nominatim

load_dotenv()


def get_quote():
    url = 'http://api.forismatic.com/api/1.0/'
    params = {
        'method': 'getQuote',
        'format': 'json',
    }
    response = requests.get(url=url, params=params)
    if response.status_code == 200:
        data = response.json()
        quote = data["quoteText"]
        author = data["quoteAuthor"]
        return {
            'quote': quote,
            'author': author
        }
    else:
        return None
    
def get_weather(city):
    CONDITION_DICT = {
        'clear': 'ясно',
        'partly-cloudy': 'малооблачно',
        'cloudy': 'облачно с прояснениями',
        'overcast': 'пасмурно',
        'drizzle': 'морось',
        'light-rain': 'небольшой дождь',
        'rain': 'дождь',
        'moderate-rain': 'умеренно сильный дождь',
        'heavy-rain': 'сильный дождь',
        'continuous-heavy-rain': 'длительный сильный дождь',
        'showers': 'ливень',
        'wet-snow': 'дождь со снегом',
        'light-snow': 'небольшой снег',
        'snow': 'снег',
        'snow-showers': 'снегопад',
        'hail': 'град',
        'thunderstorm': 'гроза',
        'thunderstorm-with-rain': 'дождь с грозой',
        'thunderstorm-with-hail': 'гроза с градом'
    }
    geolocator = Nominatim(user_agent="my_app")
    location = geolocator.geocode(city)
    url = "https://api.weather.yandex.ru/v2/informers"
    params = {
        'lat': str(location.latitude),
        'lon': str(location.longitude)
    }
    headers = {"X-Yandex-API-Key": os.getenv('X_YANDEX_API_KEY')}
    response = requests.get(url=url, headers=headers, params=params)
    if response.status_code == 200:
        data = response.json()
        temp_avg = data['forecast']['parts'][0]['temp_avg']
        feels_like = data['forecast']['parts'][0]['feels_like']
        condition = CONDITION_DICT[
            data['forecast']['parts'][0]['condition']
        ]
        temp_water = data['forecast']['parts'][0]['temp_water']
        sunrise = data['forecast']['sunrise']
        sunset = data['forecast']['sunset']
        wind_speed = data['forecast']['parts'][0]['wind_speed']
        wind_gust = data['forecast']['parts'][0]['wind_gust']
        return {
            'temp_avg': temp_avg, # Средняя температура
            'feels_like': feels_like, # Ощущается как
            'condition': condition, # Описание погоды
            'temp_water': temp_water, # Температура воды
            'sunrise': sunrise, # Время восхода
            'sunset': sunset, # Время заката
            'wind_speed': wind_speed, # Скорость ветра
            'wind_gust': wind_gust # Скорость порывов ветра
        }
    else:
        return None

def get_random_film():
    url = 'https://api.kinopoisk.dev/v1.3/movie/random'
    headers = {
        'accept': 'application/json',
        'X-API-KEY': os.getenv('SECRET_KEY_API_KINOPOISK')
    }
    response = requests.get(url=url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        title = data['name']
        description = data['description']
        genres = [i['name'] for i in data['genres']]
        year = data['year']
        rating = data['rating']['kp']
        return {
            'title': title,
            'description': description,
            'genres': genres,
            'year': year,
            'rating': rating
        }
    else:
        return None

def get_horoscope(birthdate):
    zodiac = astronum.get_zodiac(birthdate).lower()
    url = 'https://ignio.com/r/export/utf/xml/daily/com.xml'
    response = requests.get(url)
    if response.status_code == 200:
        xml_string = response.content.decode('utf-8')
        data_dict = xmltodict.parse(xml_string)
        return data_dict['horo'][zodiac]['today']
    else:
        return None

def get_psychomatrix(fullname: str, birthdate: str):
    '''Функция для рассчета психоматрицы'''
    name_num = astronum.get_name_number(fullname)
    date_num = astronum.get_birthdate_number(birthdate)
    # Возвращаем результат в виде словаря
    return {
        "name_num": name_num,
        "name_num_desc": astronum.NAME_NUMBERS_DICT[name_num],
        "date_num": date_num,
        "date_num_desc": astronum.BIRTH_NUMBERS_DICT[date_num]
    }