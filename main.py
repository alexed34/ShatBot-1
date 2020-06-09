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


def createParser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--devman', default=os.getenv('DEVMAN_TOKEN'))
    parser.add_argument('-t', '--telegram', default=os.getenv('TELEGRAM_TOKEN'))
    parser.add_argument('-c', '--chat', default=os.getenv('TG_CHAT_ID'))
    parser.add_argument('-f', '--file', default='simple.log')
    return parser

def send_message_bot(TELEGRAM_TOKEN, TG_CHAT_ID, text):
    logger.info('Подключение к telegram-боту')
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    logger.info('Отправка сообщения telegram-боту')
    bot.send_message(chat_id=TG_CHAT_ID, text=text, parse_mode=telegram.ParseMode.HTML)

def greate_log(path_file):
    logger.setLevel(logging.DEBUG)
    f_format = logging.Formatter('%(asctime)s - %(name)s -  %(lineno)d - %(levelname)s - %(message)s')
    file_handler = RotatingFileHandler(path_file, maxBytes=10000, backupCount=2)
    file_handler.setFormatter(f_format)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(f_format)
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)


def check_answer_teacher(check):
    name_lesson = check['new_attempts'][0]['lesson_title']
    verification_results = check['new_attempts'][0]['is_negative']
    if verification_results:
        return f'У вас проверили работу "{name_lesson}" К сожалению, ' \
               f'в работе нашлись ошибки.'
    else:
        return f'У вас проверили работу "{name_lesson}" Преподавателю все понравилось, ' \
               f'можете приступать к следующему уроку.'




def main():
    parser = createParser()
    namespace = parser.parse_args()
    TELEGRAM_TOKEN = namespace.telegram
    DEWMAN_TOKEN = namespace.devman
    TG_CHAT_ID = namespace.chat

    greate_log(namespace.file)

    header = {'Authorization': f'Token {DEWMAN_TOKEN}'}
    params = {'timestamp': ''}

    while True:
        try:
            logger.info('________Отправляем запрос сайту_________')
            check = get_checks_long_polling(header, params).json()
            logger.info(f'Проверяем json ')
            if check['status'] == 'timeout':
                logger.info(f'получен ответ: "status = timeout" проверенных работ нет ')
                timestamp = check['timestamp_to_request']
                params = {'timestamp': timestamp}
            elif check['status'] == 'found':
                logger.info(f'Получен ответ: "status = found" работа проверенна')
                timestamp = check['last_attempt_timestamp']
                params = {'timestamp': timestamp}
                text = check_answer_teacher(check)
                send_message_bot(TELEGRAM_TOKEN, TG_CHAT_ID, text)

        except requests.exceptions.ReadTimeout:
            logger.exception('Increase response time')


        except requests.exceptions.ConnectionError:
            logger.exception(f'No internet or wrong url ')
            time.sleep(5)
        except Exception:
            logger.exception(f'Ошибка ')
            return False


if __name__ == '__main__':
    main()
