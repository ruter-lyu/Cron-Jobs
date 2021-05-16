# -*- coding: utf-8 -*-
import os
import httpx

GITHUB_USER = os.getenv('GITHUB_USER')
NOTION_TOKEN = os.getenv('NOTION_TOKEN')
NOTION_PAGE = os.getenv('NOTION_PAGE')
NOTION_VERSION = '2021-05-13'


def get_github_stars():
    stars_lst = []
    github_stared_url = f'https://api.github.com/users/{GITHUB_USER}/starred'
    page = 1
    size = 100
    while True:
        r = httpx.get(github_stared_url, params={'page': page, 'per_page': size})
        data = r.json()
        if not data:
            break
        stars_lst.extend(data)
        page += 1
    return stars_lst


def notion_data_exists(res_id):
    notion_api_url = f'https://api.notion.com/v1/databases/{NOTION_PAGE}/query'
    headers = {
        'Authorization': f'Bearer {NOTION_TOKEN}',
        'Content-Type': 'application/json',
        'Notion-Version': NOTION_VERSION
    }
    data = {
        'filter': {
            'property': 'ID',
            'number': {'equals': res_id}
        }
    }
    r = httpx.post(notion_api_url, headers=headers, data=data)
    res = r.json()
    if res.get('results'):
        return True
    return False


def sync_to_notion(star):
    notion_api_url = 'https://api.notion.com/v1/pages'
    headers = {
        'Authorization': f'Bearer {NOTION_TOKEN}',
        'Content-Type': 'application/json',
        'Notion-Version': NOTION_VERSION
    }
    data = {
        'parent': {'database_id': NOTION_PAGE},
        'properties': {
            'ID': {'number': star.get('id')},
            'Name': {'title': [{'text': {'content': star.get('full_name')}}]},
            'Description': {'rich_text': [{'text': {'content': star.get('description') or ''}}]},
            'Homepage': {'url': star.get('homepage') or ''},
            'URL': {'url': star.get('html_url')},
            'Archived': {'checkbox': star.get('archived', False)},
            'Language': {'select': {'name': star.get('language') or ''}},
            'License': {'select': {'name': star.get('license', {}).get('name') or ''}},
        }
    }
    httpx.post(notion_api_url, headers=headers, data=data)


if __name__ == '__main__':
    stars_lst = get_github_stars()
    for star in stars_lst:
        if not notion_data_exists(star.get('id')):
            print(f'Sync {star.get("full_name")} to Notion...')
            sync_to_notion(star)
        else:
            print(f'Data {star.get("full_name")} already exists, trying next...')
