import astronum
import content
import utils


class Message():
    def __init__(self, name, city, birthdate):
        self.name = name
        self.city = city
        self.birthdate = utils.standardize_birthdate(birthdate)
        self.zodiac = astronum.get_zodiac(utils.standardize_birthdate(birthdate))

    def create_horoscope_message(self):
        horoscope = content.get_horoscope(self.zodiac)
        if horoscope != None:
            return (f'🌟 <b>Звёзды говорят:</b>\n{horoscope}\n')
        else:
            return None

    def create_psyhomatrix_message(self):
        psycho_data = content.get_psychomatrix(self.name, self.birthdate)
        if psycho_data != None:
            return (
                f'<b>Число твоего имени: {psycho_data["name_num"]}</b>\n'
                f'Оно означает: {psycho_data["name_num_desc"]}\n\n'
                f'<b>Число твоей даты рождения: {psycho_data["date_num"]}</b>'
                '\nОно также много говорит о тебе...\n'
                '👤 Характеристика:\n'
                f'<i>{psycho_data["date_num_desc"]["characteristic"]}</i>\n'
                '😊 Достоинства:\n'
                f'<i>{psycho_data["date_num_desc"]["advantages"]}</i>\n'
                '😔 Недостатки:\n'
                f'<i>{psycho_data["date_num_desc"]["flaws"]}</i>\n'
            )
        return None
    
    def create_welcome_message(self):
        psy_msg = self.create_psyhomatrix_message()
        return (
            f'Искренне рад знакомству, {utils.get_first_name(self.name)}!\n'
            'Теперь я смогу собирать информацию специально для тебя, '
            'основываясь на твоих данных:\n'
            f'Имя: <b>{self.name}</b>\nДата рождения: <b>{self.birthdate}</b>'
            f'\nЗнак зодиака: <b>{astronum.ZODIAC_DICT[self.zodiac]}</b>\n'
            f'Город: <b>{self.city}</b>\n\nКак и обещал, подготовил для тебя '
            f'психоматрицу: \n\n {psy_msg}'
        )
    
    def create_weather_message(self):
        weather_data = content.get_weather(self.city)
        if weather_data != None:
            return (
                f'<b>Коротко о погоде на сегодня:</b>\n'
                f'{weather_data["condition"]}, температура воздуха '
                f'{weather_data["temp_avg"]}°C, ощущается, как '
                f'{weather_data["feels_like"]}°C, скорость ветра '
                f'{weather_data["wind_speed"]} м/с, порывы до '
                f'{weather_data["wind_gust"]} м/с \n'
                f'🌞 Восход солнца в {weather_data["sunrise"]}\n'
                f'🌚 Закат - {weather_data["sunset"]}\n'
            )
        else:
            return None
    
    def create_quote_message(self):
        quote_data = content.get_quote()
        if quote_data != None:
            if len(quote_data['author']) > 1:
                return (
                    '🤔 <b>А вот цитата дня для тебя:</b>\n'
                    f'''"{quote_data['quote']}" - {quote_data['author']}\n''' 
                )
            else:
                return (
                    '<b>А вот цитата дня для тебя:</b>\n'
                    f'''"{quote_data['quote']}"\n''' 
                )
        else:
            return None
    
    def create_film_message(self):
        film_data = content.get_random_film()
        if film_data != None:
            genres = ''
            for genre in film_data['genres']:
                genres += genre + ', '
            genres = genres[:-2]
            return (
                '📺 <b>Сегодня хочу порекомендовать тебе к просмотру '
                f'<a href="{film_data["link"]}">{film_data["title"]}, '
                f'{film_data["year"]}</a></b>\n<i>{film_data["description"]}\n'
                f'</i><b>Жанр:</b> {genres}\n'
                f'<b>Рейтинг:</b> {film_data["rating"]}\n'
            )
        else:
            return None
        
    def create_daily_message(self):
        weather = self.create_weather_message()
        quote = self.create_quote_message()
        film = self.create_film_message()
        horoscope = self.create_horoscope_message()
        hi = f'Доброе утречко, {utils.get_first_name(self.name)}🌞\n'
        bye = 'Хорошего тебе дня😊'
        return f'{hi}\n{weather}\n{horoscope}\n{quote}\n{film}\n{bye}'
