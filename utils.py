import dateparser
from geopy.geocoders import Nominatim
import re
import sqlite3

def standardize_birthdate(date):
    '''Функция стандартизации даты рождения'''
    # Приводим строку к формату даты
    birt_date = dateparser.parse(date, languages=['ru', 'en'])
    # Приводим полученную дату к нужному формату "ДД.ММ.ГГГГ"
    formatted_date = birt_date.strftime('%d.%m.%Y')
    return formatted_date

def validate_city(city):
    if re.search('\d', city):
        raise ValueError
    else:
        geolocator = Nominatim(user_agent="my_app")
        location = geolocator.geocode(city)
        if location == None:
            raise ValueError
        else:
            return city

def get_users_dict():
    with sqlite3.connect('users.db') as connect:
        cursor = connect.cursor()

        # Получение всех чат-ид пользователей из таблицы
        cursor.execute("SELECT DISTINCT id, name, city, birthday FROM users")
        rows = cursor.fetchall()

        # Формирование словаря пользователей
        users_dict = {}
        for row in rows:
            chat_id, name, city, birthday = row
            user_info = {'name': name, 'city': city, 'birthday': birthday}
            users_dict[chat_id] = user_info

        # Возврат словаря пользователей
        return users_dict
    
def get_first_name(fullname):
    _, name, _ = fullname.split(' ')
    return name

def validate_name(name):
    if len(name.split(' ')) < 3:
        raise ValueError
    else:
        return name