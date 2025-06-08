import time
import requests

class VisualNovel():

    '''
    游戏名称
    游戏ID
    游戏简介
    '''

    def __init__(self, title:str, id:str, description:str):
        self.title = title
        self.id = id
        self.description = description
        self.type = 'ViscualNovel'
        self.characters = []

    def add_Char(self, char):
        self.characters.append(char)
    
    def add_Chars(self, chars):
        for char in chars:
            self.characters.append(char)

    def get_all_Chars(self):

        for char in self.characters:
            print(char)

        return self.characters

class Character():

    '''
    名称
    主要/次要
    罗马名
    其他
    '''

    def __init__(self, role_type:str, romaji_name:str, name:str):

        self.role_type = role_type
        self.romaji_name = romaji_name
        self.name = name

    def __str__(self):
        
        # 使用print时调用这个函数,必须使用return一个字符串
        return self.name


class Cookie():

    def __init__(self, value: str = '', expires_at :float = 0):

        self.value = value
        self.expires_at = expires_at

    def is_expired(self, type):

        return time.time() > self.expires_at + 120 
    
    def upgrade_cookie(self, new_value: str = '', new_expires_at:float = 0):

        """更新 Cookie 的值和过期时间"""
        self.value = new_value
        self.expires_at = new_expires_at

class SearchResult():

    def __init__(self, query: str, url: str = None, type: str = 'vndb', ):

        '''
        初始化搜索结果

        :param query: 搜索查询字符串
        :param type: 搜索类型
        :param url: 搜索网址 
        '''
        self.query = query
        self.type = type

        if url == None:

            self.url = self._genetrate_url()

        self.url = url

    def _genetrate_url(self):

        '''
        不建议外部使用
        '''
        headers= {
                'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
        proxy= {   
            "http": "http://127.0.0.1:7897", 
            "https": "http://127.0.0.1:7897", 
            "ftp":"http://127.0.0.1:7897"
        }

        try:

            if self.type =='vndb':

                response = requests.get(url=f'https://vndb.org/v?sq={self.query}',headers=headers,proxies=proxy) 
                return response.url
            
            else:

                raise ValueError('TODO')

        except Exception as e:

            raise ValueError(f'Failed to generate url:{e}')

    def is_Target(self):

        '''
        判断是否为需要的结果

        :param type: 搜索类型

        '''

        if self.type == 'vndb':

            return not self.url.rsplit('/')[-1].startswith('v?')
        
    def get_id(self):

        if self.is_Target() == True:

            if self.type == 'vndb':

                return self.url.split('/')[-1]

        raise ValueError("Not the target url")



