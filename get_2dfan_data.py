import requests 
import parsel
from vndb_classes import SearchResult,Cookie

# 可以通过主函数分别调用vndb,2dfan传参数，变量传递
def get_2dfan_data(games:list=[]):

    Result = []
    if games == []:
        games = input('输入游戏名称(请勿携带/):')

    print('\n')

    if type(games) is not list:
        games = [games]

        count = 1
        id_index = []
        bad_index = []
        titles = []

    for game in games:

        # 可以考虑只访问有介绍的内容: &filter_by=intro
        game = SearchResult(game,'2dfan')
        Result.append(game.query) # ..

        SearchResult_selector = parsel.Selector(game.url_text)
        SearchResults_text  = SearchResult_selector.css('.media').getall()

        if SearchResults_text == []:
            raise ValueError('[ERROR]: TODO!!')

        for SearchResult_text in SearchResults_text:

            SearchResult_selector = parsel.Selector(SearchResult_text)

            title = SearchResult_selector.css('.media-heading a::text').get()
            publish_time = SearchResult_selector.css('p:nth-of-type(1) span:nth-of-type(2)::text').get()
            _path = SearchResult_selector.xpath("//span[contains(text(), '介绍')]")

            if _path:

                value = _path.css('a::text').get()
                id = _path.css('a::attr(href)').get()

            else:

                value = '无'
                bad_index.append(count)

            id_index.append(id)
            titles.append(title)
            print(f'{count} - {title} - {publish_time} - {value}介绍')
            count = count + 1
        
        print('\n\n')
        choose = input('----请键入你的选择----\n1.AI查询(不联网)\n2.网络搜索\n3.手动选择\n4.先让AI提供信息\n')

        if choose == '3':

            id_choose = int(input('\n请键入你的选择:'))
            print('\n\n')
            id = id_index[id_choose - 1]
            title = titles[id_choose - 1]

        if int(id_choose) in bad_index:

            # 可以考虑不写入文件

            with open(f'{title}_2dfan.txt','w',encoding='utf-8') as file:
                file.write(f'游戏标题: {title}\n游戏介绍: \n"""\n"""')
                
            return 2

        intro_url = f'https://galge.top{id}'
        headers = {
                    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                }
        response = requests.get(url=intro_url,headers=headers)
        selector = parsel.Selector(response.text)
        end_page = selector.css('.pagination ul li:nth-last-of-type(1) a::attr(href)').get()

        if end_page == None:

            page_count = 1

        else:

            page_count = end_page.split('/')[-1]

    with open(f'{title}_2dfan.txt','w',encoding='utf-8') as file:
        file.write(f'游戏标题: {title}\n')
        get_intro_data(int(page_count),id,file,headers)

def get_intro_data(page_count,id,file,headers):

    print('游戏介绍: \n"""')
    file.write('游戏介绍: \n"""\n\n')

    for count in range(1, page_count + 1):

        intro_url = f'https://galge.top{id}/page/{count}'
        response = requests.get(intro_url,headers)
        selector = parsel.Selector(response.text)

        intro_list = selector.css('#topic-content p::text').getall()

        intro = ''.join(intro_list)

        print(intro)
        file.write(intro)
    
    print('"""')
    file.write('\n"""')
