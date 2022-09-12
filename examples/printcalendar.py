from ..client import MyDay
from dotenv import load_dotenv
import os

load_dotenv()


def main():
    # Make sure "EMAIL" and "PASSWORD" variables are setup in a .env file
    client = MyDay(os.getenv("EMAIL"), os.getenv("PASSWORD"))
    client.login()

    events = client.get_calendar()
    print(events)

    # Dismantle the client after running the things we need
    client.remove_session()