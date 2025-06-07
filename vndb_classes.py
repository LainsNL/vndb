import time

class VisualNovel():

    '''
    游戏名称
    游戏ID
    游戏简介
    '''

    def __init__(self,title:str,id:str,description:str):
        self.title = title
        self.id = id
        self.description = description
        self.type = 'ViscualNovel'
        self.characters = []

    def add_Char(self,char):
        self.characters.append(char)
    
    def add_Chars(self,chars):
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

    def __init__(self,role_type:str,romaji_name:str,name:str):

        self.role_type = role_type
        self.romaji_name = romaji_name
        self.name = name

    def __str__(self):
        
        # 使用print时调用这个函数,必须使用return一个字符串
        return self.name


class Cookie():

    def __init__(self,value: str = '',expires_at :float = 0):

        self.value = value
        self.expires_at = expires_at

    def is_expired(self,type):

        return time.time() > self.expires_at + 120 
    
    def upgrade_cookie(self,new_value: str = '',new_expires_at:float = 0):

        """更新 Cookie 的值和过期时间"""
        self.value = new_value
        self.expires_at = new_expires_at

