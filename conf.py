import datetime
import os


from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.environ.get('BOT_TOKEN')

USER_API_ID = os.environ.get('USER_API_ID')
USER_API_HASH = os.environ.get('USER_API_HASH')
USER_SESSION_NAME = os.environ.get('USER_SESSION_NAME')
PHONE = os.environ.get('PHONE')
REDIS_URI = f'{os.environ.get("REDIS_HOST", "localhost")}:{os.environ.get("REDIS_PORT", 6379)}'


schedule = [datetime.time(0), datetime.time(3), datetime.time(6), datetime.time(9), datetime.time(12), datetime.time(15), datetime.time(18), datetime.time(21)]

channels = [[public_channel_id, private_channel_id, text_for_button],]

button_text = 'Text for buttons under every posts'
button_url = 'Link for this button'