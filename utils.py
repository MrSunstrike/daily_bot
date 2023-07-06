import datetime
import sqlite3

import dateparser
import pytz
from geopy.geocoders import Nominatim
from pymystem3 import Mystem


def get_nsk_time():
    now = datetime.datetime.now()
    nsk_time = pytz.timezone('Asia/Novosibirsk')
    nsk_now = nsk_time.localize(now)
    return nsk_now

def get_time_to_msg():
    TEXT = ('❌<code>[ОШИБКА]: Нейромодуль не найден.</code>\nК сожалению, не '
            'могу Вас понять. Я отправлю Вам сообщение через')
    nsk_now = get_nsk_time()
    target_time = pytz.timezone('Asia/Novosibirsk').localize(datetime.datetime(
        nsk_now.year, nsk_now.month, nsk_now.day + 1, 10, 0, 0))
    delta = target_time - nsk_now
    h, m, _ = str(delta).split(':')
    if 'day' in h:
        h = h[7:]
    if int(m[0]) == 0:
        m = m[-1]
    if int(h) == 1 or int(h) == 21:
        h_txt = 'час'
    elif 1 < int(h) < 5 or 21 < int(h) < 25:
        h_txt = 'часа'
    else:
        h_txt = 'часов'
    if str(m)[-1] == '1':
        m_txt = 'минуту'
    elif 1 < int(str(m)[-1]) < 5:
        m_txt = 'минуты'
    else:
        m_txt = 'минут'
    if int(h) == 0:
        text = f'{TEXT} {m} {m_txt}'
    elif int(m) == 0:
        text = f'{TEXT} {h} {h_txt}'
    else:
        text = f'{TEXT} {h} {h_txt} {m} {m_txt}'
    return text


def standardize_birthdate(date):
    '''Функция стандартизации даты рождения'''
    # Приводим строку к формату даты
    birt_date = dateparser.parse(date, languages=['ru', 'en'])
    # Приводим полученную дату к нужному формату "ДД.ММ.ГГГГ"
    formatted_date = birt_date.strftime('%d.%m.%Y')
    return formatted_date

def validate_city(city):
    m = Mystem()
    analysis = m.analyze(city)
    for word_info in analysis:
        if 'analysis' in word_info and word_info['analysis']:
            tags = word_info['analysis'][0]['gr']
            if 'гео' in tags:
                geolocator = Nominatim(user_agent="my_app")
                location = geolocator.geocode(city)
                if location == None:
                    raise ValueError
                else:
                    return city
        else:
            raise ValueError

def get_users_dict():
    with sqlite3.connect('users.db') as connect:
        cursor = connect.cursor()

        # Получение всех чат-ид пользователей из таблицы
        cursor.execute("SELECT DISTINCT id, name, city, birthday, is_blocked \
                       FROM users")
        rows = cursor.fetchall()

        # Формирование словаря пользователей
        users_dict = {}
        for row in rows:
            chat_id, name, city, birthday, is_blocked = row
            user_info = {
                'name': name,
                'city': city,
                'birthday': birthday,
                'is_blocked': is_blocked
            }
            users_dict[chat_id] = user_info

        # Возврат словаря пользователей
        return users_dict
    
def get_first_name(fullname):
    _, name, _ = fullname.split(' ')
    return name

def validate_name(name):
    if len(name.split(' ')) != 3:
        raise ValueError
    else:
        return name