

i=1;
while [ $i -gt 0 ];
do
date;
echo $i;
python3 run_listener.py $1 $2
sleep 1
done;


