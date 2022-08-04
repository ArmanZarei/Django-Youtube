# DDOS

# block ip
```
iptables -I INPUT -s xxx.xxx.xxx.xxx -j DROP
```

# find ip connected to server
```
netstat -ntu|awk '{print $5}'|cut -d: -f1 -s|sort|uniq -c|sort -nk1 -r\n
```

# find ping requests

run this on server
```
stdbuf -i0 -o0 -e0 tcpdump -i eth0 'icmp and icmp[icmptype]=icmp-echo' | stdbuf -i0 -o0 -e0 tee test.ping
```

then you can find people who are pining you with this code
```python3
from collections import defaultdict

pings = defaultdict(int)
with open("test.ping", "r") as f:
    for line in f.readlines()[-300:]:
        ip = line.split()[2]
        if ip.startswith("127.") or ip.startswith("10."):
            continue
        pings[ip] += 1
for ip in sorted(pings, key=lambda x: pings[x], reverse=True):
    print(f'{ip} pinged {pings[ip]} times')
```
run this code to check ping
```bash
png=` ping -c 5 185.18.214.189 | tail -n 1 | awk '{print $4}' | cut -d "/" -f 2 | cut -d "." -f 1`
echo "avg ping is $png"
if [ $png -gt 150 ]
then
		echo "dos detected"
else
		echo "ok"
fi
```

run this code for ddso attack
```bash
for i in $(seq 100)
do
	ping 185.18.214.189 &
done
```


# find number of requests per second

run this code for alerting about ddos attacks
```python3
import collections
import datetime
import re

x = 50
y = 10

months = [
    "Jan",
    "Feb",
    "Mar",
    "Apr",
    "May",
    "Jun",
    "Jul",
    "Aug",
    "Sep",
    "Oct",
    "Nov",
    "Dec",
]

lineformat = re.compile(
    r"""(?P<ipaddress>\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}) - - \[(?P<dateandtime>\d{2}\/[a-z]{3}\/\d{4}:\d{2}:\d{2}:\d{2} (\+|\-)\d{4})\] ((\"(GET|POST) )(?P<url>.+)(http\/1\.1")) (?P<statuscode>\d{3}) (?P<bytessent>\d+) (["](?P<refferer>(\-)|(.+))["]) (["](?P<useragent>.+)["])""",
    re.IGNORECASE)
all_data = collections.defaultdict(list)
with open("/var/log/nginx/access.log", "r") as f:
    for line in f:
        data = re.search(lineformat, line)
        if data:
            datadict = data.groupdict()

            dt = datadict['dateandtime']
            day = int(dt.split(':')[0].split("/")[0])
            month = months.index(dt.split(':')[0].split("/")[1]) + 1
            year = int(dt.split(':')[0].split("/")[2])
            h = int(dt.split(':')[1])
            m = int(dt.split(':')[2])
            s = int(dt.split(':')[3].split(' ')[0])
            datadict['dateandtime'] = datetime.datetime(year, month, day, h, m, s)
            all_data[datadict['ipaddress']].append(datadict)

for ip in all_data:
    l = 0
    r = 0
    for r in range(len(all_data[ip])):
        while (all_data[ip][r]['dateandtime'] - all_data[ip][l]['dateandtime']).total_seconds() > y:
            l += 1
        if r - l >= x:
            print(f'ddos attack detected at {all_data[ip][r]["dateandtime"]} from ip {ip}')

```

# proxy
add this to `/etc/nginx/sites-available/default `
```
server {
        listen 8080 default_server;

        location / {
                allow 10.8.0.0/24;
                deny all;
                proxy_pass http://185.18.214.189:8000/;

        }
}
```


# Stop after 100m
add this line to `/etc/nginx/nginx.conf` at the end of `http` part
```
client_max_body_size 100M;
```
![image](https://user-images.githubusercontent.com/36403983/182473440-a45c43df-3762-450c-bfda-d0b235c92e3f.png)
