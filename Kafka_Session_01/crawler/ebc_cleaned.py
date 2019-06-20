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


##將日期轉成所需的url
def generateURL(datelist):
    url_list = [
        "https://news.ebc.net.tw/Search/Result?type=date&value=" + date[0:4] + "%252F" + date[4:6] + "%252F" + date[-2:]
        for date in datelist]
    return url_list


def appendToFile(info_final):
    # ---------------一篇一篇append到受監聽的文件中---------------
    with open("/opt/modules/apache-flume-1.9.0-bin/test.log", "a") as fjson:
        fjson.write(json.dumps(info_final, ensure_ascii=False))
        fjson.write('\n')
        print('.', end='')


# -------------------- 標題清洗pattern -----------------------
# 取代為""   【xxx】：
pattern_title = re.compile(r'【.{1,8}】');

# -------------------- 內文清洗pattern -----------------------

pattern_conn = re.compile(r'(http://|https://|www)[a-zA-Z0-9\\./_]+')
pattern_flower = re.compile(r'(\n|\r|✿|❤|\(\)|（）|　| |◆|＊|▼|●|★|☆|♥|♫|①|②|③|④|⑤|⑥|⑦|⑧|⑨|⑩|►|⬇|➡|▲)|※|＃|▶|○|✿|❤|（）|　|◆|＊|①|②|③|④|⑤|⑥|⑦|★|▼|☆')
pattern_flower1 = re.compile(r'\(\*´•ω•`\*\)/♡\*|～\^\^～\)|ლ\(･\(エ\)･|\(๑´ㅂ`๑\)|！\(=￣ω￣=\)|（◎`·ω·\'）人（\'·ω·`\*）')
pattern_1 = re.compile(
    r'（圖／翻攝.{0,10}|（@.{0,10}）|（新增網友留言）|(首圖.{0,15})|（新增影片）|（圖片取自.{0,15}臉書）|（以上圖片皆為示意圖）|（取.{0,10}粉絲團）|（點超連結看詳細介紹）|（更新影音新聞、網友回應）|（影片.{0,2}/.{0,50}）|攝:AFP/GoogleDeepMind/GOOGLE|（.{1,30}／.{1,30}）|（.{1,30}/.{1,30}）|\(.{1,30}/.{1,30}\)|（圖.{0,30}）|（影片.{0,30}）|（示意.{0,20}）|（東森新聞資料畫面）|（新增.{0,10}來源）|【.{0,20}】')
pattern_3 = re.compile(
    r'圖/.{1,15}臉書|圖/唐立淇占星幫|圖/.{0,4}社|圖／.{0,20}推特|圖/.{0,10}影片/|圖/DailyView網路溫度計|圖/|圖／.{1,15}臉書|圖／|圖/.{0,5}微博|文／')
pattern_2 = re.compile(
    r'.{0,20}Facebook）|\\n|\\r|\\t|微博）|/東森新聞\)|.{0,11}臉書.{0,10}）|facebook.{0,30}\)|twitter）|Instagram|推特）|/取自鉅亨網\)|文章來源：.{0,6}|OnLine）|Online）|moviepicks】.{0,15}提供）|Relief）|YouTube）|Youtube）|IG）|map）|Map）|News）|Salads）|DuckCompany）|Twitter）|攝）|.{0,15}併圖）|臉書、pixabay）|news）|熱講香港、東森新聞）|臉書社團《爆廢公社》）|示意圖.{0,10}）|YOUTUBE）')
pattern_4 = re.compile(
    r'Source from《.{1,100}》|鏡週刊關心您：未滿18歲禁止飲酒，飲酒過量害人害己，酒後不開車，安全有保障。珍惜生命拒絕毒品，健康無價不容毒噬。遠離家庭暴力，可通報全國保護專線113鏡週刊關心您，再給自己一次機會自殺諮詢專線：0800-788995（24小時）生命線：1995張老師專線：1980揍子他哭求鬧自殺的媽：沒錢幫妳辦後事由《鏡週刊》授權提供。')
pattern_5 = re.compile(r'想爆料、投訴、分享自己的生活點滴嗎？快來東森新聞「爆一爆」|newsreader.{0,10}tw|馬上按讚 加入噪咖粉絲團')  # !!!
pattern_6 = re.compile(r'想看更多.{1,10}的作品嗎，請上【YouTube頻道】，或是到粉絲團追蹤「.{1,10}」，精彩內容不錯過喔！|觀看影片請點此')
pattern_7 = re.compile(r'東森新聞關心您.{0,150}119|東森新聞關心您{0,100}1980|影片取自YouTube，如遭刪除請見諒。|若影片無法觀看請|尊重身體自主權！請撥打113、110')
pattern_8 = re.compile(r'生命誠可貴.{1,150}1980|家暴求助專線.{1,40}119|服務時間：週一至週五 9：00～18：00|自殺防治諮詢.{1,50}0')
pattern_9 = re.compile(r'本篇文章由.{0,10}授權提供※.{0,10}官網※.{0,10}部落格|示意圖，非當事畫面。|本文獲授權，請勿任意轉載！|民俗說法，僅供參考')
pattern_10 = re.compile(
    r'東森電視版權所有.{1,30}。|Text/MarieClaire美麗佳人Photo|本文.{1,20}提供，未經授權，請勿轉載！|Claire美麗佳人提供，未經授權，請勿轉載！】|作者言論不代表東森立場授權轉載。')

ILLEGAL_CHARACTERS_RE = re.compile(r'[\000-\010]|[\013-\014]|[\016-\037]')
ILLEGAL_CHARACTERS_EMOJI = re.compile(u'[\U00010000-\U0010ffff]')
# -------------------- pattern宣告結束 -----------------------


# 獲得日期列表
dayStart = sys.argv[1]
dayEnd = sys.argv[2]
dateForm = '%Y%m%d'

print("Now's EBC")

url_list = generateDatelist(dateForm, dayStart, dayEnd)
for url in url_list:
    for round in range(6):
        r = requests.get(url)
        soup = BeautifulSoup(r.text, 'html.parser')
        r.encoding = 'utf-8'

        paging = soup.select('div.page-area.white-box div a')
        if paging[-1].string != '＞':
            url = url
        else:
            next_url = 'https://news.ebc.net.tw' + paging[-1]['href']
            url = next_url

        target_list = soup.find_all('div', class_='news-list-box')

        for i in target_list:
            news_list = i.find_all('a')
            time_list = i.find_all('span', class_='small-gray-text')
            for i in news_list:
                if i.attrs.get('href') != None:
                    new_url = 'https://news.ebc.net.tw' + i.attrs.get('href')
                    res = requests.get(new_url)
                    soup = BeautifulSoup(res.text, 'html.parser')
                    r.encoding = 'utf-8'

                    # TAGS
                    taglist = soup.select('div.keyword a')
                    tags = ""
                    if len(taglist) >= 1:
                        for i in taglist:
                            tags = tags + str(i.text) + "、"
                        tags = tags[0:-1]

                    # TITLE
                    title = soup.find('h1').text
                    title = title.replace(' ', '_').replace('\u3000', '_')
                    # -------【清洗】【title】-------
                    if re.search(pattern_title, title):
                        title = pattern_title.sub('', title)

                    # TIME
                    time_auth = soup.select('div.info span.small-gray-text')[0].string.strip().split()
                    time = time_auth[0]
                    if len(time_auth) > 3:
                        author = time_auth[-1]
                    elif len(time_auth) == 3:

                        if time_auth[-1][0:2] == "東森":
                            author = ""
                        elif time_auth[-1][0:3] == "端傳媒":
                            author = time_auth[-1][-3:]
                        else:
                            author = time_auth[-1]
                    else:
                        author = ""

                    # TYPE
                    type_list = ""
                    group = soup.find(id='web-map')
                    type = group.find_all('a')[1].text
                    if type:
                        for j in type:
                            type_list = type_list + str(j)

                    # TEXT
                    txt_div = soup.find('div', {'class': 'raw-style'})
                    txt_target = txt_div.find_all('p')
                    text = ""
                    if len(txt_target) != 0:
                        for i in txt_target:
                            if i.string != None:
                                if len(i.string) > 1:
                                    if i.string[0] != "▼":
                                        if i.string[0] != "▲":
                                            if i.string[0] == "【":
                                                if i.string[0] == "（":
                                                    if i.string[0] == "●":
                                                        break
                                            else:
                                                text += i.string
                    elif len(txt_target) != 0:
                        for i in txt_target:
                            if i != None:
                                if len(i) > 1:
                                    text = i.text
                    else:
                        pre_text = txt_div.get_text()
                        for i in pre_text.split():
                            if i[0] != "【":
                                if i[0] != "●":
                                    if i[0] != "▼":
                                        if i[0] != "▲":
                                            text += i

                    # -------【清洗】【text】-------
                    check_sup = text.__contains__('【今日最熱門】')
                    if check_sup:
                        split_sup = text.split('【今日最熱門】')
                        text = split_sup[0]
                    check_intern = re.search(pattern_1, text)
                    if check_intern:
                        text = pattern_1.sub('', text)
                    check_fb = re.search(pattern_2, text)
                    if check_fb:
                        text = pattern_2.sub('', text)
                    check_sentence = re.search(pattern_3, text)
                    if check_sentence:
                        text = pattern_3.sub('', text)
                    check_report = re.search(pattern_4, text)
                    if check_report:
                        text = pattern_4.sub('', text)
                    check_fb = re.search(pattern_5, text)
                    if check_fb:
                        text = pattern_5.sub('', text)
                    check_fb = re.search(pattern_6, text)
                    if check_fb:
                        text = pattern_6.sub('', text)
                    check_fb = re.search(pattern_7, text)
                    if check_fb:
                        text = pattern_7.sub('', text)
                    check_fb = re.search(pattern_8, text)
                    if check_fb:
                        text = pattern_8.sub('', text)
                    check_fb = re.search(pattern_9, text)
                    if check_fb:
                        text = pattern_9.sub('', text);
                    check_fb = re.search(pattern_10, text);
                    if check_fb:
                        text = pattern_10.sub('', text);
                    check_flower = re.search(pattern_flower, text);
                    if check_flower:
                        text = pattern_flower.sub('', text);
                    check_conn = re.search(pattern_conn, text);
                    if check_conn:
                        text = pattern_conn.sub('', text);
                    # -------------------- 清洗結束 -----------------------

                    # 塞進字典
                    info = {}
                    info['title'] = title
                    info['time'] = time
                    info['author'] = author
                    info['text'] = text
                    info['url'] = new_url
                    info['tags'] = tags
                    info['type_list'] = type_list
                    info['source'] = '東森'
                    info['views'] = ''
                    info['share'] = ''
                    info['like'] = ''

                    clean_total = ['title', 'time', 'author', 'text', 'url', 'tags']
                    for i in clean_total:
                        info[i] = ILLEGAL_CHARACTERS_RE.sub(r'', str(info[i]))
                        info[i] = ILLEGAL_CHARACTERS_EMOJI.sub(r'', str(info[i]))
                        info[i] = info[i].strip()

                    # append到文件中
                    if info != {}:
                        appendToFile(info)
print("EBC Done!")

