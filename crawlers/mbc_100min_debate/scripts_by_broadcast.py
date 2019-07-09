import os
import json
from pprint import pprint
import requests
from bs4 import BeautifulSoup as bs
from tqdm.auto import tqdm

QUERY_URL = 'http://script.imbc.com/scenario_billing_check_adam.asp?ContID={}'
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))


def create_login_session():
    headers = {
        'Connection': 'keep-alive',
        'Pragma': 'no-cache',
        'Cache-Control': 'no-cache',
        'Origin': 'http://member.imbc.com',
        'Upgrade-Insecure-Requests': '1',
        'DNT': '1',
        'Content-Type': 'application/x-www-form-urlencoded',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
        'Referer': 'http://member.imbc.com/Login/Login.aspx',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
    }

    data = {
        'TemplateID': 'main',
        'TURL': '',
        'confirmMsg': '',
        'IdsafeURL': '',
        'AdultYN': 'n',
        'AppID': '',
        'SNSType': '',
        'Uid': os.environ.get('MBC_ID'),
        'Password': os.environ.get('MBC_PW')
    }

    s = requests.Session()
    s.headers = headers

    # login
    login = s.post('https://member.imbc.com/Login/LoginProcess.aspx', data=data)
    assert "window.location.href='http://www.imbc.com'" in login.text
    return s


def get_scripts_by_broadcast_id(session, broadcast_id):
    r = session.get(QUERY_URL.format(broadcast_id))
    soup = bs(r.text, 'lxml')
    try:
        contents = soup.select_one('pre').text.split('\n\n')
    except AttributeError as e:
        print(e)
        print(QUERY_URL.format(broadcast_id))
        print(r.text)
        raise e
    result = ''
    for c in contents:
        result += ' '.join(c.split()).strip() + '\n'
    return result.strip()


if __name__ == '__main__':
    error_list = []
    consecutive_error = 0

    session = create_login_session()
    data = json.load(open(os.path.join(CURRENT_DIR, '1000842100000100000_1999-2019.json')))
    os.makedirs(os.path.join(CURRENT_DIR, 'data'), exist_ok=True)
    for i in tqdm(list(reversed(data))[1:]):
        json_path = os.path.join(CURRENT_DIR, 'data', f"{i['BroadDate']}_{i['ContentNumber']}.json")
        if os.path.exists(json_path):
            continue
        try:
            contents = get_scripts_by_broadcast_id(session, i['BroadCastID'])
            json.dump(
                {**i, **{'contents': contents}},
                open(json_path, 'w+')
            )
            consecutive_error = 0
        except Exception as e:
            print(e)
            print(i)
            error_list.append(i)
            consecutive_error += 1
        if consecutive_error > 3:
            print(error_list)
            raise Exception("Too many errors")
