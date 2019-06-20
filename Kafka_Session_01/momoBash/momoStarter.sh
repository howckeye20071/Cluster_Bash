#!/bin/sh

# test01 zookeeper
echo "-----Starting zookeeper on test01-----"
cd /opt/modules/zookeeper-3.4.14/
bin/zkServer.sh start

# test02 zookeeper
echo "-----Starting zookeeper on test02-----"
ssh test02 << remotessh
/opt/modules/zookeeper-3.4.14/bin/zkServer.sh start
echo -e "\n"
exit
remotessh

# test03 zookeeper
echo "-----Starting zookeeper on test03-----"
ssh test03 << remotessh
/opt/modules/zookeeper-3.4.14/bin/zkServer.sh start
echo -e "\n"
exit
remotessh

# test01 start-dfs.sh
echo "-----Starting hdfs on test01-----"
/opt/modules/hadoop-3.1.2/sbin/start-dfs.sh
echo -e "\n"

# test02 start-yarn.sh
echo "-----Starting yarn on test02-----"
ssh test02 << remotessh
/opt/modules/hadoop-3.1.2/sbin/start-yarn.sh
echo -e "\n"
exit
remotessh

# test03 historyserver
echo "--Starting historyserver on test03--"
ssh test03 << remotessh
/opt/modules/hadoop-3.1.2/bin/mapred --daemon start historyserver
echo -e "\n"
exit
remotessh
