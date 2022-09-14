from datetime import datetime, timedelta

import requests
from requests import exceptions

from telebot import TeleBot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

group_id = None


def get_data_groups():
    result = []
    get_data = False
    while not get_data:
        try:
            groups = requests.get(
                'https://edu.donstu.ru/api/raspGrouplist?year=2022-2023').json()
        except exceptions.ConnectionError:
            continue
        get_data = True
        result = [{'name': i['name'], 'id': i['id']} for i in groups['data']]
    return result


def get_timetable(date):
    rasp = []
    data = []
    today = {}
    get_data = False
    while not get_data:
        try:
            rasp = requests.get(
                f'https://edu.donstu.ru/api/Rasp?idGroup={group_id}&date={date}').json()[
                'data']['rasp']
        except exceptions.ConnectionError:
            continue
        get_data = True
    classes = [i for i in rasp if date in i['дата']]
    if classes:
        for i in range(len(classes)):
            data.append({
                classes[i]['номерЗанятия']: {
                    'start': classes[i]['начало'],
                    'end': classes[i]['конец'],
                    'name': classes[i]['дисциплина'],
                    'teacher_name': classes[i]['фиоПреподавателя'],
                    'auditorium': classes[i]['аудитория'],
                }
            })
        today.update({
            classes[0]['день_недели']: data
        })
        return today
    else:
        return False


groups_list = get_data_groups()

bot = TeleBot('5761718381:AAG5vZ-Wc_iokuJZHMV45_B2G7UjQLhzKj4')


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
                         f'Выбрана группа {group}. Выберите действие',
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
    markup1 = InlineKeyboardMarkup()
    markup1.add(InlineKeyboardButton(text='Выбор действия',
                                     callback_data='Выбор действия'))
    markup2 = InlineKeyboardMarkup()
    markup2.add(InlineKeyboardButton(text='Просмотр расписания по дате',
                                     callback_data='Просмотр расписания по дате'))
    markup2.add(InlineKeyboardButton(text='Просмотр расписания на завтра',
                                     callback_data='Просмотр расписания на завтра'))
    if req[0] == 'Просмотр расписания по дате':
        bot.send_message(call.from_user.id,
                         'Введите дату в формате "день.месяц.год"')
        bot.register_next_step_handler(call.message, timetable_date)
    elif req[0] == 'Просмотр расписания на завтра':
        message = timetable_today()
        bot.send_message(call.from_user.id, message, reply_markup=markup1)
    elif req[0] == 'Выбор действия':
        bot.send_message(call.from_user.id, 'Выберите действие',
                         reply_markup=markup2)
    elif req[0] == 'Просмотр расписания':
        pass


@bot.message_handler(content_types=['text'])
def timetable_date(msg):
    global group_id
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton(text='Выбор действия',
                                    callback_data='Выбор действия'))
    try:
        date = str(datetime.strptime(msg.text, '%d.%m.%Y').date())
        timetable = get_timetable(date)
        if timetable:
            day = list(timetable.keys())[0] + '\n'
            message = [day]
            for i in range(len(list(timetable.items())[0])):
                number = list(list(timetable.values())[0][i].keys())[0]
                data = list(timetable.values())[0][i][number]
                start = data['start']
                end = data['end']
                name = data['name']
                teacher_name = data['teacher_name']
                auditorium = data['auditorium']
                message.append(
                    f'{number} пара: \nНачало: {start}\nКонец: {end}\nПара: {name}\nАудитория: {auditorium}\nПреподаватель: {teacher_name}\n')
            message = '\n'.join(message)
            bot.send_message(msg.from_user.id, message, reply_markup=markup)
        else:
            bot.send_message(msg.from_user.id, 'Нет расписания на эту дату.',
                             reply_markup=markup)
    except ValueError:
        retry_msg(msg, 'timetable_date')


def timetable_today():
    today = datetime.now().date()
    tomorrow = str(today + timedelta(1))
    timetable = get_timetable(tomorrow)
    if timetable:
        day = list(timetable.keys())[0] + '\n'
        message = [day]
        for i in range(len(list(timetable.items())[0])):
            number = list(list(timetable.values())[0][i].keys())[0]
            data = list(timetable.values())[0][i][number]
            start = data['start']
            end = data['end']
            name = data['name']
            teacher_name = data['teacher_name']
            auditorium = data['auditorium']
            message.append(
                f'{number} пара: \nНачало: {start}\nКонец: {end}\nПара: {name}\nАудитория: {auditorium}\nПреподаватель: {teacher_name}\n')
        message = '\n'.join(message)
    else:
        message = 'Нет расписания на завтра.'
    return message


bot.polling(none_stop=True, interval=0)
