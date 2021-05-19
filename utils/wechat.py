# -*- coding: utf-8 -*-
import httpx


class WeChatWork:
    def __init__(self, corp_id, corp_secret, agent_id, to_user=None, to_party=None, to_tag=None):
        self.corp_id = corp_id
        self.corp_secret = corp_secret
        self.agent_id = int(agent_id)
        self.to_user = to_user
        self.to_party = to_party
        self.to_tag = to_tag

    def _get_basic_params(self, msg_type='text'):
        params = {
            'agentid': self.agent_id,
            'msgtype': msg_type
        }
        if self.to_user:
            params.update({'touser': self.to_user})
        if self.to_party:
            params.update({'toparty': self.to_party})
        if self.to_tag:
            params.update({'totag': self.to_tag})
        return params

    def get_access_token(self):
        url = f'https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid={self.corp_id}&corpsecret={self.corp_secret}'
        resp = httpx.get(url)
        data = resp.json()
        return data.get('access_token')

    def send_app_msg(self, msg_type='text', msg_data=None):
        if not msg_data:
            return False
        access_token = self.get_access_token()
        msg_api_url = f'https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token={access_token}'
        params = self._get_basic_params(msg_type)
        params.update(msg_data)
        resp = httpx.post(msg_api_url, json=params)
        return resp.json().get('errmsg')
