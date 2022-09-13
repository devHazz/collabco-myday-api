import ast
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
        self.session = None
        # Base API Endpoints
        self.base = "https://api.myday.cloud/"
        self.home = "https://coleggwent.myday.cloud/dashboard/home"

        # The "Juicy" Endpoints
        self.calendar_endpoint = self.base + "legacy/api/aggregate/v2/calendaritem"
        self.session_endpoint = self.base + "sessions/session/"
        self.alert_read_endpoint = self.base + "alerts/v3/read"
        self.endsession_endpoint = self.base + "connect/endsession"
        self.attendance_endpoint = self.base + "legacy/api/aggregate/attendancemark"

    def login(self) -> None:

        # Debug Stuff
        # chrome_options = Options()
        # chrome_options.add_experimental_option("detach", True)

        browser = webdriver.Chrome("bin/chromedriver")
        browser.get(self.home)
        WebDriverWait(browser, 5).until(
            lambda driver: driver.current_url != self.home)

        # Send Email via Microsoft oAuth and pass along password via Coleg Gwent ADFS System
        email = browser.find_element(By.NAME, 'loginfmt')
        email.send_keys(self.email)
        browser.find_element(By.XPATH, "//input[@type='submit']").click()

        # Finish ADFS Flow with Password Input
        WebDriverWait(browser, 10).until(EC.presence_of_element_located(
            (By.XPATH, "//input[@id='passwordInput']")))
        password = browser.find_element(
            By.XPATH, "//input[@id='passwordInput']")
        password.send_keys(self.password)
        browser.find_element(By.XPATH, "//span[@id='submitButton']").click()

        # Check for the "Stay Signed In" Page
        prompt_text = WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.XPATH, "//div[@id='KmsiDescription']")))
        prompt_text.find_element(By.XPATH, "//input[@type='submit']").click()

        # Get Bearer Token from Local Storage
        try:
            WebDriverWait(browser, 10).until(
                EC.presence_of_element_located((By.XPATH, "//h1[@ng-bind='$root.$title']")))
            storage = browser.execute_script("return window.localStorage;")
            auth = json.loads(storage["myday-auth"])
            bootstrap = json.loads(storage["bootstrap"])

            # We just setup our most needed properties for pulling specific data
            self.storage = json.dumps(storage)
            self.bearer_token = auth["access_token"]
            self.id_token = auth["id_token"]
            self.tenant_id = bootstrap["tenantId"]
            self.session = json.loads(storage["myday-session"])

        except TimeoutException:
            print("[*] Page Timeout")

    def get_calendar(self, start=None, end=None):
        headers = {"Authorization": self.bearer_token}
        try:
            x = requests.get(self.calendar_endpoint, headers=headers)
            if 'status' not in x.json() or 'storageQueryFailed' in x.json() and False:
                if start is not None and end is not None:
                    params = {
                        '$filter': "End gt datetime'{}' and Start lt datetime'{}'".format(start, end)}
                    return requests.get(self.calendar_endpoint, headers=headers, params=params).json()
                else:
                    return x.json()
            else:
                raise Exception('[*] Calendar Query Failure')
        except requests.exceptions.RequestException as e:
            raise e

    def get_attendance(self, start=None, end=None):
        headers = {"Authorization": self.bearer_token}
        try:
            if start is not None and end is not None:
                params = {
                    '$filter': "sessionTime gt datetime'{}' and sessionTime lt datetime'{}'".format(start, end)
                }
                res = requests.get(self.attendance_endpoint, headers=headers, params=params)
                if res.status_code == 200:
                    return res.json() 
            else:
                res = requests.get(self.attendance_endpoint, headers=headers)
                if res.status_code == 200:
                    return res.json()
        except:
            raise Exception("[*] Attendance Query Failure")
            

    def read_alert(self, alert_id):
        bearer_token = self.bearer_token
        headers = {"Authorization": bearer_token}
        data = {"alertIds": [alert_id]}
        try:
            requests.put(data, headers=headers)
        except:
            raise Exception("[*] Could not mark alert as read")
