import json
import requests


def hello(event, context):
    url = 'https://api.pexels.com/v1/search?query=Ocean'
    headers = {
        'Authorization': '',
    }

    res = requests.get(url, headers=headers)

    print(res.json())

