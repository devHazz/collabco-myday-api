from client import MyDay
from dotenv import load_dotenv
import os

load_dotenv()

# Make sure "EMAIL" and "PASSWORD" variables are setup in a .env file
client = MyDay(os.getenv("EMAIL"), os.getenv("PASSWORD"))
client.login()

events = client.get_calendar()
print(events)