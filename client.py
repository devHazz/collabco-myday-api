import json
import requests
from requests import PreparedRequest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os


class MyDay:
    def __init__(self, email, password) -> None:
        self.email = email
        self.password = password
        self.home = "https://coleggwent.myday.cloud/dashboard/home"
        self.calendar_endpoint = "https://api.myday.cloud/legacy/api/aggregate/v2/calendaritem"


    def login(self) -> None:
        browser = webdriver.Chrome("bin/chromedriver")
        browser.get(self.home)
        WebDriverWait(browser, 5).until(lambda driver: driver.current_url != self.home)

        # Send Email via Microsoft oAuth and pass along password via Coleg Gwent ADFS System
        email = browser.find_element(By.NAME, 'loginfmt')
        email.send_keys(self.email)
        browser.find_element(By.XPATH, "//input[@type='submit']").click()

        # Finish ADFS Flow with Password Input
        passwordIpt = WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.ID, 'passwordInput')))
        passwordIpt.send_keys(self.password)
        browser.find_element(By.ID, 'submitButton').click()

        # Check for the "Stay Signed In" Page
        promptText = WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, "//div[@id='KmsiDescription']")))
        promptText.find_element(By.XPATH, "//input[@type='submit']").click()

        # Get Bearer Token from Local Storage
        try:
            WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, "//h1[@ng-bind='$root.$title']")))
            storage = browser.execute_script("return window.localStorage;")
            bearer_token = json.loads(storage["myday-auth"])["access_token"]
            self.bearer_token = bearer_token
        except TimeoutException:
            print("Page timeout - Try again")

    def get_calendar(self, start=None, end=None):
        bearer_token = self.bearer_token
        headers = {"Authorization": bearer_token}
        try:
            x = requests.get(self.calendar_endpoint, headers=headers)
            if 'status' not in x.json() or 'storageQueryFailed' in x.json() and False:
                if start is not None and end is not None:
                    pr = PreparedRequest()
                    params = {'$filter': "End gt datetime'{}' and Start lt datetime'{}'".format(start, end)}
                    pr.prepare_url(self.calendar_endpoint, params)
                    return requests.get(pr, headers=headers).json()
                else:
                    return x.json()
            else:
                raise Exception('Calendar Query Failed - Maybe an expired Bearer token?')
        except requests.exceptions.RequestException as e:
            raise e
