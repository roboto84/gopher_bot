from requests import Response, get


def get_external_ip():
    try:
        url: str = 'https://myexternalip.com/raw'
        r: Response = get(url)
    except Exception as e:
        print('Unable to get external IP', e)
        return 'unknown'
    else:
        return r.text
