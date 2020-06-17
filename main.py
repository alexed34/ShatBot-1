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
my_logger = logging.getLogger('логер отладки')


def get_checks(headers):
    url = 'https://dvmn.org/api/user_reviews/'
    response = requests.get(url, headers=headers)
    my_logger.info(f'Ответ сервера: {response.status_code}')
    response.raise_for_status()
    json_data = response.json()
    if 'error' in json_data:
        raise requests.exceptions.HTTPError(json_data['error'])
    return response


def get_checks_long_polling(header, params):
    url = 'https://dvmn.org/api/long_polling/'
    response = requests.get(url, headers=header, params=params)
    my_logger.info(f'Ответ сервера: {response.status_code}')
    response.raise_for_status()
    json_data = response.json()
    if 'error' in json_data:
        raise requests.exceptions.HTTPError(json_data['error'])
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


def create_log(file_path):
    my_logger.setLevel(logging.DEBUG)
    f_format = logging.Formatter(
        '%(asctime)s - %(name)s -  %(lineno)d - %(levelname)s - %(message)s')
    file_handler = RotatingFileHandler(file_path, maxBytes=10000, backupCount=2)
    file_handler.setFormatter(f_format)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(f_format)
    my_logger.addHandler(file_handler)
    my_logger.addHandler(console_handler)


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
    TELEGRAM_TOKEN = namespace.telegram
    DEWMAN_TOKEN = namespace.devman
    TG_CHAT_ID = namespace.chat
    create_log(namespace.file)
    header = {'Authorization': f'Token {DEWMAN_TOKEN}'}
    params = {'timestamp': ''}


    bot = telegram.Bot(token=TELEGRAM_TOKEN)

    class MyLogsHandler(logging.Handler):
        def emit(self, record):
            log_entry = self.format(record)
            # для проверяющего: devman почему то перестал отвечать текст ошибки
            # превышает 4096, это превышает лимит telegrama , поэтому пришлось
            # так разбить
            if len(log_entry) < 4096:
                bot.send_message(chat_id=TG_CHAT_ID, text=log_entry)
            else:
                num = len(log_entry) // 4096 + 1
                start = 0
                finish = 4096
                for i in range(num):
                    text = log_entry[start:finish]
                    bot.send_message(chat_id=TG_CHAT_ID, text=text)
                    start, finish = finish, finish + 4096

    logger = logging.getLogger('Bot_loger')
    logger.setLevel(logging.WARNING)
    logger.addHandler(MyLogsHandler())
    logger.warning('bot start')

    while True:
        try:
            my_logger.info('________Отправляем запрос сайту devman_________')
            check = get_checks_long_polling(header, params).json()
            my_logger.info(f'Проверяем json ')
            if check['status'] == 'timeout':
                my_logger.info(
                    f'получен ответ: "status = timeout" проверенных работ нет')
                timestamp = check['timestamp_to_request']
                params = {'timestamp': timestamp}
            elif check['status'] == 'found':
                my_logger.info(
                    f'Получен ответ: "status = found" работа проверенна{check}')
                timestamp = check['last_attempt_timestamp']
                params = {'timestamp': timestamp}
                text = get_checked_text(check)
                send_message_bot(TELEGRAM_TOKEN, TG_CHAT_ID, text)

        except requests.exceptions.ReadTimeout:
            pass

        except requests.exceptions.ConnectionError:
            logger.exception(f'No internet or wrong url ')
            my_logger.exception(f'No internet or wrong url ')
            time.sleep(3600)

        except Exception:
            logger.exception(f'Нестандартная ошибка: ')
            my_logger.exception(f'Нестандартная ошибка: ')
            return False


if __name__ == '__main__':
    main()
