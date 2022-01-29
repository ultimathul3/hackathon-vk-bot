import os

from dotenv import load_dotenv


load_dotenv()

API_SERVER_URL = os.getenv('API_SERVER_URL')
VK_API_TOKEN = os.getenv('VK_API_TOKEN')