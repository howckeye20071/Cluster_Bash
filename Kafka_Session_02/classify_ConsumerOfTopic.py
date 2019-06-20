from kafka import KafkaConsumer
import json
import pymysql
import jieba.analyse
import re
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
import pickle

jieba.load_userdict("/home/stu/jiebaDict/tags_set0602.txt")
jieba.analyse.set_stop_words("/home/stu/jiebaDict/stopword0601.txt")
pattern_digi = re.compile(
    r'/t| |/n|\"\"|\'\'|原PO|原po|原Po|PO|po|Po|[0-9]{1,2}|[0-9]{1,10}((\.[0-9]{1,10})|([0-9]{1,10}|個月內|幼童|成人|男|女|人|號|\.|連戰|連勝|連拜|連敗|年級|度|歲|歲少女|歲兒童|兆|千億|百億|十億|億|千萬|百萬|十萬|萬|千|百|十|元|局|場|次|下|頁|多年|年|年前|年後|日|日前|日後|周|周前|周後|週|週前|週後|月|月前|個月|個月前|月後|個月後|天|時|點|點半|分|分鐘|秒|秒鐘|公分|公尺|公里|死|傷|公斤|公克|%)+)')


def secureSQL_Distinct(info):
    url = info['url']

    db = pymysql.connect(
        host="192.168.35.168",
        port=3306,
        user="egg",
        passwd="egg",
        db="News")
    cursor = db.cursor()

    table = "news_kafka"
    # --SQL Command：  將新文章的所有資訊 INSERT或UPDATE 進SQL，並以該篇文章的url為WHERE判斷是否有過重複
    sql_distinct = "SELECT * FROM " + table + " WHERE url LIKE \'%" + url + "%\'"
    # print(sql_distinct)

    cursor.execute(sql_distinct)
    text_tuple = cursor.fetchall()

    secure_id = 0
    if text_tuple:
        secure_id = "1"

    db.close()
    # print("secure_id")
    return secure_id


def jieba_fromJson(info):
    # info含title,time,author,text,url,tags,type_list,source,views,share,like & 新加的"type_final"
    # 需回傳 tags_final 和 weight

    # 將title和text以"。"合併
    title = info['title']
    text = info['text']
    content = title + '。' + text

    max_weight = 0.0
    final_dic = {}
    tags_final = ""
    tags_list = []

    # --使用JIEBA：關鍵詞提取k,w(權重分數)
    for k, w in jieba.analyse.extract_tags(content, topK=20, withWeight=True, allowPOS=()):
        # 強制跳過正則中的停用詞
        if re.fullmatch(pattern_digi, k):
            continue
        if k == '':
            continue
        # 更新權重最大值
        if w > max_weight:
            max_weight = w
        # 更新字典中key為k的value為w
        final_dic[k] = final_dic.get(k, 0.0) + w
        tags_list.append(k)

    # 取文章原本的tags，以"、"分隔
    tags_original = info['tags']
    tags_split = tags_original.split('、')

    for tag in tags_split:
        # 強制跳過正則中的停用詞
        if re.fullmatch(pattern_digi, tag):
            continue
        if tag == '':
            continue
        # 更新字典中key為tag的value為本篇文章的w中的max
        final_dic[tag] = max_weight
        tags_list.append(tag)

    # 【final_dic】將可能出現的的'單引號'和"雙引號"全部替換成 已加過反斜線的版本
    final_dic = str(final_dic)
    if '\'' in final_dic:
        final_dic = final_dic.replace('\'', '\\\'')
    if '\"' in final_dic:
        final_dic = final_dic.replace('\"', '\\\"')
    weight = final_dic

    # 【tags_final】將去重完的tags塞成字串
    tags_setted = list(set(tags_list))
    for setted in tags_setted:
        tags_final = tags_final + setted + '、'

    # 【tags_final】刪除每段tags最後面多出來的"、"，成為真正的tags_final，準備放入新字典
    tags_final = tags_final[:-1]

    if '\'' in tags_final:
        tags_final = tags_final.replace('\'', '\\\'')
    if '\"' in tags_final:
        tags_final = tags_final.replace('\"', '\\\"')

    # 返回此文章的 tags_final 和 weight
    return tags_final, weight


def sql_fromjieba(info_jieba, tags_final, weight):
    table = "news_kafka"

    title = info_jieba['title']
    time = info_jieba['time']
    author = info_jieba['author']
    text = info_jieba['text']
    url = info_jieba['url']
    tags = info_jieba['tags']
    type_list = info_jieba['type_list']
    source = info_jieba['source']
    views = info_jieba['views']
    share = info_jieba['share']
    like = info_jieba['like']
    type_final = info_jieba['type_final']
    tags_final = tags_final
    weight = weight

    # 消滅title跟text裡的單雙引號！
    if '\'' in title:
        title = title.replace('\'', '\\\'')
    if '\"' in title:
        title = title.replace('\"', '\\\"')
    if '\'' in text:
        text = text.replace('\'', '\\\'')
    if '\"' in text:
        text = text.replace('\"', '\\\"')

    db = pymysql.connect(
        host="192.168.35.168",
        port=3306,
        user="egg",
        passwd="egg",
        db="News")
    cursor = db.cursor()

    # --SQL Command：  將新文章的所有資訊 INSERT或UPDATE 進SQL，並以該篇文章的url為WHERE判斷是否有過重複
    sql_insert = "INSERT INTO " + table + "(title, time, author, text, url, tags, type_list, source, views, share, `like`, type_final, tags_final, weight) " \
                                          "VALUES (\"" + title + "\",\"" + time + "\",\"" + author + "\",\"" + text + "\",\"" + url + "\",\"" + tags + "\",\"" + type_list + "\",\"" + source + "\",\"" + views + "\",\"" + share + "\",\"" + like + "\",\"" + type_final + "\",\"" + tags_final + "\",\"" + weight + "\")"
    # print(sql_insert)
    # # --移動指標，執行SQL Command
    cursor.execute(sql_insert)
    # # 因為有 INSERT，最後記得要Commit Transaction
    db.commit()
    db.close()
    print(url + " is Updated to DB at " + table)


def model_forTypeFinal(tags_final):
    f_open = open('/home/stu/model/new_feature_names1.txt', 'r', encoding='UTF-8')
    f_text = f_open.read()
    f_list = eval(f_text)  # 將字符串str當成有效的表達式來求值並返回計算結果
    file_set = set(f_list)
    type(f_list)

    # info_forModel = {}
    # info_forModel = info_jieba
    # info_forModel['tags_final'] = tags_final
    # info_forModel['weight'] = weight

    tags_final_forModel = tags_final.split("、")
    tags_setted =list(set(tags_final_forModel) & file_set)
    x_test = [' '.join(tags_setted)]

    f_open = open('/home/stu/model/new_vocabulary.txt', 'r', encoding='UTF-8')
    f_text = f_open.read()
    vocab = eval(f_text)

    f_open = open('/home/stu/model/new_idf_all.txt', 'r', encoding='UTF-8')
    f_text = f_open.read()
    idf_all = np.asarray(eval(f_text))

    count_v2 = CountVectorizer(vocabulary=vocab);
    counts_test = count_v2.transform(x_test);
    # print("the shape of test is " + repr(counts_test.shape))

    tfidftransformer = TfidfTransformer();
    tfidftransformer.idf_ = idf_all
    x_test = tfidftransformer.transform(counts_test);

    model_path = '/home/stu/model/new_clf.pickle'
    model = pickle.load(open(model_path, "rb"))

    y_pred = model.predict(x_test);
    preds = y_pred.tolist()
    id2c = id2c_mapping[preds[0]]

    return id2c


# ------------------------------------------

# def appendToFile(info):
#     # ---------------一篇一篇append到受監聽的文件中---------------
#     with open("/home/stu/resultPrint", "a") as fjson:
#         fjson.write(json.dumps(info,ensure_ascii=False))
#         fjson.write('\n')
#         print('.', end='')


# ------------------------------------------
# 從Kafka中取出集合物件(consumer)
consumer = KafkaConsumer(
    'flume-kafka',
    # group_id='groupA',
    # auto_offset_reset='latest',
    auto_offset_reset='earliest',
    bootstrap_servers=['192.168.35.170:9092', '192.168.35.171:9092', '192.168.35.172:9092'],
    value_deserializer=lambda m: json.loads(m.decode('utf-8'))
)

politic = ["政治", "大選", "選舉"]
social = ["社會", "蘋果爆破社", "蘋論陣線", "環保", "司法"]
international = ["國際", "兩岸", "全球", "中國"]
life = ["生活", "食尚", "健康", "氣象", "科技", "旅遊", "汽車", "玩樂", "藝文", "美食"]
entertainment = ["娛樂名人", "木瓜霞吐槽", "直擊好萊塢", "亞洲哈燒星", "娛樂", "星座", "電競", "遊戲"]
sport = ["體育焦點", "大運動場", "籃球瘋", "投打對決", "運動", "體育"]
economic = ["財經焦點", "頭家人生", "熱門話題", "財經", "企業動態"]
need_Classify = ["頭條", "要聞", "焦點"]

id2c_mapping = {0: '國際', 1: '娛樂', 2: '政治', 3: '生活', 4: '社會', 5: '經濟', 6: '運動'}

# 【第一步】篩選：建立全部已被分類到的子分類陣列，判斷此文章是否為已被分類的子分類
types_list = [politic, social, international, life, entertainment, sport, economic]
types_classified = []
for i in types_list:
    types_classified.extend(i)
# print(types_classified) #為所有已知被分進七大類的分類

# 【第二步之1】取資料：consumer經迭代後(msg)可取其value，得到"一篇文章的資訊"的字典(info)
for msg in consumer:
    info = msg.value

    #【第二步之2】確認資料唯一性：SELECT...WHERE url = info['url']
    # 透過確認回傳的tuple是否有值，回傳secure_id，若為1表示該文章url已存在，則跳過此文章
    secure_id = secureSQL_Distinct(info)
    if secure_id == "1":
        continue

    type_list = info['type_list']
    source = info['source']
    if type_list in types_classified:

        # 【第三步】JIEBA：將info 丟入Jieba，得到此文章的 tags_final 和 weight，並存在變數中(不存回info，怕反斜線的格式跑掉)
        tags_final, weight = jieba_fromJson(info)

        # 【第四步】分流：需要進模型的出列！
        if (source == '東森' and type_list in life) or (source == '東森' and type_list in international):
            # 進模型
            id2c = model_forTypeFinal(tags_final)
            info['type_final'] = id2c
        elif type_list in need_Classify:
            # 進模型
            id2c = model_forTypeFinal(tags_final)
            info['type_final'] = id2c
        else:
            # 不需要進模型的，直接新增該文章的type_final，進Jieba + 進SQL
            if type_list in politic:
                info['type_final'] = '政治'
            elif type_list in social:
                info['type_final'] = '社會'
            elif type_list in international:
                info['type_final'] = '國際'
            elif type_list in life:
                info['type_final'] = '生活'
            elif type_list in entertainment:
                info['type_final'] = '娛樂'
            elif type_list in sport:
                info['type_final'] = '運動'
            elif type_list in economic:
                info['type_final'] = '經濟'

        # # append到其中一份文件中，測試輸出是否正確
        # appendToFile(info)

        # 【第五步】進DB：已更新type_final,tags_final,weight 的 info，INSERT 或 UPDATE 回SQL
        sql_fromjieba(info, tags_final, weight)

