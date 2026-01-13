import sys
import time
import requests
from bs4 import BeautifulSoup

LOGIN_URL   = 'https://img.ink/auth/login.html'
MORE_URL    = 'https://img.ink/user/moremore.html'
ACCOUNT = os.getenv('ACCOUNT')
PASSWORD = os.getenv('PASSWORD')
PROXIES     = {}
TIMEOUT     = 10

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                  'AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/114.0 Safari/537.36'
}

def init():
    if not ACCOUNT and not PASSWO:
        raise ValueError("环境变量 ACCOUNT和PASSWORD  未设置")
    if not ACCOUNT:
        raise ValueError("环境变量 ACCOUNT  未设置")
    if not PASSWORD:
        raise ValueError("环境变量 PASSWORD  未设置")

def log(msg):
    print(f'[{time.strftime("%Y-%m-%d %H:%M:%S")}] {msg}')

def get_token(session):
    rsp = session.get(LOGIN_URL, headers=HEADERS, proxies=PROXIES, timeout=TIMEOUT)
    rsp.raise_for_status()
    soup = BeautifulSoup(rsp.text, 'lxml')
    token_input = soup.select_one('input[name="__token__"]')
    if not token_input:
        raise RuntimeError('Can not find __token__ in login page!')
    token = token_input['value']
    return token

def login(session, token):
    data = {
        'account': ACCOUNT,
        'password': PASSWORD,
        '__token__': token
    }
    rsp = session.post(LOGIN_URL, data=data, headers=HEADERS,
                       proxies=PROXIES, timeout=TIMEOUT, allow_redirects=True)
    rsp.raise_for_status()
    if 'login.html' in rsp.url:
        raise RuntimeError('Login failed, check account/password!')

def check_in(session):
    rsp = session.get(MORE_URL, headers=HEADERS, proxies=PROXIES, timeout=TIMEOUT)
    rsp.raise_for_status()
    soup = BeautifulSoup(rsp.text, 'html.parser')
    success_tag = soup.select_one('p.success')
    if success_tag and '成功扩容' in success_tag.text:
        log(f'✅ 签到成功：{success_tag.text.strip()}')
        return
    text = rsp.text
    if '每天仅可扩容一次' in text or '今日已扩容' in text:
        log('⚠️  今日已扩容，明天再来~')
    else:
        log('❓ 未知返回，请手动检查：' + text[:200])


def main():
    with requests.Session() as s:
        try:
            init()
            token = get_token(s)
            login(s, token)
            check_in(s)
        except Exception as e:
            log(f'❌ Error: {e}')
            sys.exit(1)

if __name__ == '__main__':
    main()