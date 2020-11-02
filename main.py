
from telegram.ext import Updater, CommandHandler
import requests
import re
import telebot
from telebot import types
import requests
from bs4 import BeautifulSoup as bs


bot = telebot.TeleBot('804820292:AAGaG8ZzsTGuIxcmQ_nSK_ibVnJNal1CNZ4')

def rubles():
    features = "html.parser"
    r = requests.get('https://minfin.com.ua/currency/rub/')
    soup = bs(r.content,features)
    title = soup.find('td', {"data-title" : "Продажа"}).get_text()
    title = list(title.split())
    rubles = soup.find('span', class_='mfm-posr')
    rubles = rubles.get_text()
    rubles = list(rubles.split())
    return rubles[0] + ' / ' + title[0]



def euro():

    features = "html.parser"
    r = requests.get('https://minfin.com.ua/currency/eur/')
    soup = bs(r.content,features)
    euro = soup.find('span', class_='mfm-posr')
    title = soup.find('td', {"data-title": "Продажа"}).get_text()
    title = list(title.split())
    euro = euro.get_text()
    euro = list(euro.split())
    return euro[0] + ' / ' + title[0]

def parser():

    features = "html.parser"
    r = requests.get('https://minfin.com.ua/')
    soup = bs(r.content,features)
    classes = soup.find("span", class_="mf-currency-bid")
    i = classes.next_sibling
    for t in range(3):
        i = i.next_sibling
        if t == 2:
            i = i.get_text()
            i = list(i.split())
    dollar = classes.get_text()
    dollar = dollar.replace(',', '.')
    dollar = list(dollar.split())
    return i[0] + ' / ' + dollar[0]

def covid():

    features = "html.parser"
    r = requests.get('https://nv.ua')
    soup = bs(r.content,features)
    stats = soup.find('span', class_='spec-covid-number-increase').get_text()
    return stats[1:]

eu = euro()
stats = covid()
dollar = parser()
ru = rubles()


@bot.message_handler(commands=['start'])
def start_message(message):

    keyboard1 = types.InlineKeyboardMarkup()
    item1 = types.InlineKeyboardButton(text="Выберите желаемое действие", callback_data="Минфин")
    keyboard1.add(item1)
    bot.send_message(message.chat.id, 'Привет, ты написал мне /start', reply_markup=keyboard1)

@bot.message_handler(content_types=['text'])


def send_text(message):
    if message.text.lower() == 'привет':
        bot.send_message(message.chat.id, 'Привет')
    elif message.text.lower() == 'пока':
        bot.send_message(message.chat.id, 'Прощай, создатель')
    elif message.text.lower() == 'чиназес':
        bot.send_sticker(message.chat.id, 'CAACAgIAAxkBAAIFb1-IKh6jPxgXmOntGax4RoU1Yuz1AAIDAAMr0dgRkFOdcR-6RcMbBA')
    elif message.text.lower() == 'кот':
        bot.send_sticker(message.chat.id, 'CAACAgIAAxkBAAIFil-ILC5etibVstMTyOtagKKP3MG9AAIsAAMUnIcX8F2Xag3zTYwbBA')


@bot.message_handler(content_types=['sticker'])
def sticker_id(message):
    print(message)

@bot.callback_query_handler(func=lambda c:True)

def ukraine(c):
   if c.data == 'Минфин':
        key = types.InlineKeyboardMarkup()
        but_1 = types.InlineKeyboardButton(text='Курс доллара', callback_data='three_hundred_bucks')
        but_2 = types.InlineKeyboardButton(text='Курс евро', callback_data='eu')
        but_5 = types.InlineKeyboardButton(text="Сайт минфин", url="https://minfin.com.ua/")
        but_3 = types.InlineKeyboardButton(text='Ковид', callback_data='cov_19')
        but_4 = types.InlineKeyboardButton(text='Курс рубля', callback_data='ru')
        key.add(but_1,but_2, but_5,but_3,but_4)
        bot.send_message(c.message.chat.id, 'Оберіть будь ласка розділ який Вас цікавить: ', reply_markup=key)
   elif c.data == 'three_hundred_bucks':
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



bot.polling()