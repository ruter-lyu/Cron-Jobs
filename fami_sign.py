import os
import time
import base64
import json

import httpx

FAMI_TOKEN = os.getenv('FAMI_TOKEN')
FAMI_DEVICE_ID = os.getenv('FAMI_DEVICE_ID')

API_URL = 'https://fmapp.chinafamilymart.com.cn'


def _encode(encode_type='sign'):
    if encode_type == 'sign':
        data = {"tokenId":FAMI_TOKEN,"os":"iOS","seqId":"1625366917797698717","profileTime":57,"version":"3.6.7"}
    else:
        data = {"v":"weq1oGHfDOSvvhMae5CzSog58P+DGmNf64FJ3r3z5L+mqr44//ao9NtDF4sEnnrj","os":"web","it":421,"t":FAMI_TOKEN}
    s = json.dumps(data)
    return base64.b64encode(s.encode('utf-8'))


def sign():
    sign_url = f'{API_URL}/api/app/market/member/signin/sign'
    headers = {
        'Content-Type': 'application/json',
        'Accept': '*/*',
        'loginChannel': 'app',
        'os': 'ios',
        'Accept-Language': 'zh-Hans-CN;q=1.0, ru-CN;q=0.9',
        'token': FAMI_TOKEN,
        'Accept-Encoding': 'br;q=1.0, gzip;q=0.9, deflate;q=0.8',
        'deviceId': FAMI_DEVICE_ID,
        'User-Agent': 'Fa',
        'Connection': 'keep-alive',
        'fmVersion': '2.5.1',
        'blackBox': _encode('sign'),
    }
    resp = httpx.post(sign_url, data={}, headers=headers)
    data = resp.json()
    if data.get('code') == '200':
        print('Sign Success.')
    else:
        print(data.get('message'))


def lottery():
    sign_url = f'{API_URL}/api/app/market/turn/lottery'
    headers = {
        'Content-Type': 'application/json',
        'Accept': '*/*',
        'Referer': 'https://fmapp-activity.chinafamilymart.com.cn/pages/sudokuDrawLottery/index?query=%257B%2522activitycode%2522%253A%25223420210630001%2522%252C%2522activitytype%2522%253A%252234%2522%252C%2522utm_homeIndex%2522%253A%2522home_HB_001_004%2522%257D',
        'os': 'h5',
        'Accept-Language': 'zh-cn',
        'token': FAMI_TOKEN,
        'Accept-Encoding': 'gzip, deflate, br',
        'Origin': 'https://fmapp-activity.chinafamilymart.com.cn',
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148',
        'Connection': 'keep-alive',
        'blackBox': _encode('lottery'),
    }
    resp = httpx.post(sign_url, json={"activityCode":3420210630001,"cityCd":"上海"}, headers=headers)
    data = resp.json()
    if data.get('code') == '200':
        print(data.get('data', {}).get('priceInfo', {}).get('priceTitle'))
    else:
        print(data.get('message'))


if __name__ == '__main__':
    sign()
    lottery()
