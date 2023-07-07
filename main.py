import datetime
import logging
import sqlite3
import sys
import time
from os import getenv

import schedule
import telegram
import telegram.ext
from telegram.error import Unauthorized
from dotenv import load_dotenv

from message import DICT_MSG, Message
from utils import (get_first_name, get_time_to_msg, get_users_dict,
                   validate_city, validate_name)


# Подгружаем токены из .env
load_dotenv()

TELEGRAM_TOKEN = getenv('DALE_API')

# Создаем логгер
logger = logging.getLogger('bot_logger')
logger.setLevel(logging.DEBUG)
file_handler = logging.FileHandler('bot_logs.log')
file_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

if not TELEGRAM_TOKEN:
        logger.critical('Отсутствует доступ к переменным окружения')
        sys.exit()

# Инициируем бота и апдейтер
bot = telegram.Bot(token=TELEGRAM_TOKEN)
upd = telegram.ext.Updater(token=TELEGRAM_TOKEN)

# Создание/подключение БД
with sqlite3.connect('users.db') as connect:
    cursor = connect.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, \
                   fullname TEXT, name TEXT, city TEXT, birthday TEXT, \
                   is_blocked BOOLEAN DEFAULT 0)")

# Задаем универсальную клавиатуру для пользователей
KEYBOARD = [[telegram.KeyboardButton('👤 Покажи мой профайл')]]
REPLY_MARKUP = telegram.ReplyKeyboardMarkup(
    KEYBOARD,
    resize_keyboard=True,
    button_width=2,
    button_height=2
)

def start(update, context):
    '''Функция начала диалога с пользователем'''
    user_id = update.effective_chat.id
    connect = sqlite3.connect('users.db')
    update.message.reply_text(text=DICT_MSG['hi'], parse_mode='HTML')
    # Ищем в базе пользователя по chat_id
    with connect:
        cursor = connect.cursor()
        cursor.execute("SELECT * FROM users WHERE id=?", (user_id,))
        row = cursor.fetchone()
        # Если запись с таким chat_id есть в БД:
        if row:
            # Передаем в перменные данные из БД
            name, city, birthday = row[2], row[3], row[4]
            # Если имени в базе нет:
            if not name:
                # Отправляем в функцию получения имени
                update.message.reply_text(DICT_MSG['get_name'],
                                          parse_mode='HTML')
                return 'get_name'
            # Если города в базе нет:
            elif not city:
                # Отправляем в функцию получения города
                update.message.reply_text(DICT_MSG['get_city'].format(name),
                                          parse_mode='HTML')
                return 'get_city'
            # Если даты рождения в базе нет:
            elif not birthday:
                # Отправляем в функцию получения даты рождения
                update.message.reply_text(DICT_MSG['get_bday'].format(name),
                                          parse_mode='HTML')
                return 'get_bday'
            # Если все данные известны:
            else:
                # Приветствуем пользователя
                update.message.reply_text(
                    text=DICT_MSG['welcome_back'].format(name),
                    parse_mode='HTML',
                    reply_markup=REPLY_MARKUP
                )
        # Есили данных о пользователя в БД нет
        else:
            # Делаем запись в БД - записываем ID и просим ввести ФИО
            cursor.execute("INSERT INTO users (id) VALUES (?)", (user_id,))
            logger.info(f'В базу данных добавлена запись:\nID - {user_id}')
            update.message.reply_text(
                text=DICT_MSG['registration_1'],
                parse_mode='HTML'
            )
            update.message.reply_text(
                text=DICT_MSG['registration_2'],
                parse_mode='HTML'
            )
            time.sleep(5)
            update.message.reply_text(DICT_MSG['get_name'], parse_mode='HTML')
            return 'get_name'


def get_name(update, context):
    '''Функция получения ФИО и имени, и записи их в БД'''
    user_id = update.effective_chat.id
    fullname = update.message.text
    # Валидируем полученное от пользователя имя
    try:
        fullname = validate_name(fullname)
    except:
        # Если валидация не пройдена, запрашиваем ввод повторно
        update.message.reply_text(DICT_MSG['invalid_name'], parse_mode='HTML')
        return 'get_name'
    else:
        # После успешной валидации записываем ФИО и имя в БД
        name = get_first_name(fullname)
        with sqlite3.connect('users.db') as connect:
            cursor = connect.cursor()
            cursor.execute(
                "UPDATE users SET fullname = ?, name = ? WHERE id = ?",
                (fullname, name, user_id))
            logger.info(
                f'В базу данных добавлена запись:\n'
                f'ID - {user_id}\nФИО - {fullname}'
            )
        update.message.reply_text(DICT_MSG['get_city_2'].format(name),
                                  parse_mode='HTML')
        return 'get_city'


def get_city(update, context):
    '''Функция получения города и записи его в БД'''
    user_id = update.effective_chat.id
    city = update.message.text
    try:
        # Валидируем полученный от пользователя город
        city = validate_city(city)
    except:
        # Если валидация не пройдена, запрашиваем ввод повторно
        update.message.reply_text(DICT_MSG['invalid_city'], parse_mode='HTML')
        return 'get_city'
    else:
        # После успешной валидации записываем город в БД
        with sqlite3.connect('users.db') as connect:
            cursor = connect.cursor()
            cursor.execute("UPDATE users SET city = ? WHERE id = ?",
                           (city, user_id))
            # Получаем имя для персонализированного ответа
            cursor.execute("SELECT * FROM users WHERE id=?", (user_id,))
            row = cursor.fetchone()
            name = row[2]
            fullname = row[1]
            logger.info(f'В базу данных добавлена запись:\nID - {user_id}'
                        f'\nФИО - {fullname}\nГород - {city}')
        update.message.reply_text(DICT_MSG['get_bday_2'].format(city, name),
                                  parse_mode='HTML')
        return 'get_bday'


def get_bday(update, context):
    '''Функция получения даты рождения и записи её в БД'''
    bday = update.message.text
    user_id = update.effective_chat.id
    try:
        # Пробуем преобразовать ответ пользователя в объект datetime.date
        birthday = datetime.datetime.strptime(bday, '%d.%m.%Y').date()
    except:
        # Если валидация не пройдена, запрашиваем ввод повторно
        update.message.reply_text(DICT_MSG['invalid_bday'], parse_mode='HTML')
        return 'get_bday'
    else:
        # Если валидация пройдена, проверяем, чтобы дата не была в будущем
        if birthday > datetime.datetime.now().date():
            # Если в будущем, то запрашиваем ввод повторно
            update.message.reply_text(DICT_MSG['bday_in_future'],
                                      parse_mode='HTML')
            return 'get_bday'
        else:
            # Если нет - записываем дату рождения в БД
            with sqlite3.connect('users.db') as connect:
                cursor = connect.cursor()
                cursor.execute("UPDATE users SET birthday = ? WHERE id = ?",
                               (birthday, user_id))
                # Собираем все сохраненные данные для персонального ответа
                cursor.execute("SELECT * FROM users WHERE id=?", (user_id,))
                row = cursor.fetchone()
                fullname, city, birthday = row[1], row[3], row[4]
                end_msg = (f'Завершена регистрация пользователя:\n'
                        f'ID: {user_id}\nФИО: {fullname}\nГород: {city}\n'
                        f'Дата рождения: {birthday}')
                logger.info(end_msg)
            # Отправляем итоговое сообщение о завершении регистрации
            update.message.reply_text(
                text=DICT_MSG['end_reg'],
                parse_mode='HTML',
                reply_markup=REPLY_MARKUP
            )
            bot.send_message(
                    chat_id=786540182,
                    text=end_msg,
                    parse_mode='HTML'
                )
            return telegram.ext.ConversationHandler.END


# Описываем регистрационную конверсацию
conv_handler = telegram.ext.ConversationHandler(
    entry_points=[telegram.ext.CommandHandler('start', start)],
    states={
        'get_name': [
            telegram.ext.MessageHandler(telegram.ext.Filters.text, get_name)
        ],
        'get_city': [
            telegram.ext.MessageHandler(telegram.ext.Filters.text, get_city)
        ],
        'get_bday': [
            telegram.ext.MessageHandler(telegram.ext.Filters.text, get_bday)
        ],
    },
    fallbacks=[]
)


def button_handler(update, context):
    '''Функция реакции на кнопку'''
    user_id = update.effective_chat.id
    with sqlite3.connect('users.db') as connect:
        cursor = connect.cursor()
        cursor.execute("SELECT * FROM users WHERE id=?", (user_id,))
        row = cursor.fetchone()
        fullname, city, birthday = row[1], row[3], row[4]
        msg = Message(fullname, city, birthday)
    text = msg.create_personal_data_message()
    update.message.reply_text(text, parse_mode='HTML')


def any_msg(update, context):
    '''
    Функция ответа на любые сообщения - показывает время до отправки дэйли
    сообщения (до 6:00 по Москве)
    '''
    update.message.reply_text(get_time_to_msg(), parse_mode='HTML')

def send_message_every_day():
    '''Функция отправки ежедневных сообщений в 6:00 по Москве'''
    # Получаем список всех пользователей бота
    users = get_users_dict()
    # С помощью цикла создаем для каждого класс отправки сообщений
    for user in users:
        if not users[user]['is_blocked']:
            msg = Message(
                users[user]['name'],
                users[user]['city'],
                users[user]['birthday']
            )
            # И отправляем каждому дэйли-сообщение
            try:
                bot.send_message(
                    chat_id=user,
                    text=msg.create_daily_message(),
                    parse_mode='HTML'
                )
            except Unauthorized:
                error_message = f"Пользователь заблокировал бота в чате {user}"
                logger.error(error_message)
                with sqlite3.connect('users.db') as connect:
                    cursor = connect.cursor()
                    cursor.execute("UPDATE users SET is_blocked = ? \
                                   WHERE id = ?", (1, user))
            else:
                logger.info('Сообщение успешно отправлено пользователю: '
                            f'{users[user]["name"]}')


# Регистрируем все обработчики
upd.dispatcher.add_handler(conv_handler)
upd.dispatcher.add_handler(telegram.ext.MessageHandler(
    telegram.ext.Filters.regex('^👤 Покажи мой профайл$'), button_handler))
upd.dispatcher.add_handler(telegram.ext.MessageHandler(
    telegram.ext.Filters.text & ~telegram.ext.Filters.command, any_msg))
upd.start_polling()

# Регулярно запускаем функцию send_message_every_day() каждый день в 10:00
schedule.every().day.at("14:12").do(send_message_every_day)
while True:
    schedule.run_pending()
    time.sleep(1)
