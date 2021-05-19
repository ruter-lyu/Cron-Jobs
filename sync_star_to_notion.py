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
        data = get_diff_data(data)
        stars_lst.extend(data)
        page += 1
    return stars_lst


def get_diff_data(stars):
    diff_stars = []
    res_ids = [star.get('id') for star in stars]
    pages = get_notion_data(res_ids)
    page_ids = [page.get('properties').get('ID').get('number') for page in pages]
    for star in stars:
        if star.get('id') not in page_ids:
            diff_stars.append(star)
        else:
            print(f'Data {star.get("full_name")} already exists, trying next...')
    return diff_stars


def get_notion_data(res_ids):
    notion_api_url = f'https://api.notion.com/v1/databases/{NOTION_PAGE}/query'
    headers = {
        'Authorization': f'Bearer {NOTION_TOKEN}',
        'Content-Type': 'application/json',
        'Notion-Version': NOTION_VERSION
    }
    data = {
        'filter': {
            'or': [{
                'property': 'ID',
                'number': {'equals': res_id}
            } for res_id in res_ids]
        }
    }
    r = httpx.post(notion_api_url, headers=headers, json=data)
    res = r.json()
    return res.get('results', [])


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
            'Name': {'title': [{'type': 'text', 'text': {'content': star.get('full_name')}}]},
            'Description': {'rich_text': [{'type': 'text', 'text': {'content': star.get('description') or ''}}]},
            'Homepage': {'url': star.get('homepage') or None},
            'URL': {'url': star.get('html_url')},
            'Archived': {'checkbox': star.get('archived', False)},
            'Language': {'rich_text': [{'type': 'text', 'text': {'content': star.get('language') or ''}}]},
            'License': {'rich_text': [{'type': 'text', 'text': {'content': (star.get('license') or {}).get('name') or ''}}]},
        }
    }
    r = httpx.post(notion_api_url, headers=headers, json=data)
    if r.status_code == httpx.codes.OK:
        print(f'Sync {star.get("full_name")} done.')
    else:
        resp = r.json()
        print(f'code: {resp.get("code", "")}, message: {resp.get("message", "")}')
        r.raise_for_status()


if __name__ == '__main__':
    stars_lst = get_github_stars()
    for star in stars_lst:
        print(f'Sync {star.get("full_name")} to Notion...')
        sync_to_notion(star)
