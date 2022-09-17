import json
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager


class MyDay:
    def __init__(self, email, password) -> None:
        self.bearer_token = None
        self.storage = None
        self.id_token = None
        self.tenant_id = None
        self.email = email
        self.password = password
        self.session = None

        # Defaults
        self.browser = None
        self.base = "https://api.myday.cloud/"
        self.home = "https://coleggwent.myday.cloud/dashboard/home"

        # The "Juicy" Endpoints
        self.calendar_endpoint = self.base + "legacy/api/aggregate/v2/calendaritem"
        self.session_endpoint = self.base + "sessions/session/"
        self.alert_read_endpoint = self.base + "alerts/v3/read?isMobile=false"
        self.endsession_endpoint = self.base + "connect/endsession"
        self.attendance_endpoint = self.base + "legacy/api/aggregate/attendancemark"
        self.alerts_endpoint = self.base + "alerts/v3?isMobile=false"
        self.news_partition_endpoint = self.base + "newsroom/v2/news/partition/"

    def login(self) -> None:
        # User Agent to allow for Headless mode
        user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.50 Safari/537.36'

        options = Options()
        # Debug Stuff
        #options.add_experimental_option("detach", True)
        options.add_argument('--headless')
        options.add_argument("--window-size=1920,1080")
        options.add_argument('--log-level=3')
        options.add_argument(f'user-agent={user_agent}')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')

        self.browser = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        self.browser.get(self.home)
        WebDriverWait(self.browser, 5).until(
            lambda driver: driver.current_url != self.home)

        # Send Email via the Azure AD Auth and pass along password via ADFS
        email = self.browser.find_element(By.NAME, 'loginfmt')
        email.send_keys(self.email)
        self.browser.find_element(By.XPATH, "//input[@type='submit']").click()

        # Finish ADFS Flow with Password Input
        WebDriverWait(self.browser, 10).until(
            EC.presence_of_element_located((By.XPATH, "//input[@id='passwordInput']")))
        password = self.browser.find_element(
            By.XPATH, "//input[@id='passwordInput']")
        password.send_keys(self.password)
        self.browser.find_element(By.XPATH, "//span[@id='submitButton']").click()

        # Check for the "Stay Signed In" Page
        prompt_text = WebDriverWait(self.browser, 10).until(
            EC.presence_of_element_located((By.XPATH, "//div[@id='KmsiDescription']")))
        prompt_text.find_element(By.XPATH, "//input[@type='submit']").click()

        # Get Bearer Token from Local Storage
        try:
            WebDriverWait(self.browser, 10).until(
                EC.presence_of_element_located((By.XPATH, "//h1[@ng-bind='$root.$title']")))
            storage = self.browser.execute_script("return window.localStorage;")
            auth = json.loads(storage["myday-auth"])
            bootstrap = json.loads(storage["bootstrap"])

            # We just set up our most needed properties for pulling specific data
            self.storage = json.dumps(storage)
            self.bearer_token = auth["access_token"]
            self.id_token = auth["id_token"]
            self.tenant_id = bootstrap["tenantId"]
            self.session = json.loads(storage["myday-session"])

        except TimeoutException:
            print("[*] Page Timeout")

    def logout(self):
        WebDriverWait(self.browser, 5).until(
            EC.presence_of_element_located((By.XPATH, "//BUTTON[@id='header-usermenu-button']")))
        self.browser.find_element(By.XPATH, "//BUTTON[@id='header-usermenu-button']").click()
        try:
            if self.browser.find_element(By.XPATH, "(//UL[@uib-dropdown-menu=''])[2]"):
                self.browser.find_element(By.XPATH, "//A[@id='header-usermenu-signout']").click()
                if self.browser.find_element(By.XPATH, "//DIV[@class='modal-content']"):
                    self.browser.find_element(By.XPATH, "//BUTTON[@type='submit']").click()
        except NoSuchElementException:
            print("[*] No Header User Menu")

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

    def get_news(self, row_key, feed_id):
        headers = {"Authorization": self.bearer_token}
        try:
            res = requests.get("{}{}/{}/entries".format(self.news_partition_endpoint, row_key, feed_id),
                               headers=headers, params={'amount': '10'})
            if res.status_code != 404 and res.text != 'There is no news feed with the given ID.':
                return res.json()["model"]
        except:
            raise Exception("[*] News Query Failure | Row Key: {} | Feed ID: {}".format(row_key, feed_id))

    def get_alerts(self):
        headers = {"Authorization": self.bearer_token}
        try:
            res = requests.get(self.alerts_endpoint, headers=headers)
            if res.status_code == 200:
                return res.json()["alerts"]
        except:
            raise Exception("[*] Could not get alerts")

    def read_alert(self, alert_id):
        bearer_token = self.bearer_token
        headers = {"Authorization": bearer_token}
        data = {"alertIds": [alert_id]}
        try:
            requests.put(self.alert_read_endpoint, data=data, headers=headers)
        except:
            raise Exception("[*] Could not mark alert as read")
