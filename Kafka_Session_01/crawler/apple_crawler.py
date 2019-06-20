
import requests
from bs4 import BeautifulSoup
import  datetime
import  re
import json
import sys

##生成日期列表
def generateDatelist(dateForm = '%Y%m%d',start=datetime.datetime.now().strftime('%Y%m%d'),end=datetime.datetime.now().strftime('%Y%m%d')):
    datelist = []
    datelist.append(start)
    start = datetime.datetime.strptime(start,dateForm)
    end = datetime.datetime.strptime(end,dateForm)
    while start < end:
        start = start+datetime.timedelta(days=+1)
        start = start.strftime(dateForm)
        datelist.append(start)
        start = datetime.datetime.strptime(start,dateForm)
    return generateURL(datelist)

# 'https://tw.appledaily.com/appledaily/archive/20190415'
# 將日期轉成所需的url
def generateURL(datelist):
    url_list = ["https://tw.appledaily.com/appledaily/archive/" + date  for date in datelist]
    return  url_list

# 獲得日期列表
dayStart = sys.argv[1]
dayEnd = sys.argv[2]
dateForm = "%Y%m%d"

# content ={}
print("Now's Apple")
url_list = generateDatelist(dateForm,dayStart,dayEnd)

for url in url_list:
# print(url)
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'html.parser')
    count = 0
    eee =['nclns eclnms5','nclns eclnms9','nclns eclnms7','nclns eclnms10','nclns eclnms8','nclns eclnmsSub']
    for jj in eee :
        title_list = soup.find_all('article', class_= jj)
        for i in title_list:
            type_list = i.find('h2').text
            news_list = i.find_all('a')

            for i in news_list:
                if i.attrs.get('href')[0] == 'h':
                    new_url = i.attrs.get('href')

                    # print('type_list :'+type_list)
                    # print('url :'+new_url)
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
                    # print(i3.text)
                    i3.encoding = i3.apparent_encoding
                    soup2 = BeautifulSoup(i3.text, features='html.parser')
                    # print(soup2)
                    # if soup2.find('header')  :
                    #    header = soup2.find('header')
                    # else :
                    #     continue
                    header = soup2.find('header')
                    title = header.find('h2').string
                    # print('title:'+str(title))
                    t1 = header.find('time').string
                    t2 = t1.replace("建立時間：", "")
                    t3 = t2.split()
                    t4 = t3[1][0:3] + str(count)
                    time = t3[0] + '_' + t4
                    count += 1
                    # print('time:'+time)
                    text_author = soup2.find_all('div', class_='text')
                    text = ""
                    for i in text_author:
                        if i.find('a'):
                            continue
                        else:
                            text1 = i.text.strip()
                            text += text1

                    text66 = text.replace("本新聞文字、照片、影片專供蘋果《好蘋友》壹會員閱覽，版權所有，禁止任何媒體、社群網站、論壇，在紙本或網路部分引用、改寫、轉貼分享，違者必究。", "")
                    # print('text:'+text66)
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
                dic = {}
                dic['title'] = title
                dic['time'] = time
                dic['author'] = author
                dic['text'] = text66
                dic['url'] = new_url
                dic['tags'] = ''
                dic['type_list'] = type_list
                dic['source'] = '蘋果'
                dic['views'] = ''
                dic['share'] = ''
                dic['like'] = ''

                with open("/opt/modules/apache-flume-1.9.0-bin/test.log", "a") as fjson:
                    fjson.write(json.dumps(dic,ensure_ascii=False))
                    fjson.write('\n')
                print('.', end='')
print("Apple Done!")
