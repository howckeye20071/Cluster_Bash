import requests
from bs4 import BeautifulSoup
import re
import datetime
import sys
import json

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

##將日期轉成所需的url
def generateURL(datelist):
    url_list = ["https://news.ebc.net.tw/Search/Result?type=date&value=" + date[0:4] +"%252F"+date[4:6]+"%252F"+date[-2:] for date in datelist]
    return  url_list


#獲得日期列表

dayStart = sys.argv[1]
dayEnd = sys.argv[2]
dateForm = '%Y%m%d'

print("Now's EBC")
url_list = generateDatelist(dateForm,dayStart,dayEnd)
for url in url_list:
    # print(url)

    for round in range(6):
        r = requests.get(url)
        soup = BeautifulSoup(r.text, 'html.parser')
        r.encoding = 'utf-8'
        # print(res.text)

        paging = soup.select('div.page-area.white-box div a')
        if paging[-1].string != '＞' :
            url = url

        else :
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
                    tags=[]
                    if len(taglist) >= 1:
                        for i in taglist:
                            tags.append(i.text)
                           # print(tags)
                    # print(new_url)


                    #TITLE
                    title = soup.find('h1').text
                    title = title.replace(' ','_').replace('\u3000','_')
                    # print('title:' + title)
                    #TIME
                    time_auth = soup.select('div.info span.small-gray-text')[0].string.strip().split()
                    time = time_auth[0] +"_"+time_auth[1]
                    if len(time_auth) > 3:
                        author = time_auth[-1]
                    elif len(time_auth) == 3:

                        if time_auth[-1][0:2] == "東森" :
                            author = ""
                        elif time_auth[-1][0:3] == "端傳媒":
                            author = time_auth[-1][-3:]
                        else:
                            author = time_auth[-1]
                    else:
                        author=""

                    # time  = append(time1)
                    # print('time:' + time)
                    # print('author:' + author)


                    #LIST
                    type_list =[]
                    group = soup.find(id='web-map')
                    type = group.find_all('a')[1].text
                    type_list.append(type)
                    #print('type_list:' + type)
                    # url
                    # url1 = 'https://news.ebc.net.tw' + i.attrs.get('href')
                    #print(url1)

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
                                text=i.text
                                # print(text)



                    else:
                        pre_text = txt_div.get_text()
                        # text = pre_text.strip()

                        for i in pre_text.split():
                            if i[0] != "【":
                                if i[0] != "●":
                                    if i[0]!= "▼":
                                        if i[0] != "▲":
                                            text += i
                    #print('text:' + text)
                    #print(" ")


# 塞進字典
                    dic = {};
                    dic['title'] = title;
                    dic['time'] = time;
                    dic['author'] = author;
                    dic['text'] = text;
                    dic['url'] = new_url;
                    dic['tags'] = tags;
                    dic['type_list'] = type_list;
                    dic['source'] = '東森';
                    dic['views'] = '';
                    dic['share'] = '';
                    dic['like'] = ''

                    with open("/opt/modules/apache-flume-1.9.0-bin/test.log", "a") as fjson:
                        fjson.write(json.dumps(dic))
                        fjson.write('\n')
                    print('.',end='')
    print("EBC Done!")
