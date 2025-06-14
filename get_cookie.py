import requests
from vndb_classes import Cookie
import re
import os
import time

def get_cookie(type,cookie:Cookie=None):

    '''
    vndb
    cookie: Cookie 类的实例
    '''

    if cookie == None:
        cookie = Cookie()

    if type == 'vndb':

        if cookie.is_expired or cookie.value == None:

            PROXY = os.getenv('PROXY')
            proxy= {   
                "http": PROXY, 
                "https": PROXY, 
                "ftp": PROXY
            }

            headers = {
                'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }

            response = requests.get('https://vndb.org/v2897', headers=headers, allow_redirects=False,proxies=proxy)
            pattern = r'xbotcheck=([^;]+); Path=([^;]+); Max-Age=(\d+)'

            if response.status_code == 307:

                cookies = response.headers.get('set-Cookie')
                match = re.search(pattern,cookies)

                xbotcheck = match.group(1)
                expires_at = time.time() + float(match.group(3))
                cookie.upgrade_cookie(xbotcheck,expires_at)

            else:

                print('导入logging/重试')
        
        return cookie.value
