import argparse
import logging
import os
import sys
import time
from logging.handlers import RotatingFileHandler

import requests
import telegram
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)


def get_checks(headers):
    url = 'https://dvmn.org/api/user_reviews/'
    response = requests.get(url, headers=headers)
    logger.info(f'Ответ сервера: {response.status_code}')
    response.raise_for_status()
    json_data = response.json()
    if 'error' in json_data:
        raise requests.exceptions.HTTPError(json_data['error'])
    return response


def get_checks_long_polling(header, params):
    url = 'https://dvmn.org/api/long_polling/'
    response = requests.get(url, headers=header, params=params)
    logger.info(f'Ответ сервера: {response.status_code}')
    response.raise_for_status()
    json_data = response.json()
    if 'error' in json_data:
        raise requests.exceptions.HTTPError(json_data['error'])
    return response


def create_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--devman', default=os.getenv('DEVMAN_TOKEN'))
    parser.add_argument('-t', '--telegram', default=os.getenv('TELEGRAM_TOKEN'))
    parser.add_argument('-c', '--chat', default=os.getenv('TG_CHAT_ID'))
    parser.add_argument('-f', '--file', default='simple.log')
    return parser

def heroku_create_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--devman', default=os.environ['DEVMAN_TOKEN'])
    parser.add_argument('-t', '--telegram', default=os.environ['TELEGRAM_TOKEN'])
    parser.add_argument('-c', '--chat', default=os.environ['TG_CHAT_ID'])
    parser.add_argument('-f', '--file', default='simple.log')
    return parser


def send_message_bot(TELEGRAM_TOKEN, TG_CHAT_ID, text):
    logger.info('Подключение к telegram-боту')
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    logger.info('Отправка сообщения telegram-боту')
    bot.send_message(
        chat_id=TG_CHAT_ID,
        parse_mode=telegram.ParseMode.HTML,
        text=text
    )


def create_log(file_path):
    logger.setLevel(logging.DEBUG)
    f_format = logging.Formatter(
        '%(asctime)s - %(name)s -  %(lineno)d - %(levelname)s - %(message)s')
    file_handler = RotatingFileHandler(file_path, maxBytes=10000, backupCount=2)
    file_handler.setFormatter(f_format)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(f_format)
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)


def get_checked_text(check):
    new_attempts = check['new_attempts'][0]
    name_lesson = new_attempts['lesson_title']
    answer_template = f'У вас проверили работу "{name_lesson}" '
    verification_results = new_attempts['is_negative']
    if verification_results:
        return f'{answer_template} К сожалению, в работе нашлись ошибки.'
    else:
        return f'{answer_template} Преподавателю все понравилось, ' \
               f'можете приступать к следующему уроку.'


def main():
    #parser = create_parser()
    parser = heroku_create_parser()
    namespace = parser.parse_args()
    TELEGRAM_TOKEN = namespace.telegram
    DEWMAN_TOKEN = namespace.devman
    TG_CHAT_ID = namespace.chat

    create_log(namespace.file)

    header = {'Authorization': f'Token {DEWMAN_TOKEN}'}
    params = {'timestamp': ''}

    while True:
        try:
            logger.info('________Отправляем запрос сайту_________')
            check = get_checks_long_polling(header, params).json()
            logger.info(f'Проверяем json ')
            if check['status'] == 'timeout':
                logger.info(
                    f'получен ответ: "status = timeout" проверенных работ нет')
                timestamp = check['timestamp_to_request']
                params = {'timestamp': timestamp}
            elif check['status'] == 'found':
                logger.info(
                    f'Получен ответ: "status = found" работа проверенна{check}')
                timestamp = check['last_attempt_timestamp']
                params = {'timestamp': timestamp}
                text = get_checked_text(check)
                send_message_bot(TELEGRAM_TOKEN, TG_CHAT_ID, text)

        except requests.exceptions.ReadTimeout:
            pass

        except requests.exceptions.ConnectionError:
            logger.exception(f'No internet or wrong url ')
            time.sleep(5)

        except Exception:
            logger.exception(f'Ошибка ')
            return False


if __name__ == '__main__':
    main()
