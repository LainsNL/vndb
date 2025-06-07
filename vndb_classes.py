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
    

""" 
game = VisualNovel("七ヶ音学園 -旅行部-","v32820","Main character Kei Tokisaka, is a second year student attending a travel club. He is an ordinary student, but he has a secret that he can't tell anyone about. He adores club members who are all beautiful girls: the beautiful head of the club, the idol girl, the honor student's childhood friend, and cute younger students. The life of the club is filled with excitement, anxiety, humor and romance.")
A = Character('Main','ZZZ','Amy')
B = Character('Main12','ZZ2Z','Asmy')
C = Character('Maqin','ZZqZ','Amqy')
game.add_Char(A)
game.add_Chars([B,C])
game.get_all_Chars()
print(game.title,game.id,game.description) """