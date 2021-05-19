import os
import random

import httpx

from utils.wechat import WeChatWork

NOTION_TOKEN = os.getenv('NOTION_TOKEN')
NOTION_PAGE = os.getenv('NOTION_PAGE')
NOTION_VERSION = '2021-05-13'

CORP_ID = os.getenv('WECHAT_CORP_ID')
CORP_SECRET = os.getenv('WECHAT_CORP_SECRET')
AGENT_ID = os.getenv('WECHAT_AGENT_ID')
TO_USER = os.getenv('WECHAT_TO_USER')
MEDIA_ID = os.getenv('WECHAT_MEDIA_ID')


def _random_pick(data):
    if not data:
        raise ValueError('Not enough data to pick.')
    rand_data = random.sample(data, random.randint(0, len(data)))
    return rand_data[random.randint(0, len(rand_data) - 1)]


def get_notion_data():
    notion_api_url = f'https://api.notion.com/v1/databases/{NOTION_PAGE}/query'
    headers = {
        'Authorization': f'Bearer {NOTION_TOKEN}',
        'Content-Type': 'application/json',
        'Notion-Version': NOTION_VERSION
    }
    data = {
        'filter': {
            'property': 'Reviewed',
            'checkbox': {'equals': False}
        },
        'sorts': [{
            'property': random.sample(['Name', 'Language', 'ID'], 1)[0],
            'direction': random.sample(['ascending', 'descending'], 1)[0]
        }]
    }
    r = httpx.post(notion_api_url, headers=headers, json=data)
    res = r.json()
    return _random_pick(res.get('results', []))


def get_msg_by_data(data):
    title = data.get("Name").get("title")[0].get("plain_text")
    digest = data.get('Description').get('rich_text')
    lang = data.get('Language').get('rich_text')
    if digest:
        digest = digest[0].get('plain_text')
    else:
        digest = '😂 暂无描述'
    
    if lang:
        lang = lang[0].get('plain_text')
    else:
        lang = 'Unknown'

    content_html = f'''<div>
        <p>{title}</p>
        <p>{digest}</p>
        <p>{lang}</p>
        <p>{data.get("URL").get("url")}</p>
    </div>
    '''
    msg = {
        'mpnews' : {
            'articles':[{
                'title': f'今日回顾 - {title}',
                'thumb_media_id': MEDIA_ID,
                'author': 'Ruter',
                'content_source_url': '',
                'content': content_html,
                'digest': digest
            }]
        }
    }
    return msg


if __name__ == '__main__':
    data = get_notion_data()
    msg_data = get_msg_by_data(data.get('properties', {}))
    wx = WeChatWork(CORP_ID, CORP_SECRET, AGENT_ID, TO_USER)
    wx.send_app_msg(msg_type='mpnews', msg_data=msg_data)
