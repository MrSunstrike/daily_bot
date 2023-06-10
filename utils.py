import dateparser
from geopy.geocoders import Nominatim

def standardize_birthdate(date):
    '''Функция стандартизации даты рождения'''
    # Приводим строку к формату даты
    birt_date = dateparser.parse(date, languages=['ru', 'en'])
    # Приводим полученную дату к нужному формату "ДД.ММ.ГГГГ"
    formatted_date = birt_date.strftime('%d.%m.%Y')
    return formatted_date

def validate_city(city):
    geolocator = Nominatim(user_agent="my_app")
    location = geolocator.geocode(city)
    if location == None:
        raise ValueError
    else:
        return city