import requests
import os
from dotenv import load_dotenv
import logging
import json

import time


load_dotenv()
logging.basicConfig(filename="sample.log", level=logging.DEBUG)

logging.debug("This is a debug message")
# logging.info("Informational message")
logging.error("An error has happened!")

TOKEN = os.getenv('Authorization')
headers = {'Authorization': TOKEN}
params = {'timestamp': ''}



def get_checks():
    url = 'https://dvmn.org/api/user_reviews/'
    response = requests.get(url, headers=headers)
    response.raise_for_status
    return response


def get_checks_long_polling():
    long_polling_url = 'https://dvmn.org/api/long_polling/'
    response = requests.get(long_polling_url, headers=headers, params=params)
    response.raise_for_status
    return response


def main():
    while True:
        try:
            checks = get_checks_long_polling().json()
            timestamp_to_request = checks['timestamp_to_request']
            params = {'timestamp': timestamp_to_request}
            print(checks)
            print(params)



        except requests.exceptions.ReadTimeout:
            print('increase response time')
        except requests.exceptions.ConnectionError:
            print('noy internet')







if __name__ == '__main__':
    main()
