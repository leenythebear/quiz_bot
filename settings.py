import os
from dotenv import load_dotenv

load_dotenv()

redis_host = os.environ['DB_HOST']
redis_port = os.environ['DB_PORT']
redis_password = os.environ['DB_PASSWORD']

telegram_token = os.environ['TG_TOKEN']
