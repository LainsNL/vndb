import requests 
import parsel
from vndb_classes import SearchResult,Cookie
from get_cookie import get_cookie

def get_vndb_data(games:list=[]):

    Result = []
    
    # Todo:不是字典类型则使用默认的，否则遍历，考虑并发池
    if games == []:
        games = input('输入游戏名称(请勿携带/):')
        print()

    if type(games) is not list:
        games = [games]

    for game in games:

        game = SearchResult(game,'vndb')
        Result.append(game.query)

        if game.is_Target() == False:

            count = 1
            id_index = []

            SearchResult_selector = parsel.Selector(game.url_text)
            SearchResults_text = SearchResult_selector.xpath('//*[contains(@class, "stripe")]//tr[not(parent::thead)]').getall()

            if SearchResults_text == []:
                raise ValueError('[ERROR]: TODO!!')
            
            for SearchResult_text in SearchResults_text:

                SearchResult_selector = parsel.Selector(SearchResult_text)
                id_index.append(SearchResult_selector.css('a::attr("href")').get())
                title = SearchResult_selector.css('a::attr("title")').get()

                print(f"{count} - {title}  {SearchResult_selector.css('.tc_rel::text').get()}")
                count = count + 1

            print('\n\n')
            choose = input('----请键入你的选择----\n1.AI查询(不联网)\n2.网络搜索\n3.手动选择\n4.先让AI提供信息\n')  

            # print('todo')
            if choose == '3':

                id_choose = int(input('\n请键入你的选择:'))
                print('\n\n')
                id = id_index[id_choose - 1]

        else:

            id = game.get_id()

        base_url = f'https://vndb.org{id}'

    clean_id = id.replace("/",'')
    chars_url = f'{base_url}/chars'
    cookie = get_cookie('vndb')
    headers = {
                'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Cookie':f'xbotcheck={cookie}; vndb_view=2-%2f{clean_id}%2fchars'
            }
    
    response = requests.get(url=chars_url,headers=headers)
    selector = parsel.Selector(response.text)

    # 返回第一个
    game_title = selector.css('.title span::text').get()
    game_desc = selector.css('.vndesc p ::text').getall()

    if game_desc[-1] != ']':

        Description =', '.join(game_desc)

    else:

        Description = ''.join(item for item in game_desc[:-3])
    
    print(f"{game_title} - {Description}")
    with open(f'{game_title}.txt','w',encoding='utf-8') as file:

        file.write(f'游戏标题: {game_title}\n游戏简介: {Description}\n')
        get_chars_data(selector,file,'Protagonist')
        get_chars_data(selector,file,'Main characters')
        get_chars_data(selector,file,'Side characters')

def get_chars_data(selector,file,role = 'Protagonist'):

    role_selector = selector.css(f'article>h1:contains("{role}")').xpath('..').get()

    if role_selector != None:

        role_chars_Selector = parsel.Selector(role_selector)
        role_chars = role_chars_Selector.css('.chardetails .stripe').getall()

        for role_char in role_chars:

            role_char = parsel.Selector(role_char)

            file.write(f'\n## {role}\n')
            print('\n')

            if role_char.css('thead small::text').get() != None:
                name = role_char.css('thead small::text').get()
                file.write(f'Name: {name}\n')
                print(f'name: {name}')

            if role_char.css('thead a::text').get() != None:
                romaji_name = role_char.css('thead a::text').get()
                file.write(f'Romaji name: {romaji_name}\n')
                print(f'Romaji name: {romaji_name}')

            if role_char.css('thead abbr::attr(title)').get() != None:
                role_char_gender = role_char.css('thead abbr::attr(title)').get()
                file.write(f'{role_char_gender}\n')
                print(f'{role_char_gender}')
        
            if role_char.css('thead span::text').get() != None:
                role_char_blood = role_char.css('thead span::text').get()
                file.write(f'Blood type: {role_char_blood}\n')
                print(f'Blood type: {role_char_blood}')

            char_rows_1 = role_char.xpath('//tr[not(parent::thead) and not(@class)]').getall()

            for char_row_1 in char_rows_1:

                char_row_1= parsel.Selector(char_row_1)
                _info = char_row_1.css('td:not(.key) ::text').getall() # 可以细分为捕获Voiced by 的title(如果有，否则就文本)
                char_rowinfo_1 = ''.join(_info)
                char_rowkey_1 =  char_row_1.css('.key::text').get()

                print(char_rowkey_1 + ': ' + char_rowinfo_1)
                file.write(f'{char_rowkey_1}: {char_rowinfo_1}\n')

            char_rows_2 = role_char.xpath('//tr[not(parent::thead) and starts-with(@class, "trait")]').getall()
            for char_row_2 in char_rows_2:

                char_row_2 = parsel.Selector(char_row_2)
                _info = []
                for node in char_row_2.xpath('.//td[not(@class="key")]/node()'):
                    if node.xpath('self::a'):
                        a_text = node.xpath('string(.)').get()
                    next_sup = node.xpath('following-sibling::*[1][self::sup]')
                    if next_sup:
                        sup_title = next_sup.xpath('@title').get()
                        if sup_title == 'Minor spoiler':
                            sup_title = '!'
                        else:
                            sup_title = '!!'
                        _info.append(f"{a_text}({sup_title})")
                    else:
                        _info.append(a_text)
                char_rowinfo_2 = ', '.join(_info)   
                char_rowkey_2 =  char_row_2.css('.key a::text').get()

                print(char_rowkey_2 + ': ' + char_rowinfo_2)
                file.write(f'{char_rowkey_2}: {char_rowinfo_2}\n')

            char_desc = role_char.css('tr .chardesc p ::text').getall()

            if char_desc != []:
                if char_desc[-1] != ']':
                    Description =''.join(char_desc)
                else:
                    Description = ''.join(item for item in char_desc[:-3]) 
                print(f'Description: {Description}') 
                file.write(f'Description: {Description}')
            file.write('\n\n')
            print('\n\n')

