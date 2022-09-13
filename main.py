import re
from datetime import datetime

import requests
from requests import exceptions

from telebot import TeleBot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

group_id = None

get_group_link = 'https://edu.donstu.ru/api/raspGrouplist?year=2022-2023'


def get_data_groups():
    get_data = False
    while not get_data:
        try:
            groups = requests.get(get_group_link).json()
        except exceptions.ConnectionError:
            continue
        get_data = True
        result = [{'name': i['name'], 'id': i['id']} for i in groups['data']]
    return result


def get_timetable(date):
    get_data = False
    while not get_data:
        try:
            groups = requests.get(requests.get(
                f'https://edu.donstu.ru/api/Rasp?idGroup={group_id}&date={date}').json()).json()
        except exceptions.ConnectionError:
            continue
        get_data = True
    # return result


groups_list = get_data_groups()

bot = TeleBot('5611418224:AAH77nTvbqsiiR4FAcAeH5e11NtcjBViDuw')


@bot.message_handler(content_types=['text'])
def start(msg):
    if msg.text == '/start':
        bot.send_message(msg.from_user.id, 'Введи группу')
        bot.register_next_step_handler(msg, get_group)
    else:
        bot.send_message(msg.from_user.id,
                         'Для перезапуска бота напиши /start')


def get_group(msg):
    global group_id
    group = msg.text
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton(text='Просмотр расписания по дате',
                                    callback_data='Просмотр расписания по дате'))
    markup.add(InlineKeyboardButton(text='Просмотр расписания на завтра',
                                    callback_data='Просмотр расписания на завтра'))
    # markup.add(InlineKeyboardButton(text='Просмотр расписания до конца недели',
    #                                 callback_data='Просмотр расписания до конца недели'))
    try:
        group_id = [i['id'] for i in groups_list if i['name'] == group][0]
        bot.send_message(msg.from_user.id,
                         f'Выбрана группа {group}. Выбери действие',
                         reply_markup=markup)
    except IndexError:
        retry_msg(msg, 'get_group')


@bot.message_handler(content_types=['text'])
def retry_msg(msg, func_name):
    if func_name == 'get_group':
        bot.send_message(msg.from_user.id,
                         'Группа введена неправильно или не существует. \nВведите группу ещё раз')
        bot.register_next_step_handler(msg, get_group)
    elif func_name == 'timetable_date':
        bot.send_message(msg.from_user.id,
                         'Неверная дата. \nВведите ещё раз')
        bot.register_next_step_handler(msg, timetable_date)


@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    req = call.data.split('_')

    if req[0] == 'Просмотр расписания по дате':
        bot.send_message(call.from_user.id,
                         'Выбрано просмотр расписания по дате. Введите дату в формате "31/12/2001"')
        bot.register_next_step_handler(call, timetable_date)

    elif req[0] == 'Просмотр расписания на завтра':
        bot.send_message(call.from_user.id,
                         'Выбрано просмотр расписания на завтра')


@bot.message_handler(content_types=['text'])
def timetable_date(msg):
    global group_id
    try:
        time = datetime.strptime(msg, '%d/%m/%Y')
    except ValueError:
        retry_msg(msg, 'timetable_date')
        pass
    time = re.sub('/', '-', msg)
    get_timetable(time)


bot.polling(none_stop=True, interval=0)
