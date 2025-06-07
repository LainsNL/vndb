from playwright.sync_api import sync_playwright
from vndb_classes import Cookie

def get_cookie(type,cookie:Cookie=None):

    '''
    vndb
    cookie: Cookie 类的实例
    '''

    if cookie == None:
        cookie = Cookie()

    if type == 'vndb':

        if cookie.is_expired or cookie.value == None:

            proxy= {   
                    "server": f"http://127.0.0.1:7897",
                    "bypass": "localhost",    
                }

            p = sync_playwright().start()
            browser = p.chromium.launch(proxy=proxy)
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                viewport={"width": 1280, "height": 720}
            )
            context.set_default_timeout(20000)
            page = context.new_page()

            try:
                
                page.goto("https://vndb.org/v28297")
                cookies = context.cookies()
                expires_at = cookies[0]['expires']
                xbotcheck = cookies[0]['value']
                cookie.upgrade_cookie(xbotcheck,expires_at)
            
            except:

                print('导入logging/重试')

        return cookie.value
