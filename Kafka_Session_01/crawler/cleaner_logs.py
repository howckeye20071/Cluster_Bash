with open('/opt/modules/apache-flume-1.9.0-bin/test.log','w',encoding='utf8') as test:
    test.truncate()
    print("test.log is Cleaned!")

with open('/opt/modules/apache-flume-1.9.0-bin/nba.log','w',encoding='utf8') as nba:
    nba.truncate()
    print("nba.log is Cleaned!")
