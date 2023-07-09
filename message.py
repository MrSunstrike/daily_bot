import astronum
import content
import utils

DICT_MSG = {
    'hi': 'Бип-бип-буп-уип! <code>[..язык загружен..]</code> Ну, то есть, '
    'здравствуйте! Мое имя <b>D06V1</b>, но Вы можете называть меня '
    '<b>Дейл</b>. Я роботизированный дэйли-помощник🤖',

    'get_name': '<code>[ЗАГРУЗКА ПРОТОКОЛА "ЗНАКОМСТВО"]</code>\nИспытываю '
    'необходимость идентифицировать Вас. Напишите мне, пожалуйста, Ваше ФИО:',

    'get_city': '{}, для успешного cбора метеоданных со спутников и '
    'предоставления Вам корректной информации о погоде, мне необходимо '
    'установить Вашу геопозицию. Уточните, пожалуйста, название Вашего '
    'населенного пункта:',

    'get_city_2': '✅<code>[УСПЕШНО]: Валидация ФИО пройдена.</code>\nОчень '
    'приятно, {}! Для успешного cбора метеоданных со спутников и '
    'предоставления Вам корректной информации о погоде, мне необходимо '
    'установить Вашу геопозицию. Уточните, пожалуйста, название Вашего '
    'населенного пункта:',

    'get_bday': '{}, для завершения идентификации предоставьте, пожалуйста, '
    'дату Вашего рождения в формате <code>ДД.ММ.ГГГГ</code>:',

    'get_bday_2': '✅<code>[УСПЕШНО]: Населённый пункт "{}" найден. '
    'Подключение к спутникам завершено.</code>\n{}, для завершения '
    'идентификации предоставьте, пожалуйста, дату Вашего рождения в формате '
    'ДД.ММ.ГГГГ:',

    'welcome_back': '✅<code>[УСПЕШНО]: Идентификация завершена.</code>\n{}, '
    'рад вновь приветствовать Вас! Я продолжу направлять Вам '
    'персонализированные сообщения каждый день в 6:00 по часовому поясу GMT+3 '
    '(Москва)',

    'registration_1': 'Мой функционал пока сильно ограничен, но создатель '
    'работает над моим кодом каждые выходные, опираясь на обратную связь '
    'пользователей.',

    'registration_2': 'После идентификации я проанализирую данные и в начале '
    'каждого нового дня буду отправлять Вам полезную информацию:\n-Прогноз '
    'погоды\n-Рекомендации, основанные на положении космических тел\n'
    '-Случайное мотивирующее высказывание\n-Случайное кинопроизведение',

    'invalid_name': '❌<code>[ОШИБКА]: ФИО должно состоять из 3 слов.</code>\n'
    'Чтобы мои службы работали корректно, прошу предоставить мне Ваше полное '
    'ФИО:',

    'invalid_city': '❌<code>[ОШИБКА]: Населённый пункт не найден на планете '
    'Земля.</code>\nЧтобы мои службы работали корректно, прошу указать '
    'существующий населённый пункт',

    'invalid_bday': '❌<code>[ОШИБКА]: Некорректный формат даты.</code>\n'
    'Чтобы мои службы работали корректно, прошу указать дату рождения в '
    'формате ДД.ММ.ГГГГ',

    'bday_in_future': '❌<code>[ОШИБКА]: Дата из будущего.</code>\n'
    'Чтобы мои службы работали корректно, прошу указать Вашу реальную дату '
    'рождения в формате ДД.ММ.ГГГГ',

    'bday_incorrect': '❌<code>[ОШИБКА]: Некорректный возраст.</code>\n'
    'Пожалуйста, укажите Вашу реальную дату рождения в формате ДД.ММ.ГГГГ',

    'end_reg': '✅<code>[УСПЕШНО]: Идентификация завершена.</code>\n'
    'На основе Вашего профайла теперь я смогу генерировать персональные '
    'сообщения. Служба отправки сообщений запускается каждый день в 6:00 по '
    'часовому поясу GMT+3 (Москва). Рад Вас видеть в числе моих пользователей!'
}


class Message():
    def __init__(self, first_name, city, birthdate):
        self.name = first_name
        self.city = city
        self.birthdate = utils.standardize_birthdate(birthdate)
        self.zodiac = astronum.get_zodiac(utils.standardize_birthdate(birthdate))

    def create_horoscope_message(self):
        horoscope = content.get_horoscope(self.zodiac)
        zodiac = astronum.ZODIAC_DICT[self.zodiac][1]
        if horoscope != None:
            return (
                f'🌟<b>Рекомендация для родившихся под знаком "{zodiac}":</b>'
                f'<i>\n{horoscope}</i>\n')
        else:
            return None
    
    def create_personal_data_message(self):
        zodiac = astronum.ZODIAC_DICT[self.zodiac]
        psycho_data = content.get_psychomatrix(self.name, self.birthdate)
        name_num = psycho_data['name_num']
        name_num_desc = psycho_data['name_num_desc']
        date_num = psycho_data['date_num']
        characteristic = psycho_data['date_num_desc']['characteristic']
        advantages = psycho_data['date_num_desc']['advantages']
        flaws = psycho_data['date_num_desc']['flaws']
        return (
            '✅<code>[УСПЕШНО]: Профайл загружен.</code>\n'
            f'<b>ФИО:</b> <i>{self.name}</i>\n'
            f'<b>Дата рождения:</b> <i>{self.birthdate}</i>\n'
            f'<b>Город:</b> <i>{self.city}</i>\n'
            f'<b>Знак зодиака:</b> <i>{zodiac[0]}{zodiac[1]}</i>\n\n'
            '<code>[ПСИХОАНАЛИЗ ЛИЧНОСТИ НА ОСНОВЕ НУМЕРОЛОГИИ]:</code>\n'
            f'<b>Чиcло имени:</b> <i>{name_num}</i>\n'
            f'<b>Характеристика по числу имени:</b> <i>{name_num_desc}</i>\n\n'
            f'<b>Чиcло даты рождения:</b> <i>{date_num}</i>\n'
            '<b>Характеристика по числу даты рождения:</b> '
            f'<i>{characteristic}</i>\n'
            f'<b>Сильные стороны личности:</b> <i>{advantages}</i>\n'
            f'<b>Слабые стороны личности:</b> <i>{flaws}</i>\n'
        )
    
    def create_weather_message(self):
        weather_data = content.get_weather(self.city)
        icon = weather_data["condition"][0]
        if weather_data != None:
            return (
                f'{icon}<b>Погода в локации {self.city}:</b>\n<i>'
                f'{weather_data["condition"][1]}, средняя '
                f'температура воздуха сегодня составит '
                f'{weather_data["temp_avg"]}°C. Сейчас температура воздуха '
                f'{weather_data["feels_like"]}°C, скорость ветра '
                f'{weather_data["wind_speed"]} м/с, порывы до '
                f'{weather_data["wind_gust"]} м/с </i>\n'
                f'Восход солнца - <i>{weather_data["sunrise"]}</i>\n'
                f'Закат - <i>{weather_data["sunset"]}</i>\n'
            )
        else:
            return None
    
    def create_quote_message(self):
        quote_data = content.get_quote()
        if quote_data != None:
            if len(quote_data['author']) > 1:
                return (
                    '🤔<b>Интересная мысль на сегодня:</b>\n'
                    f'''<i>"{quote_data['quote']}" - '''
                    f'''{quote_data['author']}</i>\n''' 
                )
            else:
                return (
                    '🤔<b>Интересная мысль на сегодня:</b>\n'
                    f'''<i>"{quote_data['quote']}"</i>\n''' 
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
                '📺<b>Случайное кинопроизведение на сегодня: '
                f'<a href="{film_data["link"]}">{film_data["title"]}, '
                f'{film_data["year"]}</a></b>\n'
                f'<b>Описание:</b> <i>{film_data["description"]}</i>\n'
                f'<b>Жанр:</b> <i>{genres}</i>\n'
                f'<b>Рейтинг:</b> <i>{film_data["rating"]}</i>\n'
            )
        else:
            return None
        
    def create_daily_message(self):
        weather = self.create_weather_message()
        quote = self.create_quote_message()
        film = self.create_film_message()
        horoscope = self.create_horoscope_message()
        hi = f'Доброе утречко, {self.name}🌞 На связи Дейл🤖\n '
        bye = 'Хорошего Вам дня😊'
        return f'{hi}\n{weather}\n{horoscope}\n{quote}\n{film}\n{bye}'
