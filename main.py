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
logger = logging.getLogger('логер отладки')


def get_checks(headers):
    url = 'https://dvmn.org/api/user_reviews/'
    response = requests.get(url, headers=headers)
    logger.info(f'Ответ сервера: {response.status_code}')
    response.raise_for_status()
    json = response.json()
    if 'error' in json:
        raise requests.exceptions.HTTPError(json['error'])
    return response


def get_checks_long_polling(header, params):
    url = 'https://dvmn.org/api/long_polling/'
    response = requests.get(url, headers=header, params=params)
    logger.info(f'Ответ сервера: {response.status_code}')
    response.raise_for_status()
    json = response.json()
    if 'error' in json:
        raise requests.exceptions.HTTPError(json['error'])
    return response


def create_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--devman', default=os.environ['DEVMAN_TOKEN'])
    parser.add_argument('-t', '--telegram',
                        default=os.environ['TELEGRAM_TOKEN'])
    parser.add_argument('-c', '--chat', default=os.environ['TG_CHAT_ID'])
    parser.add_argument('-f', '--file', default='simple.log')
    return parser


def send_message_bot(TELEGRAM_TOKEN, TG_CHAT_ID, text):
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    bot.send_message(
        chat_id=TG_CHAT_ID,
        text=text
    )


def configure_logging(file_path):
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
    parser = create_parser()
    namespace = parser.parse_args()
    telegram_token = namespace.telegram
    dewman_token = namespace.devman
    tg_chat_id = namespace.chat
    configure_logging(namespace.file)
    header = {'Authorization': f'Token {dewman_token}'}
    params = {'timestamp': ''}

    bot = telegram.Bot(token=telegram_token)

    class MyLogsHandler(logging.Handler):
        def emit(self, record):
            log_entry = self.format(record)
            if len(log_entry) < 4096:
                bot.send_message(chat_id=tg_chat_id, text=log_entry)
            else:
                num = len(log_entry) // 4096 + 1
                start = 0
                finish = 4096
                for i in range(num):
                    text = log_entry[start:finish]
                    bot.send_message(chat_id=tg_chat_id, text=text)
                    start, finish = finish, finish + 4096

    bot_handler = MyLogsHandler()
    bot_handler.setLevel(logging.WARNING)
    logger.addHandler(bot_handler)
    logger.warning('bot start')

    while True:
        try:
            logger.info('________Отправляем запрос сайту devman_________')
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
                send_message_bot(telegram_token, tg_chat_id, text)

        except requests.exceptions.ReadTimeout:
            pass

        except requests.exceptions.ConnectionError:
            logger.exception(f'No internet or wrong url ')
            time.sleep(3600)

        except Exception:
            logger.exception(f'Нестандартная ошибка: ')
            return False


if __name__ == '__main__':
    main()
