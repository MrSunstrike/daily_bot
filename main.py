import telegram, telegram.ext
from os import getenv
from dotenv import load_dotenv
import sqlite3
import schedule
import datetime
import threading

load_dotenv()

bot = telegram.Bot(token=getenv('TELEGRAM_BOT_API'))
upd = telegram.ext.Updater(token=getenv('TELEGRAM_BOT_API'))

connect = sqlite3.connect('users.db')
cursor = connect.cursor()

# Создание таблицы users, если она не существует
cursor.execute('''CREATE TABLE IF NOT EXISTS users
             (id INTEGER PRIMARY KEY, name TEXT, birthday TEXT)''')

connect.commit()

def start(update, context):
    user_id = update.effective_chat.id
    conn = sqlite3.connect('users.db')
    with conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE id=?", (user_id,))
        row = cursor.fetchone()
        if row:
            # пользователь уже есть в базе данных
            name, birthday = row[1], row[2]
            update.message.reply_text(f'Привет, {name}! Рад, что ты снова с '
                                      'нами.')
        else:
            # пользователь новый, запускаем диалоговую форму для ввода ФИО и даты рождения
            update.message.reply_text('Привет! Как тебя зовут?')
            return 'get_name'

def get_name(update, context):
    global name
    name = update.message.text
    update.message.reply_text(f'Приятно познакомиться, {name}! Когда ты '
                              'родился(ась)? (в формате ДД.ММ.ГГГГ)')
    return 'get_birthday'

lock = threading.Lock()

# в функции get_birthday() захватываем блокировку перед использованием cursor
def get_birthday(update, context):
    global birthday, user_id
    text = update.message.text
    user_id = update.effective_chat.id
    try:
        # Пробуем преобразовать ответ пользователя в объект datetime.date
        birthday = datetime.datetime.strptime(text, '%d.%m.%Y').date()
    except ValueError:
        # Если не получается, выводим сообщение об ошибке и переспрашиваем ввод даты
        update.message.reply_text('Некорректный формат даты. Пожалуйста, '
                                  'введите дату в формате ДД.ММ.ГГГГ')
        return 'get_birthday'
    else:
        conn = sqlite3.connect('users.db')
        with conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO users (id, name, birthday) VALUES \
                           (?, ?, ?)", (user_id, name, birthday))
        update.message.reply_text(f'Отлично, {name}! Ты родился(ась) '
                                  f'{birthday.strftime("%d.%m.%Y")}.')
        return telegram.ext.ConversationHandler.END
    

conv_handler = telegram.ext.ConversationHandler(
    entry_points=[telegram.ext.CommandHandler('start', start)],
    states={
        'get_name': [telegram.ext.MessageHandler(telegram.ext.Filters.text,
                                                 get_name)],
        'get_birthday': [telegram.ext.MessageHandler(telegram.ext.Filters.text,
        get_birthday)],
    },
    fallbacks=[]
)

upd.dispatcher.add_handler(conv_handler)
upd.start_polling()