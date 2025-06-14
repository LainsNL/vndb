import os
import json
import parsel
import re
import requests
from dotenv import load_dotenv
from vndb_classes import SearchResult
from aiclasses import GoogleProvider,OpenAiProvider
from get_cookie import get_cookie

def action_verify(your_choose: int = None,content: dict = None,_vndb_choose :int = None ) -> dict: 

    '''
    展示选择列表
    如果为None则输入选择文字,否则直接调入相关函数

    :param your_choose: 输入你的选择的类型
    :param content: 需要给定参数
    :_vndb_choose: 可选,有时第一个搜索结果是固定的
    :return: 返回选择json结果
    '''
    # 读取本地文件来获取值也行
    if your_choose == None:

        try:
            your_choose = int(input('----请键入你的选择----\n1.AI查询\n2.手动选择\n3.先让AI提供信息\n'))
        except Exception as e:
            raise ValueError('请选择正确的数字')

    if your_choose == 1:

        result = ai_action_choose('Verify',content)
        return result

    elif your_choose == 2:

        if _vndb_choose == None:
            _vndb_choose = int(input('请键入你的第一个选择(0表示不选择任何游戏): '))
        
        _2dfan_choose = int(input('请键入你的第二个选择(0表示不选择任何游戏): '))

        if _vndb_choose == 0:_vndb_choose = None
        if _2dfan_choose == 0:_2dfan_choose = None

        result = []
        _vndb_choose_json = {'result':f'{_vndb_choose}'}
        _2dfan_choose_json = {'result':f'{_2dfan_choose}'}
        result.append(_vndb_choose_json)
        result.append(_2dfan_choose_json)

        return result

    elif your_choose == 3:
        ai_action_choose('Verify',content)
        

    else:
        raise ValueError("传入的可选参数并非选项中的其中一个")

def ai_action_choose(type:str = 'Verify',content:dict = None) -> dict:

    '''
    使用Google的或者自定义OpenAi类型的模型

    :param type: 需要解决的类型
    :param content: 可选的json文本内容
    :return: 返回一个结果列表
    '''

    if type == 'Verify':

        with open('prompt.json','r',encoding='utf-8') as file:
            data = json.load(file)
        
        prompt = data["PROMPT_VERIFY_GAME"]
        Channel = os.getenv("VERIFY_GAME_CHANNEL")

        if Channel == 'Openai':
            OPENAI = OpenAiProvider()
            result = OPENAI.sendRequests(prompt,content)
            return result

        elif Channel == 'Google':
            GOOGLE = GoogleProvider()
            result = GOOGLE.sendRequests(prompt,content)
            return result

        else:
            raise ValueError(f'不支持当前渠道{Channel}')

    elif type == 'Change_glossary':

        with open('prompt.json','r',encoding='utf-8') as file:
            data = json.load(file)
        
        prompt  = data["PROMPT_CHANGE_GLOSSARY"]
        Channel = os.getenv("CHANGE_GLOSSARY_CHANNEL")

        if Channel == 'Openai':
            OPENAI = OpenAiProvider()
            result = OPENAI.sendRequests(prompt,content)
            return result

        elif Channel == 'Google':
            GOOGLE = GoogleProvider()
            result = GOOGLE.sendRequests(prompt,content)
            return result

        else:
            raise ValueError(f'不支持当前渠道{Channel}')
        
    else:
        raise ValueError(f'不支持当前类型{type}')

# TODO
def get_vndb_list(keywords:list = None):

    '''
    获取vndb的list数据,暂时先用单个数据进行演示,要求支持/v132类似数据
    错误处理暂时没做
    '''
    game = SearchResult(keywords,'vndb')
    list=[]
    id_index = []
    game_info = {}
    count = 1

    if game.is_Target() == True:

        game_info['count'] = '-1'
        game_info['id'] = game.vndb_id
        game_info['title'] = game.title
        list.append(game_info)
        print(f'Vndb有唯一结果 - {game.title}')

        return list,id_index,game

    SearchResult_selector = parsel.Selector(game.url_text)
    SearchResults_selector = SearchResult_selector.xpath('//*[contains(@class, "stripe")]//tr[not(parent::thead)]')

    if SearchResults_selector == []:
        raise ValueError('[ERROR]: TODO!!')
    
    for SearchResult_selector in SearchResults_selector:
        
        game_info['count'] = count 
        game_info['id'] = SearchResult_selector.css('a::attr("href")').get()
        game_info['title'] = SearchResult_selector.css('a::attr("title")').get()
        game_info['publish_time'] = SearchResult_selector.css('.tc_rel::text').get()

        list.append(game_info)
        id_index.append(game_info['id'])

        print(f'{count} - {game_info['title']} - {game_info['publish_time']}')
        count = count + 1
        game_info={}

    return list,id_index,game

# TODO
def get_2dfan_list(keywords:list = None):

    '''
    获取vndb的list数据,暂时先用单个数据进行演示
    错误处理暂时没做
    '''

    game = SearchResult(keywords,'2dfan')

    game_info = {}
    list=[]
    id_index = []
    bad_index = []
    count = 1

    SearchResult_selector = parsel.Selector(game.url_text)
    SearchResults_selector  = SearchResult_selector.css('.media')

    if SearchResults_selector == []:
        print('2dfan无搜索结果')
        return list,id_index,bad_index

    for SearchResult_selector in SearchResults_selector:

        _path= SearchResult_selector.xpath("//span[contains(text(), '介绍')]")

        if _path:

            value = _path.css('a::text').get()
            id = _path.css('a::attr(href)').get()

        else:

            value = '无'
            id = 'None'
            bad_index.append(count)

        game_info['count'] = count
        game_info['id'] = id
        game_info['title'] = SearchResult_selector.css('.media-heading a::text').get()
        game_info['publish_time'] = SearchResult_selector.css('p:nth-of-type(1) span:nth-of-type(2)::text').get().replace('发售日期：','')

        list.append(game_info)
        id_index.append(id)

        print(f'{count} - {game_info['title']} - {game_info['publish_time']} - {value}介绍')
        count = count + 1
        game_info={}
    
    print('\n\n')
    return list,id_index,bad_index


def get_glossary_info(type:str,threshold:int = 15) -> str:

    '''
    用于获取筛选游戏列表的补充信息

    :param threshold: 过滤术语出现次数
    '''

    pattern = r'''词语原文 : ([^\n]+)\n置信度 : ([^\n]+)\n罗马音 : ([^\n]+)\n出现次数 : ([^\n]+)\n词语翻译 : ([^\n]+)\n角色性别 : ([^\n]+)\n语义分析 : ([^\n]+)\n参考文本原文 : ※+\n((?:.*\n)+?)参考文本翻译 : ※+\n((?:.*\n)+?)'''
    with open(r'E:.\input\input_角色_日志.txt','r',encoding='utf-8') as file:
        content = file.read()

    matches = re.findall(pattern,content)

    data = []
    count = 0
    for match in matches:

        if int(match[3]) > threshold:

            if type == 'Verify':

                data.append({
                    '人名': match[0],
                    '罗马音名': match[2],
                    '相关的游戏原文': match[7].replace('\n','') 
                })

            elif type == 'Change_glossary':
                data.append({
                    '人名': match[0],
                    '置信度': match[1],
                    '罗马音名': match[2],
                    '出现次数': match[3],
                    '人名翻译': match[4],
                    '角色性别': match[5],
                    '语义分析': match[6],
                    '相关的游戏原文': match[7].replace('\n',''),
                    '文本参考翻译': match[8].replace('\n','') 
                })

        count = count + 1

    return data


def get_title_id(keyword)->list:

    glossary_info_list = get_glossary_info('Verify')

    vndb_info_list,vndb_id_index,game = get_vndb_list(keyword)
    dfan_info_list,dfan_id_index,dfan_bad_index = get_2dfan_list(keyword)

    verify_input_list = []
    user_query = {}
    user_query['user_query'] = keyword 
    
    verify_input_list.append([user_query])
    verify_input_list.append(glossary_info_list)
    verify_input_list.append(vndb_info_list)
    verify_input_list.append(dfan_info_list)

    if vndb_info_list[0]["count"] == "-1":
        vndb_choose = -1
    else:vndb_choose = None
    
    verify_input = str(verify_input_list)
    result = action_verify(your_choose = 1,_vndb_choose = vndb_choose,content = verify_input)

    try:

        vndb_count_result = int(result[0]['result'])
        if vndb_count_result == -1:
            vndb_id = game.vndb_id
        else:
            vndb_id = vndb_id_index[vndb_count_result - 1]
    except:
        vndb_id = None
    
    try:

        dfan_count_result = int(result[1]['result'])
        if dfan_count_result in dfan_bad_index:
            dfan_id = None
        else:
            dfan_id = dfan_id_index[dfan_count_result - 1]
        
    except:

        dfan_id = None

    print(vndb_id,dfan_id)

    return vndb_id,dfan_id


def get_vndb_data(id):

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
 
    with open(rf'.\output\{game_title}_vndb.json','w',encoding='utf-8') as file:

        data = []
        data = get_chars_data(data,selector,'Protagonist')
        data = get_chars_data(data,selector,'Main characters')
        data = get_chars_data(data,selector,'Side characters')
        file.write(json.dumps(data, ensure_ascii=False,indent=4))

    return data


def get_chars_data(data,selector,classification = 'Protagonist'):

    game_info = {}

    if data == []:

        game_desc = selector.css('.vndesc p ::text').getall()
        if game_desc[-1] != ']':
            game_Description =', '.join(game_desc)
        else:
            game_Description = ''.join(item for item in game_desc[:-3])

        game_info['title']= selector.css('.title span::text').get()
        game_info['Description'] = game_Description
        data.append(game_info)

    role_selector = selector.css(f'article>h1:contains("{classification}")').xpath('..')

    if role_selector != []:

        role_chars = role_selector.css('.chardetails .stripe').getall()

        for role_char in role_chars:

            role_char = parsel.Selector(role_char)

            char = {}
            char['classification'] = classification

            if role_char.css('thead small::text').get() != None:
                name = role_char.css('thead small::text').get()
                char['name'] = name

            if role_char.css('thead a::text').get() != None:
                romaji_name = role_char.css('thead a::text').get()
                char['Romaji_name'] = romaji_name

            if role_char.css('thead abbr::attr(title)').get() != None:
                role_char_gender = role_char.css('thead abbr::attr(title)').get()
                char['gender'] = role_char_gender.replace('Sex: ','')
        
            if role_char.css('thead span::text').get() != None:
                role_char_blood = role_char.css('thead span::text').get()
                char['blood_type'] = role_char_blood

            char_rows_1 = role_char.xpath('//tr[not(parent::thead) and not(@class)]').getall()

            for char_row_1 in char_rows_1:

                char_row_1= parsel.Selector(char_row_1)
                _info = char_row_1.css('td:not(.key) ::text').getall() # 可以细分为捕获Voiced by 的title(如果有，否则就文本)
                char_rowinfo_1 = ''.join(_info)
                char_rowkey_1 =  char_row_1.css('.key::text').get()

                char[f'{char_rowkey_1}'] = char_rowinfo_1

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

                char[f'{char_rowkey_2}'] = char_rowinfo_2

            char_desc = role_char.css('tr .chardesc p ::text').getall()

            if char_desc != []:
                if char_desc[-1] != ']':
                    Description =''.join(char_desc)
                else:
                    Description = ''.join(item for item in char_desc[:-3]) 

                char['Description'] = Description

            data.append(char)
        
    return data

def get_2dfan_data(id):

    intro_url = f'https://galge.top{id}'
    headers = {
                'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            }
    response = requests.get(url=intro_url,headers=headers)
    selector = parsel.Selector(response.text)
    end_page = selector.css('.pagination ul li:nth-last-of-type(1) a::attr(href)').get()
    title = selector.css('.block .navbar h3::text').get()

    if end_page == None:page_count = 1
    else:page_count = end_page.split('/')[-1]  

    with open(rf'.\output\{title}_2dfan.txt','w',encoding='utf-8') as file:
        
        list = get_2dfan_intro(int(page_count),id,headers)
        file.write(str(list))
    
    return list

def get_2dfan_intro(page_count,id,headers):

    list = ''

    for count in range(1, page_count + 1):

        intro_url = f'https://galge.top{id}/page/{count}'
        response = requests.get(intro_url,headers)
        selector = parsel.Selector(response.text)

        dfan_intro_list = selector.css('#topic-content p::text').getall()
        intro = ''.join(dfan_intro_list)
        list += intro 

    list = [list]
    return list

def main():

    load_dotenv()
    keyword = '水月 ～すいげつ～'
    vndb_id,dfan_id = get_title_id(keyword)
    input = []

    glossary_list = get_glossary_info('Change_glossary', 0)

    if vndb_id != None:
        vndb_data = get_vndb_data(vndb_id)
    else:vndb_data =[]

    if dfan_id != None:
        dfan_data = get_2dfan_data(dfan_id)
    else:dfan_data =[]

    input += [glossary_list,vndb_data,dfan_data]

    glossary_result = ai_action_choose('Change_glossary',content = str(input))

    with open(rf'.\output\{keyword}_人物.json','w', encoding='utf-8') as file:
        json.dump(glossary_result, file, ensure_ascii=False, indent=4)
    print(f'已写入文件 - {os.path.abspath(f"./output/{keyword}_人物.json")}')

# 主函数入口
if __name__ == "__main__":

    main()
