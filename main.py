import requests
import os
from dotenv import load_dotenv
import logging
import telegram

load_dotenv()

logging.basicConfig(filename="sample2.log", level=logging.DEBUG)
logging.debug("This is a debug message")
logging.info("Informational message")
logging.error("An error has happened!")


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
    TEL_TOKEN = os.getenv('TEL_TOKEN')
    TOKEN = os.getenv('Authorization')
    header = {'Authorization': TOKEN}
    params = {'timestamp': ''}

    while True:
        try:
            check = get_checks_long_polling(header, params).json()
            if check['status'] == 'timeout':
                timestamp = check['timestamp_to_request']
                params = {'timestamp': timestamp}

            elif check['status'] == 'found':
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
                bot = telegram.Bot(token=TEL_TOKEN)
                bot.send_message(chat_id=283654263, text=text, parse_mode=telegram.ParseMode.HTML)

        except requests.exceptions.ReadTimeout:
            print('increase response time')
        except requests.exceptions.ConnectionError:
            print('noy internet')


if __name__ == '__main__':
    main()
