import requests
import os
from dotenv import load_dotenv
load_dotenv()

Token = os.getenv('Authorization')
url = 'https://dvmn.org/api/user_reviews/'
headers = {'Authorization': Token}

def get_checks(url):
    response = requests.get(url, headers=headers)
    response.raise_for_status
    return response
    
def main():
    checks = get_checks(url).text
    print(checks)



if __name__ == '__main__':
    main()