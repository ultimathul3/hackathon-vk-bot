import requests

from config import API_SERVER_URL
from data import RequestData


def get_categories():
    return requests.get(API_SERVER_URL + 'problem-categories').json()


def send_request(peer_id):
    payload = RequestData.data[peer_id]
    payload['latitude'] = 0
    payload['longitude'] = 0
    payload['source'] = 'VK'

    response = requests.post(API_SERVER_URL + 'requests', json=payload)
    return response