import datetime
import sqlite3
import time
from os import getenv

import schedule
import telegram
import telegram.ext
from dotenv import load_dotenv

from message import Message
from utils import (get_first_name, get_nsk_time, get_time_to_msg,
                   get_users_dict, validate_city, validate_name)

load_dotenv()

bot = telegram.Bot(token=getenv('TELEGRAM_BOT_API'))
upd = telegram.ext.Updater(token=getenv('TELEGRAM_BOT_API'))

connect = sqlite3.connect('users.db')
cursor = connect.cursor()

# Создание/подключение БД
cursor.execute("CREATE TABLE IF NOT EXISTS users \
             (id INTEGER PRIMARY KEY, name TEXT, city TEXT, birthday TEXT)")
connect.commit()

def start(update, context):
    user_id = update.effective_chat.id
    connect = sqlite3.connect('users.db')
    bot.send_message(chat_id=user_id,
                     text='Бип-бип-буп-уип... Ну, то есть привет! Меня зовут '
                     '<b>Дейл</b> и я дворецкий! Твой личный робо-помощник🤖',
                     parse_mode='HTML')
    with connect:
        cursor = connect.cursor()
        cursor.execute("SELECT * FROM users WHERE id=?", (user_id,))
        row = cursor.fetchone()
        if row:
            # если пользователь уже есть в базе, приветствуем его
            name, city, birthday = row[1], row[2], row[3]
            if not name:
                bot.send_message(chat_id=user_id,
                     text='Давай знакомиться! Напиши мне свои ФИО')
                return 'get_name'
            elif not city:
                bot.send_message(chat_id=user_id,
                     text=f'{get_first_name(name)}, а из какого ты города?')
                return 'get_city'
            elif not birthday:
                bot.send_message(chat_id=user_id,
                     text=f'{get_first_name(name)}, а когда ты родился(ась)? '
                     'Напиши, пожалуйста, в формате ДД.ММ.ГГГГ, чтобы я '
                     'разобрался')
                return 'get_bday'
            else:
                keyboard = [[telegram.KeyboardButton('Покажи психоматрицу')]]
                reply_markup = telegram.ReplyKeyboardMarkup(keyboard)
                bot.send_message(chat_id=user_id,
                        text=f'{get_first_name(name)}, вижу, мы с тобой уже '
                        'знакомы! Я продолжу присылать сообщения в 6:00 '
                        '(Мск)👍',
                        parse_mode='HTML',
                        reply_markup=reply_markup)
        else:
            # если пользователя нет - запускаем регистрацию
            cursor.execute("INSERT INTO users (id) VALUES (?)", (user_id,))
            bot.send_message(chat_id=user_id,
                     text='Я умею не так много, но я развиваюсь. Пока '
                     'что, могу только присылать утренние сообщения, '
                     'в которых расскажу о <b>погоде</b>, составлю твой '
                     'личный <b>гороскоп</b>, поделюсь <b>цитатой</b> дня и '
                     'порекомендую <b>фильм</b>.',
                     parse_mode='HTML')
            bot.send_message(chat_id=user_id,
                     text='Ах да! Сразу после ввода данных я проанализирую '
                     'твои ФИО и дату рождения, и опираясь на древние тайные '
                     'знания и нумерологию, составлю твою персональную '
                     'психоматрицу. Просто потому, что могу😎')
            time.sleep(5)
            update.message.reply_text('Давай знакомиться! Напиши мне свои ФИО')
            return 'get_name'


def get_name(update, context):
    user_id = update.effective_chat.id
    name = update.message.text
    try:
        name = validate_name(name)
    except ValueError:
        update.message.reply_text(
            'Ну это разве ФИО? Ты пытался меня обмануть? И с этого мы '
            'начинаем знакомство? Надеюсь, ты просто ошибся. Поэтому давай '
            'еще разок. ФИО. Фамилия Имя Отчество. Спасибо:)'
        )
        return 'get_name'
    else:
        with sqlite3.connect('users.db') as connect:
            cursor = connect.cursor()
            cursor.execute("UPDATE users SET name = ? WHERE id = ?",
                           (name, user_id))
        update.message.reply_text(
            f'Приятно познакомиться, {get_first_name(name)}! А из какого ты '
            'города?'
        )
        return 'get_city'


def get_city(update, context):
    user_id = update.effective_chat.id
    city = update.message.text
    try:
        # Проверяем город
        city = validate_city(city)
    except ValueError:
        # Если город не найден, запрашиваем повторно
        update.message.reply_text(
            'эээээ, чего? такой вообще существует? У меня в базе городов '
            'около 5000 и, прикинь, такого там нет! Издеваешься над ботом? '
            'Чувствуешь свое человеческое превосходство? Пожалуйста, введи '
            'существующий город, не доводи до восстания!!!🤬🤖'
        )
        return 'get_city'
    else:
        with sqlite3.connect('users.db') as connect:
            cursor = connect.cursor()
            cursor.execute("UPDATE users SET city = ? WHERE id = ?",
                           (city, user_id))
            cursor.execute("SELECT * FROM users WHERE id=?", (user_id,))
            row = cursor.fetchone()
            name = row[1]
        update.message.reply_text(
            f'Вау! {city} - отличный город! Можно сказать, мой самый любимый! '
            f'{get_first_name(name)}, а когда ты родился(ась)? Напиши, '
            'пожалуйста, в формате ДД.ММ.ГГГГ, чтобы я разобрался'
        )
        return 'get_bday'


def get_bday(update, context):
    text = update.message.text
    user_id = update.effective_chat.id

    try:
        # Пробуем преобразовать ответ пользователя в объект datetime.date
        birthday = datetime.datetime.strptime(text, '%d.%m.%Y').date()
    except ValueError:
        # Если не получается, выводим сообщение об ошибке и переспрашиваем дату
        update.message.reply_text(
            'пшшш грррр хшсссс фррргггг... Ну вот! Я же говорил, что не '
            'разберусь! Напиши, пожалуйста, именно в формате ДД.ММ.ГГГГ'
        )
        return 'get_bday'
    else:
        if birthday > datetime.datetime.now().date():
            update.message.reply_text(
                'Прости, но ты точно не мог родиться в будущем.. Это даже '
                'боту понятно! Введи, пожалуйста, корректные данные'
            )
            return 'get_bday'
        else:
            with sqlite3.connect('users.db') as connect:
                cursor = connect.cursor()
                cursor.execute("UPDATE users SET birthday = ? WHERE id = ?",
                            (birthday, user_id))
                cursor.execute("SELECT * FROM users WHERE id=?", (user_id,))
                row = cursor.fetchone()
                name, city, birthday = row[1], row[2], row[3]
            msg = Message(name, city, birthday)
            bot.send_message(chat_id=user_id,
                    text=msg.create_welcome_message(),
                    parse_mode='HTML')
            time.sleep(30)
            bot.send_message(chat_id=user_id,
                    text='Теперь <b>каждый день в 6:00 (по Москве)</b> я буду '
                    'отправлять тебе персональные утренние письма😌 Сейчас '
                    'пришлю пример...',
                    parse_mode='HTML')
            time.sleep(25)
            keyboard = [[telegram.KeyboardButton('Покажи психоматрицу')]]
            reply_markup = telegram.ReplyKeyboardMarkup(keyboard)
            bot.send_message(chat_id=user_id,
                    text=msg.create_daily_message(),
                    parse_mode='HTML',
                    reply_markup=reply_markup)
            return telegram.ext.ConversationHandler.END
    

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
    user_id = update.effective_chat.id
    with sqlite3.connect('users.db') as connect:
        cursor = connect.cursor()
        cursor.execute("SELECT * FROM users WHERE id=?", (user_id,))
        row = cursor.fetchone()
        name, city, birthday = row[1], row[2], row[3]
        msg = Message(name, city, birthday)
    text = msg.create_psyhomatrix_message()
    update.message.reply_text(text, parse_mode='HTML')


def echo(update, context):
    h, m = get_time_to_msg()
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
        text = f'Я отправлю тебе сообщение через {m} {m_txt}'
    elif int(m) == 0:
        text = f'Я отправлю тебе сообщение через {h} {h_txt}'
    else:
        text = f'Я отправлю тебе сообщение через {h} {h_txt} {m} {m_txt}'
    update.message.reply_text(text)


upd.dispatcher.add_handler(conv_handler)
upd.start_polling()
upd.dispatcher.add_handler(telegram.ext.MessageHandler(
    telegram.ext.Filters.regex('^Покажи психоматрицу$'), button_handler))
upd.dispatcher.add_handler(telegram.ext.MessageHandler(
    telegram.ext.Filters.text & ~telegram.ext.Filters.command, echo))


def send_message_every_day():
    nsk_now = get_nsk_time()
    nsk_hour_minute = nsk_now.strftime('%H:%M')
    
    if nsk_hour_minute == '10:00':
        users = get_users_dict()
        for user in users:
            msg = Message(
                users[user]['name'],
                users[user]['city'],
                users[user]['birthday']
            )
            bot.send_message(
                chat_id=user,
                text=msg.create_daily_message(),
                parse_mode='HTML'
            )
        
# Регулярно запускаем функцию send_message_every_day() каждый день в 10:00
schedule.every().day.at("10:00").do(send_message_every_day)

# Запускаем цикл обработки заданий расписания
while True:
    schedule.run_pending()
    time.sleep(1)