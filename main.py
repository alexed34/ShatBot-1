import requests
import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv('Authorization')
headers = {'Authorization': TOKEN}
params = {'timestamp': '1590647860'}


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
    checks = get_checks().text
    print(checks)



if __name__ == '__main__':
    main()
