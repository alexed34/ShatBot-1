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
loggert_my = logging.getLogger('логер отладки')


def get_checks(headers):
    url = 'https://dvmn.org/api/user_reviews/'
    response = requests.get(url, headers=headers)
    loggert_my.info(f'Ответ сервера: {response.status_code}')
    response.raise_for_status()
    json_data = response.json()
    if 'error' in json_data:
        raise requests.exceptions.HTTPError(json_data['error'])
    return response


def get_checks_long_polling(header, params):
    url = 'https://dvmn.org/api/long_polling/'
    response = requests.get(url, headers=header, params=params)
    loggert_my.info(f'Ответ сервера: {response.status_code}')
    response.raise_for_status()
    json_data = response.json()
    if 'error' in json_data:
        raise requests.exceptions.HTTPError(json_data['error'])
    return response


def heroku_create_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--devman', default=os.environ['DEVMAN_TOKEN'])
    parser.add_argument('-t', '--telegram',
                        default=os.environ['TELEGRAM_TOKEN'])
    parser.add_argument('-c', '--chat', default=os.environ['TG_CHAT_ID'])
    parser.add_argument('-f', '--file', default='simple.log')
    return parser


def send_message_bot(TELEGRAM_TOKEN, TG_CHAT_ID, text):
    loggert_my.info('Подключение к telegram-боту')
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    loggert_my.info('Отправка сообщения telegram-боту')
    bot.send_message(
        chat_id=TG_CHAT_ID,
        text=text
    )


def create_log(file_path):
    loggert_my.setLevel(logging.DEBUG)
    f_format = logging.Formatter(
        '%(asctime)s - %(name)s -  %(lineno)d - %(levelname)s - %(message)s')
    file_handler = RotatingFileHandler(file_path, maxBytes=10000, backupCount=2)
    file_handler.setFormatter(f_format)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(f_format)
    loggert_my.addHandler(file_handler)
    loggert_my.addHandler(console_handler)


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
    parser = heroku_create_parser()
    namespace = parser.parse_args()
    TELEGRAM_TOKEN = namespace.telegram
    DEWMAN_TOKEN = namespace.devman
    TG_CHAT_ID = namespace.chat
    create_log(namespace.file)
    header = {'Authorization': f'Token {DEWMAN_TOKEN}'}
    params = {'timestamp': ''}

    bot_log = telegram.Bot(token=TELEGRAM_TOKEN)

    class MyLogsHandler(logging.Handler):
        def emit(self, record):
            log_entry = self.format(record)
            bot_log.send_message(chat_id=TG_CHAT_ID, text=log_entry)

    logger = logging.getLogger('Bot_loger')
    logger.setLevel(logging.WARNING)
    logger.addHandler(MyLogsHandler())
    logger.warning('bot start')

    while True:
        try:
            loggert_my.info('________Отправляем запрос сайту Heroku_________')
            check = get_checks_long_polling(header, params).json()
            loggert_my.info(f'Проверяем json ')
            if check['status'] == 'timeout':
                loggert_my.info(
                    f'получен ответ: "status = timeout" проверенных работ нет')
                timestamp = check['timestamp_to_request']
                params = {'timestamp': timestamp}
            elif check['status'] == 'found':
                loggert_my.info(
                    f'Получен ответ: "status = found" работа проверенна{check}')
                timestamp = check['last_attempt_timestamp']
                params = {'timestamp': timestamp}
                text = get_checked_text(check)
                send_message_bot(TELEGRAM_TOKEN, TG_CHAT_ID, text)

        except requests.exceptions.ReadTimeout:
            pass

        except requests.exceptions.ConnectionError:
            logger.exception(f'No internet or wrong url ')
            loggert_my.exception(f'No internet or wrong url ')
            time.sleep(5)

        except Exception:
            logger.exception(f'Ошибка ')
            loggert_my.exception(f'Ошибка ')
            return False


if __name__ == '__main__':
    main()
