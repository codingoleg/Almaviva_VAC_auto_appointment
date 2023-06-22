from templates.ru.persons import TEMPLATE_FOR_1_PERSON, TEMPLATE_FOR_2_PERSONS
from datetime import date

REQUIRED_CITY = 'Самара'
NUMBER_OF_PERSONS = 2
START_DATE = date(2023, 6, 27)
FINAL_DATE = date(2023, 7, 10)
USERNAME = ''
PASSWORD = ''
CREDENTIALS_PERSON_1 = {
    'name': '',
    'surname': '',
    'passport': '',
    'phone': '',
    'applicantEmail': ''
}
# Fill the CREDENTIALS_PERSON_2, if you appoint two persons
CREDENTIALS_PERSON_2 = {
    'name': '',
    'surname': '',
    'passport': '',
    'phone': '',
    'applicantEmail': ''
}
REQUIRED_TIME = ('09:00', '09:30', '10:00', '10:30', '11:00', '11:30',
                 '12:00', '12:30', '13:00', '13:30', '14:00', '14:30')
URL = 'https://ru.almaviva-visa.services/'

if NUMBER_OF_PERSONS == 1:
    TEMPLATE = TEMPLATE_FOR_1_PERSON
elif NUMBER_OF_PERSONS == 2:
    TEMPLATE = TEMPLATE_FOR_2_PERSONS

with open('auth_token') as auth_token_cookie:
    HEADERS = {
        "Authorization": 'Bearer ' + auth_token_cookie.read(),
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0)"
                      " Gecko/20100101 Firefox/114.0",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.5",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "Sec-GPC": "1"
    }
