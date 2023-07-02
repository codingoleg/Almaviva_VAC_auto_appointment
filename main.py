#!/usr/bin/env python

import requests
from config import *
from datetime import timedelta, datetime
from http.client import RemoteDisconnected
from random import randint
from requests.exceptions import ConnectionError, ReadTimeout, ConnectTimeout
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from time import sleep
from typing import Iterator, List, Dict
from templates.ru.cities import CITIES
from urllib3.exceptions import ProtocolError, MaxRetryError


# TODO: Add logging
# TODO: Add tests

class Driver:
    def __init__(self):
        self.__driver = None

    def __find(self, xpath: str) -> webdriver:
        """Shorten Webdriver method for better readability."""
        return self.__driver.find_element(By.XPATH, xpath)

    def __wait(self, xpath: str):
        """Shorten Webdriver method for better readability."""
        WebDriverWait(self.__driver, timeout=60).until(
            ec.presence_of_element_located((By.XPATH, xpath)))

    def login(self):
        """Login and write auth_token[value] cookie to 'auth_token' file."""
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        url_login = URL + 'appointment'
        accept_cookies_btn = "//p-button[@label='Accept']"
        email_input = "//input[@name='email']"
        password_input = "//input[@name='password']"
        remember_me_checkbox = "//input[@type='checkbox']"
        submit_btn = "//button[@class='btn btn-primary']"
        next_page = "//div[@class='visa-select']"

        while True:
            try:
                self.__driver = webdriver.Chrome(options=options)
                self.__driver.get(url_login)
                self.__wait(accept_cookies_btn)
                self.__find(accept_cookies_btn).click()
                self.__wait(email_input)
                self.__find(email_input).send_keys(USERNAME)
                self.__find(password_input).send_keys(PASSWORD)
                self.__find(remember_me_checkbox).click()
                self.__find(submit_btn).click()
                self.__wait(next_page)
            except TimeoutException as error:
                print(error)
            else:
                with open('auth_token', 'w') as cookie_token:
                    cookie_token.write(
                        self.__driver.get_cookie('auth-token')['value'])
                break
            finally:
                self.__driver.quit()


class Appointment:
    @staticmethod
    def __create_url_free_day(month: str, day: str) -> str:
        return f"{URL}api/sites/appointment-slots/?date={day}/{month}/2023" \
               f"&siteId={CITIES[REQUIRED_CITY]['id']}"

    def check_authorization(self) -> bool:
        """Check authorization with any url that requires it, e.g. START_DATE.
        Returns:
            True, if authorized. False otherwise.
        """
        free_day = self.__create_url_free_day(
            str(START_DATE.month),
            str(START_DATE.day)
        )
        response = requests.get(free_day, headers=HEADERS)
        return False if response.status_code == 401 else True

    def find_free_day(self, month: str, day: str) -> str:
        """Try to find a day with free spots.
        Yields:
            Free time interval in format 'hh:mm'.
        """
        while True:
            try:
                response = requests.get(
                    self.__create_url_free_day(month, day),
                    headers=HEADERS
                )
            except (ConnectionError, ReadTimeout, ConnectTimeout,
                    RemoteDisconnected, ProtocolError, MaxRetryError) as error:
                print(f'\t{error}')
                print('\tTrying again...')
            else:
                break

        if response.status_code == 200:
            month_name = date(2023, int(month), int(day)).strftime('%b')
            print('Scanning...', month_name, day)
            for line in response.json():
                if line and line['freeSpots']:
                    yield line['time']
        else:
            print(f'\t{response.status_code} {response.reason}.', end=' ')
            print('Trying again in 1 minute...')
            sleep(60)

    @staticmethod
    def complete_template(month: str, day: str, time_interval: str) -> Dict:
        """Complete the template with your credentials.
        Returns:
            Completed template.
        """
        single_date = f"2023-{month}-{day}T00:00:00.000Z"
        TEMPLATE['appointment']['appointmentDate'] = single_date
        TEMPLATE['appointment']['appointmentTime'] = time_interval
        TEMPLATE['folders'][0]['person'] = CREDENTIALS_PERSON_1
        TEMPLATE['site'] = CITIES[REQUIRED_CITY]

        # Adds second person if NUMBER_OF_PERSONS == 2
        if len(TEMPLATE['folders']) == 2:
            TEMPLATE['folders'][1]['person'] = CREDENTIALS_PERSON_2

        return TEMPLATE

    def create_app(self, month: str, day: str, time_interval: str) -> bool:
        """Try to create an appointment with the completed template.
        Returns:
            True, if an appointment was successfully created. False otherwise.
        """
        api_create_app = URL + 'api/save-reservation/?online=False&reference='
        completed_template = self.complete_template(month, day, time_interval)

        while True:
            try:
                response = requests.post(
                    url=api_create_app,
                    json=completed_template,
                    headers=HEADERS
                )
            except (ConnectionError, ReadTimeout, ConnectTimeout,
                    RemoteDisconnected, ProtocolError, MaxRetryError) as error:
                print(f'\t{error}')
                print('\tTrying again...')
            else:
                break

        if response.status_code == 202:
            print('The appointment was successfully created.')
            month_name = date(2023, int(month), int(day)).strftime('%b')
            print(f'2023 {month_name} {day}. Time {time_interval}')
            return True
        else:
            current_time = datetime.now().strftime('%H:%M')
            # Prints only 'invisible' time intervals here. See README
            print(f'\t[{current_time}] {time_interval} is occupied')
            return False

    @staticmethod
    def check_app():
        """Checks for an appointment existence"""
        api_profile = f'{URL}api/user/profile'
        client_id = requests.get(api_profile, headers=HEADERS).json()['id']
        api_view_app = f'{URL}api/group/client/{client_id}'
        response = requests.get(api_view_app, headers=HEADERS).json()[0]

        if response:
            print(response['appointment']['appointmentDate'], end='. ')
            print(response['appointment']['appointmentTime'])
            print(response['site']['name'])
            for folder in response['folders']:
                print(folder['person']['surname'], folder['person']['name'])
        else:
            print('No appointment found')


class Dates:
    @staticmethod
    def __daterange() -> datetime.date:
        """Yields:
            Every date from the start to the final date with one day interval.
        """
        for day in range(int((FINAL_DATE - START_DATE).days)):
            yield START_DATE + timedelta(day)

    def get_single_date(self) -> Iterator[List]:
        """Returns:
            Iterator[List[Month, Day]]."""
        return (single_date.strftime("%m %d").split()
                for single_date in self.__daterange())


def main():
    app = Appointment()

    if not app.check_authorization():
        Driver().login()
        with open('auth_token') as cookie_token:
            HEADERS["Authorization"] = 'Bearer ' + cookie_token.read()

    while True:
        for single_date in Dates().get_single_date():
            month, day = single_date[0].zfill(2), single_date[1].zfill(2)
            # Skip saturdays and sundays
            if date(2023, int(month), int(day)).weekday() < 5:
                free_day = app.find_free_day(month, day)
                for time_interval in free_day:
                    if time_interval in REQUIRED_TIME \
                            and app.create_app(month, day, time_interval):
                        return
                    sleep(randint(1, 4))


if __name__ == '__main__':
    main()
