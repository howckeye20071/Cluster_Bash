import requests
from bs4 import BeautifulSoup
import re
import datetime
import sys
import json


##資料儲存於字典
def info_input(title, ptime, author, text, textUrl, tags, type_list):
    if not author:
        author = ""

    info = {}
    info['title'] = title
    info['time'] = ptime.split('_')[0]
    info['author'] = author
    info['text'] = text
    info['url'] = textUrl
    info['tags'] = tags
    info['type_list'] = type_list
    info['source'] = '新頭殼'
    info['views'] = ''
    info['share'] = ''
    info['like'] = ''

    # -------【清洗】最後清洗-------
    clean_total = ['title', 'time', 'author', 'text', 'url', 'tags']
    for i in clean_total:
        info[i] = ILLEGAL_CHARACTERS_RE.sub(r'', str(info[i]))
        info[i] = ILLEGAL_CHARACTERS_EMOJI.sub(r'', str(info[i]))
        info[i] = info[i].strip()

    return info


##爬取內文
def CrawlingText(url):
    response = requests.get(url=url)  # 以requests的get承接url
    response.encoding = response.apparent_encoding
    soup2 = BeautifulSoup(response.text, features='html.parser')  # 將response以.text獲得文檔，再用好湯接，宣告為html型式解讀

    targets1 = soup2.find('div', {'class': 'contentBox'})

    # AUTHOR
    author = targets1.find('a').string
    if not author:
        author = ""

    # TIME
    posttime_raw = targets1.find('div', {'class': 'content_date'}).get_text().strip()[
                   3:21]  # 以string獲得標籤內文，並以[2:12]擷取所要的資訊
    posttime_raw2 = posttime_raw.replace(" | ", "_")
    ptime = posttime_raw2.replace(".", "/")

    # TEXT
    text_tag = soup2.find(id='news_content')
    text_lists = text_tag.find_all('p')
    text = ""
    for i in text_lists:
        # print(i.string)
        if i.string:
            if i.string[0:] == "延伸閱讀：":
                # print("hi")
                break
            elif i.string[0:] == "▲":
                continue
            else:
                text += i.get_text()
        else:
            for j in i.get_text().split():
                if j[0] == "▲":
                    continue
                else:
                    text += j

    # TAGS
    tags = []
    tag_tags = soup2.find('div', {'class': "tag_group2"})
    tag_lists = tag_tags.find_all('a')
    for i in tag_lists:
        tag_text = i.get_text()
        tags.append(tag_text)
    return ptime, author, text, tags


##爬取新聞列表
def CrawlingNews(url):
    # print(">1")
    response = requests.get(url=url)  # 以requests的get承接url
    response.encoding = response.apparent_encoding  # 設定endoding與顯示的encoding相同
    soup = BeautifulSoup(response.text, features='html.parser')  # 將response以.text獲得文檔，再用好湯接，宣告為html型式解讀

    ## 抓取 [所需資訊]
    # target1 = soup.find('div', {'id': 'summary'})  # 找到目標區塊標籤
    # print(target1)
    # target1 = soup.find('div', {'class': 'news-top2'})
    # print(target1)
    top2news = soup.find_all('div', {'class': 'news-title'})
    # print(top2news)

    for i in top2news:

        # TITLE
        title = i.string
        # -------【清洗】【title】刪除不要的文章-------
        if '創夢實驗室》' in title:
            continue
        if '親情芬多精》' in title:
            continue
        if '職場多巴胺》' in title:
            continue
        if '小鎮之旅》' in title:
            continue
        if '立院LIVE》' in title:
            continue

        # URL
        textUrl = i.find('a').attrs.get('href')
        ptime, author, text, tags = CrawlingText(textUrl)
        type_list = ""

        # -------【清洗】【text,author】刪除不要的文章-------
        if not text:
            continue
        if author == '寵毛網petsmao資訊平台':
            continue

        tags_origi = ''
        if tags:
            if '書評' in tags:
                continue
            for tagstring in tags:
                if tagstring == tags[0]:
                    type_list = tagstring
                    continue
                if tagstring == "nownews":
                    continue
                tags_origi = tags_origi + tagstring + "、"
            tags_origi = tags_origi[0:-1]

        # -------【清洗】-------
        cleaner(title, author, text)

        # ---------------把資訊塞成陣列，並呼叫append func.---------------
        info_final = info_input(title, ptime, author, text, textUrl, tags_origi, type_list)
        appendToFile(info_final)
        # print(info_final)

    news_tags = soup.find_all('div', {'class': 'text'})  # 找到目標區塊標籤

    for i in news_tags:
        div_tagA = i.find('a', {'class': 'newsBox'})
        if div_tagA:
            textUrl = div_tagA.attrs.get('href')
            title = div_tagA.get_text().strip()  # 擷取text，並以strip()剝去\n

            # -------【清洗】【title】刪除不要的文章-------
            if '創夢實驗室》' in title:
                continue
            if '親情芬多精》' in title:
                continue
            if '職場多巴胺》' in title:
                continue
            if '小鎮之旅》' in title:
                continue
            if '立院LIVE》' in title:
                continue

            if textUrl[29:39] == url[32:42]:
                ptime, author, text, tags = CrawlingText(textUrl)
                type_list = []

                # -------【清洗】【text,author】刪除不要的文章-------
                if not text:
                    continue
                if author == '寵毛網petsmao資訊平台':
                    continue

                tags_origi = ''
                if tags:
                    if '書評' in tags:
                        continue
                    for tagstring in tags:
                        if tagstring == tags[0]:
                            type_list = tagstring
                            continue
                        if tagstring == "nownews":
                            continue
                        tags_origi = tags_origi + tagstring + "、"
                    tags_origi = tags_origi[0:-1]

                # -------【清洗】-------
                cleaner(title, author, text)

                # ---------------把資訊塞成陣列，並呼叫append func.---------------
                info_final = info_input(title, ptime, author, text, textUrl, tags_origi, type_list)
                appendToFile(info_final)
                # print(info_final)

            else:
                break


def cleaner(rawTitle, rawAuthor, rawText):
    # -------【清洗】【title】-------
    pattern = re.compile(r'^.{0,9}((戰報)|(觀點)|(投書)|(補選)|(財訊)||(新聞)|(LIVE)|(點將錄)|(最新)|(專訪)|(快訊)|(側寫)|(焦點人物))》')
    title = re.sub(pattern, "", rawTitle)
    pattern = re.compile(
        r"(((（|\()圖(）|\)))|((（|\()影(）|\)))| (羽球／)|(更新)|(NOW人物／)|(（獨家）)|(影／)|(影）)|(羽球／)|((（|\(){0,1}直播(）|\))))")
    title = re.sub(pattern, "", title)
    pattern = re.compile(r'【(司改爭鋒|讀者觀點|持續|快訊|最新|新聞快照)】')
    title = re.sub(pattern, "", title)

    title = title.replace(" ", "_").replace('\u3000', '_')

    # -------【清洗】【author】-------
    if rawAuthor:
        pattern = re.compile(r".+／")
        author = re.sub(pattern, "", rawAuthor)
    else :
        author = ""

    # -------【清洗】【text】-------
    pattern = re.compile(r'(\(|（)[0-9１２３４５６７８９０]{1,2}(/[0-9]{1,2}){0,1}(）|\))')
    text = re.sub(pattern, "", rawText)
    pattern = re.compile(
        r'▲.{0,75}(\(|（)圖.{0,1}(／|/).{0,6}(攝.{0,2}[0-9]{3,4}\.[0-9]{1,2}\.[0-9]{1,2}|攝自.{0,25}|.{0,25}照片|.{0,5}提供)(）|\))')
    text = re.sub(pattern, "", text)
    pattern = re.compile(r'▲.{1,40}(／|/){0,1}.{1,20}▲')
    text = re.sub(pattern, "", text)
    pattern = re.compile(
        r'▲(.+｜圖片來源：|.+直播來源：|.*(（|\().{0,10}圖.{0,40}(）|\))|.*影片來源：|.*(（|\().{0,10}來源.{0,40}(）|\))|.*(\(|（).{0,10}圖.{0,6}(／|/).{0,30}(）|\))|.{0,40}影片{0,1}：|(（|\().{0,1}記者.{0,20}(）|\)))')
    text = re.sub(pattern, "", text)
    pattern = re.compile(r'(\(|（)(圖|作者|圖片來源)：.{1,30}(）|\))')
    text = re.sub(pattern, "", text)
    pattern = re.compile(r'(圖|作者|圖片來源)：.{1,30}(）|\)|照片)')
    text = re.sub(pattern, "", text)
    pattern = re.compile(r'(\(|（)記者.{0,10}(/|／).{0,10}(）|\))')
    text = re.sub(pattern, "", text)
    pattern = re.compile(r'(http://|https://|www)[a-zA-Z0-9\\./_]+')
    text = re.sub(pattern, "", text)
    pattern = re.compile(r'(\n|\r|✿|❤|\(\)|（）|　| |◆|＊|▼|●|★|☆|♥|♫|①|②|③|④|⑤|⑥|⑦|⑧|⑨|⑩|►|⬇|➡|▲|※|＃|▶|○|✿|❤|（）|　|◆|＊|①|②|③|④|⑤|⑥|⑦|★|▼|☆|▲)')
    text = re.sub(pattern, "", text)

    return title, author, text


def appendToFile(info_final):
    # ---------------一篇一篇append到受監聽的文件中---------------
    with open("/opt/modules/apache-flume-1.9.0-bin/test.log", "a") as fjson:
        fjson.write(json.dumps(info_final, ensure_ascii=False))
        fjson.write('\n')
        print('.', end='')


##生成日期列表
def generateDatelist(dateForm='%Y-%m-%d', start=datetime.datetime.now().strftime('%Y-%m-%d'),
                     end=datetime.datetime.now().strftime('%Y-%m-%d')):
    datelist = []
    datelist.append(start)
    start = datetime.datetime.strptime(start, dateForm)
    end = datetime.datetime.strptime(end, dateForm)
    while start < end:
        start = start + datetime.timedelta(days=+1)
        start = start.strftime(dateForm)
        datelist.append(start)
        start = datetime.datetime.strptime(start, dateForm)
    return generateURL(datelist)


##將日期轉成所需的url
def generateURL(datelist):
    url_list = ["https://newtalk.tw/news/summary/" + date + "/#cal" for date in datelist]
    return url_list


##啟程~!
# 獲得日期列表
ILLEGAL_CHARACTERS_RE = re.compile(r'[\000-\010]|[\013-\014]|[\016-\037]')
ILLEGAL_CHARACTERS_EMOJI = re.compile(u'[\U00010000-\U0010ffff]')

if __name__ == '__main__':
    print("Now's NewTalk")
    date_start_formatted = sys.argv[1][0:4] + '-' + sys.argv[1][4:6] + '-' + sys.argv[1][6:8]
    date_stop_formatted = sys.argv[2][0:4] + '-' + sys.argv[2][4:6] + '-' + sys.argv[2][6:8]
    dayStart = date_start_formatted
    dayEnd = date_stop_formatted
    dateForm = "%Y-%m-%d"
    #
    url_list = generateDatelist(dateForm, dayStart, dayEnd)
    for url in url_list:
        CrawlingNews(url)

    # 測試用
    # url = 'https://newtalk.tw/news/view/2019-06-19/262014'
    # CrawlingNews(url)

    print("NewTalk Done!")

