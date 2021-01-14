from telegram.ext import Updater, CommandHandler
import re
import telebot
from telebot import types
import requests
from bs4 import BeautifulSoup as bs
from config import token
import mysql.connector
import time
import threading

DOLLAR = 'Доллары'

val = []


def conn():
    db = mysql.connector.connect(
        host="us-cdbr-east-02.cleardb.com",
        user="b8a73a66bb115c",
        password="bd06d154",
        database='heroku_ec15006e88f9ba7'
    )
    return db


bot = telebot.TeleBot(token)


class User:
    def __init__(self, name):
        self.name = name
        self.age = None
        self.sex = None


class Cur:
    def __init__(self, cur):
        self.cur = cur
        self.value = None


bot = telebot.TeleBot(token)

user_dict = {}
cur_dict = {}


def rubles():
    features = "html.parser"
    r = requests.get('https://minfin.com.ua/currency/rub/')
    soup = bs(r.content, features)
    title = soup.find('td', {"data-title": "Продажа"}).get_text()
    title = list(title.split())
    rubles = soup.find('span', class_='mfm-posr')
    rubles = rubles.get_text()
    rubles = list(rubles.split())
    return '%(ru).2f / %(sell).2f' % {'ru': float(rubles[0]), 'sell': float(title[0])}


def euro():
    features = "html.parser"
    r = requests.get('https://minfin.com.ua/currency/eur/')
    soup = bs(r.content, features)
    euro = soup.find('span', class_='mfm-posr')
    title = soup.find('td', {"data-title": "Продажа"}).get_text()
    title = list(title.split())
    euro = euro.get_text()
    euro = list(euro.split())
    return '%(eu).2f / %(sell).2f' % {'eu': float(euro[0]), 'sell': float(title[0])}


def parser():
    features = "html.parser"
    r = requests.get('https://minfin.com.ua/currency/usd/')
    soup = bs(r.content, features)
    usd = soup.find('span', class_='mfm-posr')
    title = soup.find('td', {"data-title": "Продажа"}).get_text()
    title = list(title.split())
    usd = usd.get_text()
    usd = list(usd.split())
    print(usd[0], title[0])
    return '%(usd).2f / %(sell).2f' % {'usd': float(usd[0]), 'sell': float(title[0])}


def covid():
    features = "html.parser"
    r = requests.get('https://nv.ua')
    soup = bs(r.content, features)
    stats = soup.find('span', class_='spec-covid-number-increase').get_text()
    return stats[1:]


eu = euro()
stats = covid()
dollar = parser()
ru = rubles()


def add_value(val):
    eu = euro()
    dollar = parser()
    ru = rubles()

    val.append(float(ru[0:5]))
    val.append(float(eu[0:5]))
    val.append(float(dollar[0:5]))


def job():
    add_value(val)
    mydb = conn()
    mycursor = mydb.cursor()
    mycursor.execute("SELECT * FROM users ")
    myresult = mycursor.fetchall()
    cur = {'USD': val[2], 'EURO': val[1], 'Rubles': val[0]}
    print(cur)
    for i in myresult:
        user_id = i[3]
        for j in cur.keys():
            if i[4] == j:
                    if float(i[1]) <= cur.get('USD') and j == 'USD':
                        bot.send_message(user_id, 'Hello, your value was: ' + str(i[1]) + str(i[4]) + ' now is: ' + str(parser()))
                    if float(i[1]) <= cur.get('EURO') and j == 'EURO':
                        bot.send_message(user_id, 'Hello, your value was: ' + str(i[1]) + str(i[4]) + ' now is: ' + str(euro()))
                    if float(i[1]) <= cur.get('Rubles') and j == 'Rubles':
                        bot.send_message(user_id, 'Hello, your value was: ' + str(i[1]) + str(i[4]) + ' now is: ' + str(rubles()))
    time.sleep(60)
    Timer = threading.Thread(target=job)
    Timer.start()


# Handle '/start' and '/help'
@bot.message_handler(commands=['start', 'help'])
def start_message(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    btn_1 = types.KeyboardButton('Маленькие кнопки')
    btn_2 = types.KeyboardButton('Большие кнопки')
    markup.add(btn_1, btn_2)
    bot.send_message(message.chat.id,
                     "Здавствуйте,  " + message.from_user.first_name + '. Выберите желаемый вид кнопок для роботы с ботом:',
                     reply_markup=markup)


@bot.message_handler(commands=['check'])
def check(message):
    t = 0
    add_value(val)
    user = message.from_user.id
    mydb = conn()
    mycursor = mydb.cursor()
    mycursor.execute("SELECT * FROM users WHERE user_id = " + str(user))
    myresult = mycursor.fetchall()
    cur = {'USD': val[0], 'EURO': val[1], 'Rubles': val[2]}
    for i in myresult:
        user_id = int(i[3])
        print(t, len(myresult))
        for j in cur.keys():
            if j == i[4]:
                if i[4] == 'USD':
                    bot.send_message(user_id,
                                     'Your value is ' + str(i[1]) + ' ' + str(i[4]) + ' now is: ' + str(parser()))
                elif i[4] == 'EURO':
                    bot.send_message(user_id,
                                     'Your value is ' + str(i[1]) + ' ' + str(i[4]) + ' now is: ' + str(euro()))
                elif i[4] == 'Rubles':
                    bot.send_message(user_id,
                                     'Your value is ' + str(i[1]) + ' ' + str(i[4]) + ' now is: ' + str(rubles()))
    if not myresult:
        bot.send_message(user, 'You are not registred!')


@bot.message_handler(commands=['reg'])
def asdfg(message):
    msg = bot.reply_to(message, 'Вы выбрали отслеживание курса, как к тебе обращаться? ')
    bot.register_next_step_handler(msg, process_name_step)


def process_name_step(message):
    try:
        chat_id = message.chat.id
        name = message.text
        user = User(name)
        user_dict[chat_id] = user
        msg = bot.reply_to(message, 'Введите желаемый курс валюты, при котором мне нужно вас уведомить')
        bot.register_next_step_handler(msg, process_age_step)
    except Exception as e:
        bot.reply_to(message, 'oooops')


def process_age_step(message):
    try:
        chat_id = message.chat.id
        age = float(message.text)
        print(type(age))
        if type(age) == type(str):
            msg = bot.reply_to(message, 'Здесь должна быть цифр')
            bot.register_next_step_handler(msg, process_age_step)
        user = user_dict[chat_id]
        cur = '%.2f ' % age
        print(cur)
        user.age = age
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        markup.add('USD', 'Rubles', 'EURO')
        msg = bot.reply_to(message, 'What kind of currency do you want to track? ', reply_markup=markup)
        bot.register_next_step_handler(msg, process_sex_step)
    except Exception as e:
        bot.reply_to(message, 'oooops')


def process_sex_step(message):
    try:
        mydb = conn()
        mycursor = mydb.cursor()
        user_id = message.from_user.id
        chat_id = message.chat.id
        sex = message.text
        user = user_dict[chat_id]
        if (sex == 'USD') or (sex == 'EURO') or (sex == 'Rubles'):
            user.sex = sex
        else:
            raise Exception()
        sql = "INSERT INTO users(name, address,user_id,track) VALUES (%s, %s, %s, %s)"
        val = (user.name, user.age, user_id, user.sex)
        mycursor.execute(sql, val)
        mydb.commit()
        bot.send_message(chat_id, 'Nice to meet you ' + user.name + '\n Currency:' + str(user.age) + '\n' + user.sex)
        job()
    except Exception as e:
        job()
        user_id = message.from_user.id
        bot.reply_to(message, 'oooops')


@bot.message_handler(content_types=['text'])
def buttons(message):
    keyboard1 = types.InlineKeyboardMarkup()
    item1 = types.InlineKeyboardButton(text='Да', callback_data='Clean')
    item2 = types.InlineKeyboardButton(text='Нет', callback_data='Минфин')
    keyboard1.add(item1, item2)
    if message.text == 'Маленькие кнопки':
        bot.send_message(message.chat.id, 'Хотите убрать большие кнопки?', reply_markup=keyboard1)
    if message.text == 'Большие кнопки':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        btn_1 = types.KeyboardButton('Доллары')
        btn_2 = types.KeyboardButton('Евро')
        btn_3 = types.KeyboardButton('Рубли')
        btn_4 = types.KeyboardButton('Covid')
        btn_5 = types.KeyboardButton('Слежение')
        btn_6 = types.KeyboardButton('Конвертор')
        markup.add(btn_1, btn_2, btn_3, btn_4, btn_5, btn_6)
        bot.send_message(message.chat.id, 'Выберите желаемый курс валют:',
                         reply_markup=markup)
    if message.text == 'Доллары':
        bot.send_message(message.chat.id, dollar)
    if message.text == 'Евро':
        bot.send_message(message.chat.id, eu)
    if message.text == 'Рубли':
        bot.send_message(message.chat.id, ru)
    if message.text == 'Covid':
        bot.send_message(message.chat.id, stats)
    if message.text == 'Слежение':
        asdfg(message)
    if message.text == 'Конвертор':
        first_step(message)


def first_step(message):
    msg = bot.reply_to(message, 'Введите сумму, котору. нужно конвертировать: ')
    bot.register_next_step_handler(msg, currency_step)


def currency_step(message):
    try:
        cur = message.text
        chat_id = message.chat.id
        currency = Cur(cur)
        cur_dict[chat_id] = currency
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2, one_time_keyboard=True)
        btn_1 = types.KeyboardButton(DOLLAR)
        btn_2 = types.KeyboardButton('Евро')
        btn_3 = types.KeyboardButton('Рубли')
        markup.add(btn_1, btn_2, btn_3)
        msg = bot.send_message(message.chat.id, 'Выберите желаемый курс валют:',
                               reply_markup=markup)
        bot.register_next_step_handler(msg, final_step)
    except Exception as e:
        bot.reply_to(message, 'oooops')


def final_step(message):
    usd = float(dollar[0:5])
    euro = float(eu[0:5])
    rub = float(ru[0:5])
    value = message.text
    chat_id = message.chat.id
    cur = cur_dict[chat_id]
    if value == DOLLAR:
        bot.send_message(chat_id, float(cur.cur) * usd)
    if value == 'Евро':
        bot.send_message(chat_id, float(cur.cur) * euro)
    if value == 'Рубли':
        bot.send_message(chat_id, float(cur.cur) * rub)


@bot.callback_query_handler(func=lambda c: True)
def ukraine(c):
    if c.data == 'Минфин':
        key = types.InlineKeyboardMarkup()
        but_1 = types.InlineKeyboardButton(text='Курс доллара', callback_data='three_hundred_bucks')
        but_2 = types.InlineKeyboardButton(text='Курс евро', callback_data='eu')
        but_5 = types.InlineKeyboardButton(text="Сайт минфин", url="https://minfin.com.ua/")
        but_3 = types.InlineKeyboardButton(text='Ковид', callback_data='cov_19')
        but_4 = types.InlineKeyboardButton(text='Курс рубля', callback_data='ru')
        but_6 = types.InlineKeyboardButton(text='Cлежение', callback_data='tracking')
        but_7 = types.InlineKeyboardButton(text='Конвертор', callback_data='conv')
        key.add(but_1, but_2, but_5, but_3, but_4, but_6, but_7)
        bot.send_message(c.message.chat.id, 'Выберите желаемый курс валют:', reply_markup=key)
    if c.data == 'Clean':
        clean = types.ReplyKeyboardRemove()
        bot.send_message(c.message.chat.id, 'Убираю кнопки', reply_markup=clean)
        c.data = 'Минфин'
        ukraine(c)
    if c.data == 'three_hundred_bucks':
        bot.send_message(c.message.chat.id, dollar)
        c.data = 'Минфин'
        ukraine(c)
    elif c.data == 'eu':
        bot.send_message(c.message.chat.id, eu)
        c.data = 'Минфин'
        ukraine(c)
    elif c.data == 'cov_19':
        bot.send_message(c.message.chat.id, stats)
        c.data = 'Минфин'
        ukraine(c)
    elif c.data == 'ru':
        bot.send_message(c.message.chat.id, ru)
        c.data = 'Минфин'
        ukraine(c)
    elif c.data == 'tracking':
        asdfg(c.message)


# Enable saving next step handlers to file "./.handlers-saves/step.save".
# Delay=2 means that after any change in next step handlers (e.g. calling register_next_step_handler())
# saving will hapen after delay 2 seconds.
bot.enable_save_next_step_handlers(delay=2)

# Load next_step_handlers from save file (default "./.handlers-saves/step.save")
# WARNING It will work only if enable_save_next_step_handlers was called!
bot.load_next_step_handlers()

bot.polling()
