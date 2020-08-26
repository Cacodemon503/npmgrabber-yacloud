import re
import json
import base64
import requests
from urllib.parse import parse_qs


def know_status(name):
    r = requests.get(url=f'https://www.npmjs.com/~{name}')
    if r.status_code == 404:
        return '404'
    else:
        return 'OK'


def npm_checker(name):
    r = requests.get(url=f'https://www.npmjs.com/~{name}')
    html = r.text

    target_fullname = re.search(r'"fullname":"(.*?)"', html)
    try:
        fullname = target_fullname.group(1)
    except AttributeError:
        fullname = 'none'
    target_email = re.search(r'"email":"(.*?)"', html)
    try:
        email = target_email.group(1)
    except AttributeError:
        email = 'none'

    target_github = re.search(r'"github":"(.*?)"', html)
    try:
        github = target_github.group(1)
    except AttributeError:
        github = 'none'

    target_twitter = re.search(r'"twitter":"(.*?)"', html)
    try:
        twitter = target_twitter.group(1)
    except AttributeError:
        twitter = 'none'

    return fullname, email, github, twitter


def main(name):

    status = know_status(name)

    if status == 'OK':
        fullname, email, github, twitter = npm_checker(name)
        response = str(
            f'User fullname: {fullname} User email: {email} User github: {github} User twitter: {twitter}')
        return response
    elif status == '404':
        response = str('No such user')
        return response


def handler(event, context):
    name = None
    if 'queryStringParameters' in event and 'name' in event['queryStringParameters']:
        name = event['queryStringParameters']['name']

    body = None
    if name is None:
        if event['httpMethod'] == 'POST' or \
           event['httpMethod'] == 'PUT':
            if event['isBase64Encoded']:
                body = base64.b64decode(event['body']).decode('utf-8')
            else:
                body = event['body'].decode('utf-8')

            bodydict = parse_qs(body)

            name = bodydict['name'][0] if 'name' in bodydict else None

    if name is None:
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
            },
            'isBase64Encoded': False,
            'body': json.dumps({
                "error": "Please, fill the form"
            }, ensure_ascii=False)
        }

    name = name.strip().lower()

    response = main(name)

    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
        },
        'isBase64Encoded': False,
        'body': json.dumps({
            "message": response
        }, ensure_ascii=False)
    }
