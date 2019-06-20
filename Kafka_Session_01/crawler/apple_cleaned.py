import requests
from bs4 import BeautifulSoup
import re
import datetime
import sys
import json


##生成日期列表
def generateDatelist(dateForm='%Y%m%d', start=datetime.datetime.now().strftime('%Y%m%d'),
                     end=datetime.datetime.now().strftime('%Y%m%d')):
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


# 'https://tw.appledaily.com/appledaily/archive/20190415'
# 將日期轉成所需的url
def generateURL(datelist):
    url_list = ["https://tw.appledaily.com/appledaily/archive/" + date for date in datelist]
    return url_list


def appendToFile(info_final):
    # ---------------一篇一篇append到受監聽的文件中---------------
    with open("/opt/modules/apache-flume-1.9.0-bin/test.log", "a") as fjson:
        fjson.write(json.dumps(info_final, ensure_ascii=False))
        fjson.write('\n')
        print('.', end='')


# -------------------- 標題清洗pattern -----------------------
# 取代為""   【xxx】：
pattern_title = re.compile(r'【.{0,5}】|辣蘋果：|（余艾苔）|《蘋果》|▲|（有圖）|#|＠cosme_store|\(動畫\)');
pattern_author = re.compile(r'.{0,5}：.{0,3}|.{0,5}●.{0,3}|★|▼|☆|');

# -------------------- 內文清洗pattern -----------------------
# 取代為""   xxx編輯xxx
pattern_intern = re.compile(r'【.{1,20}】');
# 取代為""   特定詞語+連結
pattern_fb = re.compile(
    r'\(記者.{0,7}\)|\(.{0,10}╱.{0,10}\)|（.{0,12}╱.{0,10}）|\(.{0,12}/.{0,10}\)|報導：.{0,7}|翻攝《每日郵報》|\(體育中心\)|綜合報導|\(圖╱.{1,3}．文╱.{1,3}\)|文╱.{1,3}．圖╱.{1,4}|報導╱.{1,3}|攝影╱.{0,3}、.{0,3}')
# 取代為""   所有連結
pattern_conn = re.compile(r'(http://|https://|www)[a-zA-Z0-9\\./_]+')
# 取代為""   特定語句
pattern_sentence = re.compile(
    r'\(見附圖\)|\(快祈禱一定要買到\)|自由作家|自殺防治安心專線：0800-788995（24小時）生命線：1995張老師專線：1980|更多資訊請上吃喝玩樂蘋果花')
# 取代為""   xxxx/xx報導
# pattern_report = re.compile(r'[\u4e00-\u9fa5]{2,4}(／|/)[\u4e00-\u9fa5]{2,4}(報導)')
# 取代為""   ✿ (多為裝飾符)
pattern_flower = re.compile(r'(\n|\r|✿|❤|\(\)|（）|　| |◆|＊|▼|●|★|☆|♥|♫|①|②|③|④|⑤|⑥|⑦|⑧|⑨|⑩|►|⬇|➡|▲)|※|＃|▶|○|✿|❤|（）|　|◆|＊|①|②|③|④|⑤|⑥|⑦|★|▼|☆')

ILLEGAL_CHARACTERS_RE = re.compile(r'[\000-\010]|[\013-\014]|[\016-\037]')
ILLEGAL_CHARACTERS_EMOJI = re.compile(u'[\U00010000-\U0010ffff]')
# -------------------- pattern宣告結束 -----------------------

# 獲得日期列表
dayStart = sys.argv[1]
dayEnd = sys.argv[2]
dateForm = "%Y%m%d"

print("Now's Apple")

url_list = generateDatelist(dateForm, dayStart, dayEnd)
for url in url_list:
    # print(url)
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'html.parser')
    count = 0
    eee = ['nclns eclnms5', 'nclns eclnms9', 'nclns eclnms7', 'nclns eclnms10', 'nclns eclnms8', 'nclns eclnmsSub']
    for jj in eee:
        title_list = soup.find_all('article', class_=jj)
        for i in title_list:

            # TYPE
            type_list_origi = i.find('h2').text
            type_list = ""
            if type_list_origi:
                for type_liststring in type_list_origi:
                    type_list = type_list + type_liststring + " "
                    t2 = type_list.split()
                    type_list = "".join(t2)
                type_list = type_list[:]

            news_list = i.find_all('a')
            for i in news_list:
                if i.attrs.get('href')[0] == 'h':

                    # URL
                    new_url = i.attrs.get('href')
                    session = requests.Session()
                    session.headers.update({
                        "Accept": "text/html,application/xhtml+xml,application/xml",
                        "Accept-Encoding": "gzip, deflate",
                        "Accept-Language": "zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7",
                        "Cache-Control": "max-age=0",
                        "Connection": "keep-alive",
                        "User-Agent": 'Mozilla/5.0 (Linux; Android 4.0.4; Galaxy Nexus Build/IMM76B) ' + 'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490.76 Mobile Safari/537.36'
                    })

                    i3 = session.post(url=new_url)
                    i3.encoding = i3.apparent_encoding
                    soup2 = BeautifulSoup(i3.text, features='html.parser')
                    header = soup2.find('header')

                    # TITLE
                    title = header.find('h2').string
                    if '今天我最美' in title:
                        continue
                    if '今日焦點' in title:
                        continue
                    if '《蘋果論壇》' in title:
                        continue
                    if '得獎名單' in title:
                        continue
                    if '蘋果全家樂' in title:
                        continue
                    if '獵人政治漫畫' in title:
                        continue
                    if '政治漫畫' in title:
                        continue
                    if '政治獵人漫畫' in title:
                        continue
                    if '看個漫畫' in title:
                        continue
                    if '昨日《蘋果》' in title:
                        continue
                    if '《蘋果日報》網站' in title:
                        continue
                    if '《蘋果新聞網》' in title:
                        continue
                    if '好片丟過來《蘋果》' in title:
                        continue
                    if '《蘋果》民調：' in title:
                        continue
                    # -------------------- 標題清洗 -----------------------
                    if re.search(pattern_title, str(title)):
                        title = pattern_title.sub('', str(title))

                    # TIME
                    t1 = header.find('time').string
                    t2 = t1.replace("建立時間：", "")
                    t3 = t2.split()
                    t4 = t3[1][0:3] + str(count)
                    time = t3[0] + '_' + t4
                    time= time.split('_')[0]
                    count += 1

                    # TEXT
                    text_author = soup2.find_all('div', class_='text')
                    text = ""
                    for i in text_author :
                        if i.find('a') :
                            continue
                        else :
                            text1 = i.text.strip()
                            text += text1
                    if text == '':
                        continue

                    text66 = text.replace("本新聞文字、照片、影片專供蘋果《好蘋友》壹會員閱覽，版權所有，禁止任何媒體、社群網站、論壇，在紙本或網路部分引用、改寫、轉貼分享，違者必究。", "")
                    content = text66.strip()

                    # -------------------- 清除後續 -----------------------
                    check_sup = content.__contains__('資料來源')
                    if check_sup:
                        split_sup = content.split('資料來源')
                        content = split_sup[0];

                    check_mark1 = content.__contains__('●')
                    if check_mark1:
                        split_mark1 = content.split('●')
                        content = split_mark1[0]

                    check_mark3 = content.__contains__('▲')
                    if check_mark3:
                        split_mark3 = content.split('▲')
                        content = split_mark3[0]

                    check_moredetail = content.__contains__('◎')
                    if check_moredetail:
                        split_moredetail = content.split('◎')
                        content = split_moredetail[0]
                    # 清除 "作者："後的所有內容
                    check_authorInText = content.__contains__('。記者')
                    if check_authorInText:
                        split_authorInText = content.split('。記者')
                        content = split_authorInText[0]

                    # -------------------- 取代單個 -----------------------
                    check_intern = re.search(pattern_intern, content)
                    if check_intern:
                        content = pattern_intern.sub('', content)

                    check_fb = re.search(pattern_fb, content)
                    if check_fb:
                        content = pattern_fb.sub('', content)

                    check_conn = re.search(pattern_conn, content)
                    if check_conn:
                        content = pattern_conn.sub('', content)

                    check_sentence = re.search(pattern_sentence, content)
                    if check_sentence:
                        content = pattern_sentence.sub('', content)

                    check_flower = re.search(pattern_flower, content)
                    if check_flower:
                        content = pattern_flower.sub('', content)

                    # AUTHOR
                    patterns = re.compile(r'【.{2,11}╱.+報導】')
                    ans = patterns.findall(text66)
                    pattern = re.compile(r'。記者.{2,7}')
                    a1 = pattern.findall(text66)
                    if ans == []:
                        if a1 != []:
                            author = a1[0][3:]
                            # print('author:' + author )
                        else:
                            author = ""
                            # print('author:' + author)
                    else:
                        a = ans[0].split("╱")
                        author = a[0][1:]
                        # print ('author:'+author)
                    if author:
                        if re.search(pattern_author, str(author)):
                            author = pattern_author.sub('', str(author));
                # -------------------- 清洗結束 -----------------------

                # 塞進字典
                info = {}
                info['title'] = title
                info['time'] = time
                info['author'] = author
                info['text'] = content
                info['url'] = new_url
                info['tags'] = ''
                info['type_list'] = type_list
                info['source'] = '蘋果'
                info['views'] = ''
                info['share'] = ''
                info['like'] = ''

                clean_total = ['title','time','author','text','url','tags']
                for i in clean_total:
                    info[i] = ILLEGAL_CHARACTERS_RE.sub(r'', str(info[i]))
                    info[i] = ILLEGAL_CHARACTERS_EMOJI.sub(r'', str(info[i]))
                    info[i] = info[i].strip()

                # append到文件中
                if info != {}:
                    appendToFile(info)

print("Apple Done!")

