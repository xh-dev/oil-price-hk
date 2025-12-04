import json
import datetime as dt
from zoneinfo import ZoneInfo

file_to_read="price-info.json"

hkt = ZoneInfo("Asia/Hong_Kong")
now = dt.datetime.now(tz=hkt).replace(hour=0, minute=0, second=0, microsecond=0)

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


    
