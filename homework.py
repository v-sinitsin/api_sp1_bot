import logging
import os
import time

import requests
import telegram
from dotenv import load_dotenv

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s::%(levelname)s::%(message)s',
    datefmt='%Y-%m-%d %H-%M-%S'
)

load_dotenv()


PRAKTIKUM_TOKEN = os.getenv("PRAKTIKUM_TOKEN")
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')


def parse_homework_status(homework):
    homework_name = homework.get('homework_name')
    homework_status = homework.get('status')
    if homework_status == 'reviewing':
        return f'Работа "{homework_name}" взята в ревью'
    if homework_status == 'rejected':
        verdict = 'К сожалению в работе нашлись ошибки.'
    else:
        verdict = ('Ревьюеру всё понравилось, '
                   'можно приступать к следующему уроку.')
    return f'У вас проверили работу "{homework_name}"!\n\n{verdict}'


def get_homework_statuses(current_timestamp):
    url = 'https://praktikum.yandex.ru/api/user_api/homework_statuses/'
    headers = {
        'Authorization': f'OAuth {PRAKTIKUM_TOKEN}'
    }
    params = {
        'from_date': current_timestamp
    }
    homework_statuses = requests.get(url, headers=headers, params=params)
    return homework_statuses.json()


def send_message(message, bot_client):
    logging.info('Отправка сообщения пользователю. '
                 f'ID пользователя: {CHAT_ID}.'
                 f'Сообщение: {message}')
    return bot_client.send_message(CHAT_ID, message)


def main():
    bot_client = telegram.Bot(TELEGRAM_TOKEN)
    logging.debug('Бот запущен')
    current_timestamp = int(time.time())
    while True:
        try:
            new_homework = get_homework_statuses(current_timestamp)
            if new_homework.get('homeworks'):
                send_message(
                    parse_homework_status(
                        new_homework.get('homeworks')[0]), bot_client)
            current_timestamp = new_homework.get(
                'current_date', current_timestamp)
            time.sleep(300)

        except Exception as e:
            logging.error(f'Бот столкнулся с ошибкой: {e}')
            time.sleep(5)


if __name__ == '__main__':
    main()
