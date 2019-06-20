#!/bin/sh

# test03 historyserver
echo "--Stopping historyserver on test03--"
ssh test03 << remotessh
/opt/modules/hadoop-3.1.2/bin/mapred --daemon stop historyserver
echo -e "\n"
exit
remotessh

# test02 stop-yarn.sh
echo "-----Stopping yarn on test02-----"
ssh test02 << remotessh
/opt/modules/hadoop-3.1.2/sbin/stop-yarn.sh
echo -e "\n"
exit
remotessh

# test01 stop-dfs.sh
echo "-----Stopping hdfs on test01-----"
/opt/modules/hadoop-3.1.2/sbin/stop-dfs.sh
echo -e "\n"

# test01 zookeeper
echo "-----Stopping zookeeper on test01-----"
cd /opt/modules/zookeeper-3.4.14/
bin/zkServer.sh stop

# test02 zookeeper
echo "-----Stopping zookeeper on test02-----"
ssh test02 << remotessh
/opt/modules/zookeeper-3.4.14/bin/zkServer.sh stop
echo -e "\n"
exit
remotessh

# test03 zookeeper
echo "-----Stopping zookeeper on test03-----"
ssh test03 << remotessh
/opt/modules/zookeeper-3.4.14/bin/zkServer.sh stop
echo -e "\n"
exit
remotessh
