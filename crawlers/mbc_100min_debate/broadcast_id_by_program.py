import requests
import json
import os.path

QUERY_URL = 'http://vodmall.imbc.com/util/wwwUtil_sbox_contents.aspx?progCode={program_code}&yyyy={year}&callback=cb'


def get_program_urls(program_code, year):
    res = requests.get(QUERY_URL.format(program_code=program_code, year=year))
    return reversed(json.loads(res.text.replace('cb(', '')[:-1]))


def get_program_range(program_code, start_year, end_year):
    res = []
    for year in range(start_year, end_year+1):
        res += get_program_urls(program_code, year)
    return res


if __name__ == '__main__':
    program_code = '1000842100000100000'
    start_year = 1999
    end_year = 2019
    current_dir = os.path.dirname(os.path.abspath(__file__))
    data = get_program_range(program_code, start_year, end_year)
    json.dump(data, open(os.path.join(current_dir, f'{program_code}_{start_year}-{end_year}.json'), 'w+'))
