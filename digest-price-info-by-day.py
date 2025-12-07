import json
import datetime as dt
from zoneinfo import ZoneInfo
import argparse

parser = argparse.ArgumentParser(description='Digest oil price info for a specific day.')
parser.add_argument('--days-after-today', type=int, nargs='?', default=0, choices=range(7),
                    help='A number representing the day after today (0 to 6). 0 for today, 1 for tomorrow, etc.')
parser.add_argument('-f', '--file', type=str, default='price-info.json', help='The JSON file to read price information from.')
args = parser.parse_args()

days_after_today=args.days_after_today
file_to_read=args.file

hkt = ZoneInfo("Asia/Hong_Kong")
now = (dt.datetime.now(tz=hkt) + dt.timedelta(days=days_after_today)).replace(hour=0, minute=0, second=0, microsecond=0)

data = json.loads(open(file_to_read, "r", encoding='utf-8').read())
filtered_data=[]
for product_name in data:
    product = data[product_name]
    for i in product['discounts']:
        if i['name'] in ['Designated Station Discount','Walk-in Discount']:
            i['date']=dt.datetime.strptime(i['date'],"%Y-%m-%d %H:%M:%S").replace(tzinfo=hkt)
            if i['date'] == now:
                filtered_data.append(i)

filtered_data.sort(key=lambda x: x['value'], reverse=True)
print(json.dumps(filtered_data, indent=2, default=str))


    
