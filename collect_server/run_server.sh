

i=1;
while [ $i -gt 0 ];
do
date;
echo $i;
python3 run_server.py
sleep 1
done;


