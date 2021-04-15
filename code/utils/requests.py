# -*- coding: utf8 -*-

import json
import requests

from variables          import API_URL, API_ADMIN_TOKEN

def api_admin_mypc_get_all(discordname):
    url      = f'{API_URL}/admin/mypc'
    payload  = {'discordname': discordname}
    headers  = json.loads('{"Authorization": "Bearer '+ API_ADMIN_TOKEN + '"}')
    response = requests.post(url, json = payload, headers=headers)

    if response.status_code == 200:
        if response.text:
            return json.loads(response.text)['payload']
    else:
        return None

def api_admin_mypc_get_one(discordname,pcid):
    url      = f'{API_URL}/admin/mypc/{pcid}'
    payload  = {'discordname': discordname}
    headers  = json.loads('{"Authorization": "Bearer '+ API_ADMIN_TOKEN + '"}')
    response = requests.post(url, json = payload, headers=headers)

    if response.status_code == 200:
        if response.text:
            return json.loads(response.text)['payload']
    else:
        return None

def api_admin_squad_get_one(squadid):
    url      = f'{API_URL}/admin/squad/{squadid}'
    headers  = json.loads('{"Authorization": "Bearer '+ API_ADMIN_TOKEN + '"}')
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        if response.text:
            if json.loads(response.text)['success']:
                return json.loads(response.text)['payload']
    else:
        return None

def api_admin_squad_get_all():
    url      = f'{API_URL}/admin/squad'
    headers  = json.loads('{"Authorization": "Bearer '+ API_ADMIN_TOKEN + '"}')
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        if response.text:
            if json.loads(response.text)['success']:
                return json.loads(response.text)['payload']
    else:
        return None
