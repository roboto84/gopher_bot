import requests
import json


def get_external_ip() -> str:
    try:
        url: str = 'https://myexternalip.com/raw'
        r: requests.Response = requests.get(url)
    except Exception as e:
        print('Unable to get external IP', e)
        return 'unknown'
    else:
        return r.text


def get_external_ip_location(ip: str) -> str:
    try:
        location_summary: str = 'location unknown'
        headers: dict = {'User-Agent': 'keycdn-tools:https://www.robhoto84.dev'}
        url: str = f'https://tools.keycdn.com/geo.json?host={ip}'
        response = requests.request('GET', url, headers=headers)
        if response:
            package: dict = json.loads(response.text)
            if package['status'] == 'success':
                location: dict = package['data']['geo']
                location_summary: str = f'{location["city"]}, {location["region_name"]} ({location["country_code"]})'
            return location_summary
        else:
            print('Unable to get IP location')
            return location_summary
    except Exception as e:
        print('Unable to get IP location', e)
        return location_summary
