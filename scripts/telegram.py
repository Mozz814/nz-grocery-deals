"""Private Telegram setup and delivery. Secrets come from environment only."""
import json
import os
import sys
import urllib.request
import urllib.error

def request(method, payload):
    token = os.environ.get('TELEGRAM_BOT_TOKEN')
    if not token:
        raise ValueError('Set TELEGRAM_BOT_TOKEN privately before running')
    url = 'https://api.telegram.org/bot' + token + '/' + method
    try:
        req = urllib.request.Request(url, data=json.dumps(payload).encode(), headers={'Content-Type': 'application/json'})
        with urllib.request.urlopen(req, timeout=30) as response:
            result = json.load(response)
        if not result.get('ok'):
            raise RuntimeError('Telegram rejected the request')
        return result['result']
    except (urllib.error.URLError, urllib.error.HTTPError):
        # Never print exceptions containing token-bearing URLs.
        raise RuntimeError('Telegram request failed; check private credentials and network') from None

def destinations():
    result = []
    for event in request('getUpdates', {'timeout': 0, 'allowed_updates': ['message']}):
        msg = event.get('message', {})
        chat = msg.get('chat', {})
        if chat.get('type') == 'private' and msg.get('text', '').split('@')[0] == '/start':
            result.append({'chat_id': chat['id'], 'username': chat.get('username'), 'first_name': chat.get('first_name')})
    return result

def send(text):
    chat = os.environ.get('TELEGRAM_CHAT_ID')
    if not chat:
        raise ValueError('Set verified TELEGRAM_CHAT_ID before sending')
    for start in range(0, len(text), 3500):
        request('sendMessage', {'chat_id': chat, 'text': text[start:start + 3500], 'disable_web_page_preview': True})

if __name__ == '__main__':
    try:
        if sys.argv[1:] == ['destinations']:
            print(json.dumps(destinations(), indent=2))
        elif len(sys.argv) == 3 and sys.argv[1] == 'send':
            with open(sys.argv[2], encoding='utf-8') as stream:
                send(stream.read())
            print('Report delivered')
        else:
            print('Usage: telegram.py destinations | send report.txt')
    except (RuntimeError, ValueError) as error:
        print(str(error), file=sys.stderr)
        sys.exit(1)
