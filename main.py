import time

import requests
from requests import exceptions

from telebot import TeleBot

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


groups_list = get_data_groups()

bot = TeleBot('5611418224:AAH77nTvbqsiiR4FAcAeH5e11NtcjBViDuw')


@bot.message_handler(content_types=['text'])
def start(msg):
    if msg.text == '/start':
        bot.send_message(msg.from_user.id, 'Введи группу')
        bot.register_next_step_handler(msg, get_group)
    else:
        bot.send_message(msg.from_user.id, 'Напиши /start')


def get_group(msg):
    global group_id
    group = msg.text
    error = True
    while error:
        try:
            group_id = [i['id'] for i in groups_list if i['name'] == group][0]
        except IndexError:
            bot.send_message(msg.from_user.id, 'Группа введена неправильно или не существует')
            bot.send_message(msg.from_user.id, 'Введите группу ещё раз')
            error = True
            continue
        error = False
    bot.send_message(msg.from_user.id, f'Выбранна групппа {group}')


bot.polling(none_stop=True, interval=0)
