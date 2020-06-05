import logging
import os
import sys
from logging.handlers import RotatingFileHandler
import requests
import telegram
from dotenv import load_dotenv
import time
load_dotenv()

logger = logging.getLogger(__name__)


def get_checks(headers):
    url = 'https://dvmn.org/api/user_reviews/'
    response = requests.get(url, headers=headers)
    response.raise_for_status
    return response


def get_checks_long_polling(header, params):
    url = 'https://dvmn.org/api/long_polling/'
    response = requests.get(url, headers=header, params=params)
    response.raise_for_status
    return response



def main():
    logger.setLevel(logging.INFO)
    #logger.setLevel(logging.ERROR)
    file_handler = RotatingFileHandler("simple.txt", maxBytes=2000, backupCount=2)
    f_format = logging.Formatter('%(asctime)s - %(name)s -  %(lineno)d - %(levelname)s - %(message)s')
    file_handler.setFormatter(f_format)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(f_format)
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    TEL_TOKEN = os.getenv('TEL_TOKEN')
    TOKEN = os.getenv('Authorization')
    header = {'Authorization': TOKEN}
    params = {'timestamp': ''}


    while True:
        try:
            logger.info('отправляем запрос сайту')
            #check = get_checks_long_polling(header, params).json()
            check = get_checks(header).json()

            logger.info(f'проверяем ответ сайта')
            if check['status'] == 'timeout':
                logger.info(f'получен ответ: status = timeout ')
                timestamp = check['timestamp_to_request']
                params = {'timestamp': timestamp}
            elif check['status'] == 'found':
                logger.info(f'получен ответ: status = found ')
                timestamp = check['new_attempts'][0]['timestamp']
                params = {'timestamp': timestamp}
                name_lesson = check['new_attempts'][0]['lesson_title']
                verification_results = check['new_attempts'][0]['is_negative']
                if verification_results:
                    text = f'У вас проверили работу "{name_lesson}" К сожалению, ' \
                           f'в работе нашлись ошибки.'
                else:
                    text = f'У вас проверили работу "{name_lesson}" Преподавателю все понравилось, ' \
                           f'можете приступать к следующему уроку.'
                logger.info('подключение к telegram-боту')
                bot = telegram.Bot(token=TEL_TOKEN)
                logger.info('отправка сообщения telegram-боту')
                bot.send_message(chat_id=283654263, text=text, parse_mode=telegram.ParseMode.HTML)

        except requests.exceptions.ReadTimeout:
            logger.error('increase response time')
            time.sleep(90)

        except requests.exceptions.ConnectionError:
            logger.error('no internet or wrong url')
            time.sleep(90)
        except Exception as err:
            logger.error(f'неизвестная ошибка: {err}')
            return False


if __name__ == '__main__':
    main()
