import logging
import time

import requests
import telegram
from telegram.error import TelegramError

import settings

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s::%(levelname)s::%(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)


def parse_homework_status(homework):
    try:
        homework_name = homework['homework_name']
        homework_status = homework['status']
    except KeyError as e:
        raise Exception(
            f'в ответе сервера не найдено поле {e}')
    homework_checked_answer = f'У вас проверили работу "{homework_name}"!\n\n'
    statuses_anwsers = {
        'reviewing': f'Работа "{homework_name}" взята в ревью',
        'rejected': (f'{homework_checked_answer}'
                     'К сожалению в работе нашлись ошибки.'),
        'approved': (f'{homework_checked_answer}'
                     'Ревьюеру всё понравилось, '
                     'можно приступать к следующему уроку.')
    }
    try:
        return statuses_anwsers[homework_status]
    except KeyError as e:
        raise Exception(f'не распознан статус проверки работы: {e}')


def get_homework_statuses(current_timestamp):
    headers = {
        'Authorization': f'OAuth {settings.PRAKTIKUM_TOKEN}'
    }
    params = {
        'from_date': current_timestamp
    }
    try:
        homework_statuses = requests.get(
            f'{settings.API_URL}homework_statuses/',
            headers=headers, params=params)
    except Exception as e:
        raise Exception(f'при обращении к API произошла ошибка: {e}')
    return homework_statuses.json()


def send_message(message, bot_client):
    logging.info('Отправка сообщения пользователю. '
                 f'ID пользователя: {settings.CHAT_ID}.'
                 f'Сообщение: {message}')
    return bot_client.send_message(settings.CHAT_ID, message)


def main():
    try:
        bot_client = telegram.Bot(settings.TELEGRAM_TOKEN)
    except TelegramError as e:
        logging.error(f'Не удалось инициализировать бота: {e}')
        return
    logging.debug('Бот запущен')
    current_timestamp = int(time.time())
    while True:
        try:
            new_homework = get_homework_statuses(current_timestamp)
            homeworks = new_homework.get('homeworks')
            if homeworks:
                send_message(
                    parse_homework_status(homeworks[0]), bot_client)
            current_timestamp = new_homework.get(
                'current_date', current_timestamp)
            time.sleep(300)
        except Exception as e:
            error_text = f'Бот столкнулся с ошибкой: {e}'
            try:
                send_message(error_text)
            finally:
                logging.error(error_text)
            time.sleep(5)


if __name__ == '__main__':
    main()
