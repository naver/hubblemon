
kill `ps -ef | grep server.sh | grep -v grep | awk '{print $2}'`
kill `ps -ef | grep server.py | grep -v grep | awk '{print $2}'`

kill `ps -ef | grep listener.sh | grep -v grep | awk '{print $2}'`
kill `ps -ef | grep listener.py | grep -v grep | awk '{print $2}'`

rm -rf nohup*.out

nohup bash run_server.sh > nohup_30000.out 2>&1 &

nohup bash run_listener.sh 30001 /data1/collect_listener/ > nohup_30001.out 2>&1 &
nohup bash run_listener.sh 30002 /data2/collect_listener/ > nohup_30002.out 2>&1 &
nohup bash run_listener.sh 30003 /data3/collect_listener/ > nohup_30003.out 2>&1 &
nohup bash run_listener.sh 30004 /data4/collect_listener/ > nohup_30004.out 2>&1 &
nohup bash run_listener.sh 30005 /data5/collect_listener/ > nohup_30005.out 2>&1 &
nohup bash run_listener.sh 30006 /data6/collect_listener/ > nohup_30006.out 2>&1 &
nohup bash run_listener.sh 30007 /data7/collect_listener/ > nohup_30007.out 2>&1 &
nohup bash run_listener.sh 30008 /data8/collect_listener/ > nohup_30008.out 2>&1 &
nohup bash run_listener.sh 30009 /data9/collect_listener/ > nohup_30009.out 2>&1 &
nohup bash run_listener.sh 30010 /data10/collect_listener/ > nohup_30010.out 2>&1 &

