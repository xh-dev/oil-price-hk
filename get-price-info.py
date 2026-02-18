import requests
from urllib.parse import urlencode
from bs4 import BeautifulSoup
import re
import datetime as dt
import json


class WeekdayConverter:
    @staticmethod
    def num_con(s):
        if s=="Monday":
            return 1
        elif s=="Tuesday":
            return 2
        elif s=="Wednesday":
            return 3
        elif s=="Thursday":
            return 4
        elif s=="Friday":
            return 5
        elif s=="Saturday":
            return 6
        elif s=="Sunday":
            return 7

    @staticmethod
    def str_con(num):
        if num == 1:
            return "Monday"
        elif num == 2:
            return "Tuesday"
        elif num == 3:
            return "Wednesday"
        elif num == 4:
            return "Thursday"
        elif num == 5:
            return "Friday"
        elif num == 6:
            return "Saturday"
        elif num == 7:
            return "Sunday"

s = requests.Session()
s.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0"
})
data = s.get("https://oil-price.consumer.org.hk/en/today-discount")
# print(data)

payload={
    "auto_fuel_type": ["premium-unleaded-gasoline"],
    "company": [":company:11:"],
    "discount_type": ["walkin"]
}
rs = s.post("https://oil-price.consumer.org.hk/en/today-discount", data=payload)

recs={}
soup = BeautifulSoup(rs.text, 'html.parser')
data = [{"name": item.select_one("div>div.blr__title>strong").text, "value":item} for item in soup.select("div#loadResult>div>div.blr__inner")]
for d in data:
    recs.update({d['name']:d['value']})

def find_pump_price(elem):
    pump_price=elem.select_one("div.panel >  div.panel__heading>span>span.panel__heading-text").text
    pump_price=pump_price.replace("\r","")
    pump_price=pump_price.replace("\n","")
    pump_price=pump_price.replace("\t","")
    matcher = re.match("^Pump Price:\\$(?P<price>[\\d\\.]+)/L", pump_price)
    return float(matcher['price'])

pump_prices = {key: find_pump_price(recs[key]) for key in recs}

rs = s.get("https://oil-price.consumer.org.hk/en/weekly-discount")
soup = BeautifulSoup(rs.text, 'html.parser')

dates=[]
last_date=None
year=dt.datetime.now().year
for item in soup.select("table.tb__table.tb__headtable>thead>tr>th.tb__cell>div.tb__head>div.tb__head-sub"):
    d=dt.datetime.strptime(item.text, "%d %b").replace(year=year)
    if last_date is not None and last_date > d:
        year+=1
        d=d.replace(year=year)
    last_date=d
    dates.append(last_date)

all={}
for item in soup.select("table.tb__table.tb__item"):
    full_name = item['title'].strip()
    price = pump_prices[full_name.replace(" - ","-").split("(")[0].strip()]
    company=full_name.split(' - ')[0]
    product=full_name.split(' - ')[1]
    trs = item.select("tbody.tb__tbody >tr")
    discounts=[]
    all[full_name]={
        "name": full_name,
        "company": company,
        "product": product,
        "price": price,
        "discounts": discounts
    }
    discount_name=""
    for tr in trs:
        td_subhead = tr.select_one("td.tb__subhead")
        if td_subhead is not None:
            discount_name=td_subhead.text
        td_cells = tr.select("td.tb__cell")
        discount=[]
        for td_cell in td_cells:
            cs = int(td_cell['colspan'])
            detail = td_cell.select_one("div.tb__cell-inner>span.tb__text")
            if discount_name == "Walk-in Discount":
                t=detail.text
                value = float(re.match("-\\$(\\d+\\.\\d+)", t)[1])
                for i in range(0,cs):
                    discount.append({
                        "product": item['title'],
                        "name": discount_name,
                        "model": "discount",
                        "criteria": [],
                        "value": value
                    })
            elif discount_name == "Designated Station Discount":
                if detail is None:
                    for i in range(0,cs):
                        discount.append(None)
                else:
                    value = detail.text
                    type_of_discount=None
                    matcher=re.match("^Discount of \\$(\\d+\\.\\d{2})/L \\(Applicable to purchases of \\$(\\d+\\.{0,1}\\d{0,2}) or more after the discount\\)$", value.strip())
                    type_of_discount = None if matcher is None else "discount_for_specific_station"

                    if type_of_discount is None:
                        matcher=re.match("^Esso customers can enjoy free upgrade to purchase ([\\w ]+) at ([\\w ]+) price at ([\\w,]+) station$", value)
                        type_of_discount = None if matcher is None else "free_upgrade_of_type_of_pertol"
                    

                    if type_of_discount == "discount_for_specific_station":
                        value = matcher
                        discount_value=float(value[1])
                        minimux=float(value[2])
                        locations = td_cell.select_one("div.tooltipster__body").text.replace("\r","")
                        vvv=[]
                        for area in [i for i in locations.split("\n") if i.strip() != '']:
                            v=area.replace(" and ",", ").strip()
                            def try_match(input):
                                input = input.strip()
                                if input == "":
                                    return []
                                
                                else:
                                    matcher = re.match("^(Kowloon|New Territories): ([\\w, ]+)[,]{0,1} stations", input)
                                    if matcher is not None:
                                        return matcher[2].split(",")
                                    matcher = re.match("^(\\w+|(\\w+,)+\\w+)$", input.replace(" ",""))
                                    if matcher is not None:
                                        return input.replace(", ",",").split(",")
                                    raise Exception(f"Failed to extract location: {input}")
                            [vvv.append(vv.strip()) for vv in try_match(v) if vv.strip() != '']
                        for i in range(0,cs):
                            discount.append({
                                "product": item['title'],
                                "name": discount_name,
                                "model": "discount",
                                "criteria": [
                                    {"min_purchasing": minimux},
                                    {"locations": vvv}
                                ],
                                "value": discount_value,
                            })
                    elif type_of_discount == "free_upgrade_of_type_of_pertol":
                        value = matcher
                        to_petrol=value[1]
                        from_petrol=value[2]
                        locations=[i.strip() for i in float(value[3]).split(",") if i.strip() != '']
                        discount.append({
                            "product": item['title'],
                            "name": discount_name,
                            "model": "upgrades",
                            "criteria": [
                                {"locations": locations}
                            ],
                            "from": from_petrol,
                            "to": to_petrol,

                        })
            elif discount_name == "Credit Card Promotion":
                if detail is None:
                    for i in range(0,cs):
                        discount.append(None)
                else:
                    t=detail.text
                    type_of_discount=None
                    matcher = re.match("^([\\w ]+) Credit Card holders can enjoy \\$(\\d+\\.{0,1}\\d{0,2})/L instant discount", t.strip())
                    type_of_discount = None if matcher is None else "Specific Credit Card"

                    if type_of_discount is None:
                        matcher = re.match("^Purchasing every \\$(\\d+\\.{0,1}\\d{0,2}) of petrol \\(after discount\\) with Mastercard, customers can redeem \\$(\\d+\\.{0,1}\\d{0,2}) worth of extra same type of petrol$", t.strip())
                        type_of_discount = None if matcher is None else "Master Card with minimum purchase"

                    if type_of_discount is None:
                        matcher = re.match("^([\\w ]+) cardholders can enjoy the extra instant petrol discount of \\$(\\d+\\.{0,1}\\d{0,2})/L$", t.strip())
                        type_of_discount = None if matcher is None else "Specific Credit Card"
                    
                    if type_of_discount == "Specific Credit Card":
                        credit_card=matcher[1]
                        value = float(matcher[2])
                        for i in range(0,cs):
                            discount.append({
                                "product": item['title'],
                                "name": discount_name,
                                "model": "discount",
                                "criteria": [
                                    {"Holding": credit_card}
                                ],
                                "discount_every_unit": value
                            })
                    elif type_of_discount == "Master Card with minimum purchase":
                        value = float(matcher[1])
                        discount_value=float(matcher[2])
                        for i in range(0,cs):
                            discount.append({
                                "product": item['title'],
                                "name": discount_name,
                                "model": "voucher",
                                "criteria":[
                                    {"type_of_card": "Master Card"},
                                    {"min_purchasing": value}
                                ],
                                "value": discount_value
                            })
            elif discount_name == "Other Promotion":
                if detail is None:
                    for i in range(0,cs):
                        discount.append(None)
                else:
                    t=detail.text.strip()
                    type_of_discount=None
                    matcher = re.match("^Esso customers can enjoy premium petrol at the price of standard petrol$", t)
                    type_of_discount = None if matcher is None else "Esso Upgrade"
                    if type_of_discount == "Esso Upgrade":
                        for i in range(0,cs):
                            discount.append({
                                "product": item['title'],
                                "name": discount_name,
                                "model": "upgrades",
                                "criteria":[
                                ],
                            })
            elif discount_name == "Membership Card Promotion":
                if detail is None:
                    for i in range(0,cs):
                        discount.append(None)
                else:
                    t=detail.text.strip()
                    type_of_discount=None
                    matcher = re.match("^X card members can earn (\\d+) points upon purchases of (standard petrol|premium petrol) of \\$(\\d+\\.{0,1}\\d{0,2}) or above \\((.*)\\)$", t)
                    type_of_discount = None if matcher is None else "X card"
                    
                    if type_of_discount is None:
                        matcher = re.match("^Designated time promotion: (\\d{2}:\\d{2}) - (\\d{2}:\\d{2})$", t)
                        type_of_discount = None if matcher is None else "Sinopect Designated Time"

                    if type_of_discount is None:
                        t = t.replace(u'\xa0', ' ')
                        matcher = re.match("^PetroChina Gasoline Discount Card members can earn 1 point per \\$1 \\(after discount\\) purchase of petrol \\((.*)\\)$", t)
                        type_of_discount = None if matcher is None else "PetroChina Gasoline Discount Card"

                    if type_of_discount is None:
                        t = t.replace(u'\xa0', ' ')
                        matcher = re.match("^PetroChina Gasoline Discount Card members can enjoy an instant (HK){0,1}\$(?P<discount_value>[0-9.]+)/L discount when fueling up (standard|premium) petrol upon spending (HK){0,1}\\$(?P<minium_usage>[0-9.]+) or above$", t)
                        type_of_discount = None if matcher is None else "PetroChina Gasoline Discount Card (special discount)"

                    if type_of_discount is None:
                        matcher = re.match("^Caltex Rewards Card members can earn (\\d+) point for every (\\d+) litre(s){0,1} of (Gold|Platinum) with Techron® gasoline purchase$", t)
                        type_of_discount = None if matcher is None else "Caltex Rewards Card"

                    if type_of_discount is None:
                        matcher = re.match("^Esso Smiles members can earn (\\d+) Points for every litre of Synergy (Extra|Supreme\\+) petrol purchase \\((.*)\\)$", t)
                        type_of_discount = None if matcher is None else "Esso Similes"

                    if type_of_discount is None:
                        matcher = re.match("^Shell GO\\+ members can earn (\\d+) (Shell ){0,1}GO\\+ Point for every litre of Shell (V-Power Racing|FuelSave Unleaded) purchase( \\(.*\\)){0,1}$", t)
                        type_of_discount = None if matcher is None else "Shell GO+"

                    if type_of_discount == "X card":
                            earn_points=int(matcher[1])
                            min_purchase=float(matcher[3])
                            special_weighting_str=matcher[4]

                            special_weighting=1

                            d = {}
                            for s in special_weighting_str.split(";"):
                                s=s.strip()
                                matcher = re.match("^(\\d)X points on (Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)", s)
                                if matcher is not None:
                                    d[matcher[2]] = int(matcher[1])
                                    continue
                                matcher = re.match("^(\\d)X points from (Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday) to (Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)", s)
                                from_num = WeekdayConverter.num_con(matcher[2])
                                to_num = WeekdayConverter.num_con(matcher[3])
                                for i in range(from_num, to_num+1):
                                    d[WeekdayConverter.str_con(i)] = int(matcher[1])
                            
                            def get_locations():
                                d = detail['title'].replace("and",", ")
                                pre = "RemarkBased on discounted price.  This promotion is not applicable at "
                                suf = " stations."
                                if not d.startswith(pre) and not d.endswith(suf):
                                    raise Exception(f"Prefix[{pre}] or suffix[{sub}] not matching: {d}")
                                d = d[len(pre):len(d)-len(suf)]
                                return [dd.strip() for dd in d.split(", ") if dd.strip() != '']
                            locations = get_locations()

                            for i in range(1,8):
                                if WeekdayConverter.str_con(i) not in d:
                                    d[WeekdayConverter.str_con(i)] = 1

                            for i in range(0,cs):
                                discount.append({
                                    "product": item['title'],
                                    "name": discount_name,
                                    "model": "membership",
                                    "criteria":[
                                        {"membership-card": "X Card"},
                                        {"min_purchasing": min_purchase},
                                        {"locations-not-apply": locations}
                                    ],
                                    "points-earning": d
                                })
                    elif type_of_discount =="PetroChina Gasoline Discount Card (special discount)":
                        discount_value=float(matcher.group('discount_value'))
                        min_purchase=float(matcher.group('minium_usage'))
                        d = {}
                        for i in range(1, 8):
                            if WeekdayConverter.str_con(i) not in d:
                                d[WeekdayConverter.str_con(i)] = 1

                        for i in range(0, cs):
                            discount.append({
                                "product": item['title'],
                                "name": discount_name,
                                "model": "membership",
                                "criteria": [
                                    {"membership-card": "PetroChina Gasoline Discount Card"},
                                    {"min_purchasing": min_purchase},
                                ],
                                "discount_every_unit": discount_value
                            })
                    elif type_of_discount == "PetroChina Gasoline Discount Card":
                            special_weighting_str=matcher[1]
                            d = {}
                            for s in special_weighting_str.split(";"):
                                s=s.strip()
                                matcher = re.match("^(\\d)X points on (Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)", s)
                                if matcher is not None:
                                    d[matcher[2]] = int(matcher[1])
                                    continue
                                matcher = re.match("^(\\d)X points from (Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday) to (Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)", s)
                                from_num = WeekdayConverter.num_con(matcher[2])
                                to_num = WeekdayConverter.num_con(matcher[3])
                                for i in range(from_num, to_num+1):
                                    d[WeekdayConverter.str_con(i)] = int(matcher[1])
                            for i in range(1,8):
                                if WeekdayConverter.str_con(i) not in d:
                                    d[WeekdayConverter.str_con(i)] = 1

                            for i in range(0,cs):
                                discount.append({
                                    "product": item['title'],
                                    "name": discount_name,
                                    "model": "membership",
                                    "criteria":[
                                        {"membership-card": "PetroChina Gasoline Discount Card"},
                                    ],
                                    "points-earning-weighting": d
                                })
                    elif type_of_discount == "Caltex Rewards Card":
                            special_weighting_str=matcher[1]
                            point=int(matcher[1])
                            unit=int(matcher[2])
                            d = {}
                            for i in range(0,cs):
                                discount.append({
                                    "product": item['title'],
                                    "name": discount_name,
                                    "model": "membership",
                                    "criteria":[
                                        {"membership-card": type_of_discount},
                                    ],
                                    "points-earning": {
                                        "litre": unit,
                                        "point":point
                                    }
                                })
                    elif type_of_discount == "Esso Similes":
                            point=int(matcher[1])
                            special_weighting_str=matcher[3]
                            d = {}
                            for s in special_weighting_str.split(";"):
                                s=s.strip()
                                matcher = re.match("^(\\d)X points on (Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)", s)
                                if matcher is not None:
                                    d[matcher[2]] = int(matcher[1])
                                    continue
                                matcher = re.match("^(\\d)X points from (Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday) to (Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)", s)
                                from_num = WeekdayConverter.num_con(matcher[2])
                                to_num = WeekdayConverter.num_con(matcher[3])
                                for i in range(from_num, to_num+1):
                                    d[WeekdayConverter.str_con(i)] = int(matcher[1]) * point
                            for i in range(1,8):
                                if WeekdayConverter.str_con(i) not in d:
                                    d[WeekdayConverter.str_con(i)] = 1 * point
                            for i in range(0,cs):
                                discount.append({
                                    "product": item['title'],
                                    "name": discount_name,
                                    "model": "membership",
                                    "criteria":[
                                        {"membership-card": type_of_discount},
                                    ],
                                    "points-earning": {
                                        "litre": 1,
                                        "point": d
                                    }
                                })
                    elif type_of_discount == "Shell GO+":
                            point=int(matcher[1])
                            special_weighting_str=matcher[4]
                            d = {}
                            if special_weighting_str is not None:
                                special_weighting_str = special_weighting_str.strip()
                                special_weighting_str = special_weighting_str[1:len(special_weighting_str)-1]
                                for s in special_weighting_str.split(";"):
                                    s=s.strip()
                                    matcher = re.match("^(\\d)X points on (Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)", s)
                                    if matcher is not None:
                                        d[matcher[2]] = int(matcher[1])*point
                                        continue
                                    matcher = re.match("^(\\d)X points from (Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday) to (Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)", s)
                                    from_num = WeekdayConverter.num_con(matcher[2])
                                    to_num = WeekdayConverter.num_con(matcher[3])
                                    for i in range(from_num, to_num+1):
                                        d[WeekdayConverter.str_con(i)] = int(matcher[1]) * point
                                for i in range(1,8):
                                    if WeekdayConverter.str_con(i) not in d:
                                        d[WeekdayConverter.str_con(i)] = 1 * point
                            for i in range(1,8):
                                if WeekdayConverter.str_con(i) not in d:
                                    d[WeekdayConverter.str_con(i)] = 1 * point
                                
                            for i in range(0,cs):
                                discount.append({
                                    "product": item['title'],
                                    "name": discount_name,
                                    "model": "membership",
                                    "criteria":[
                                        {"membership-card": type_of_discount},
                                    ],
                                    "points-earning": {
                                        "litre": 1,
                                        "point": d
                                    }
                                })
                    elif type_of_discount == "Sinopect Designated Time":
                        start_time=matcher[1]
                        end_time=matcher[2]
                        t=td_cell.select_one("div.tooltipster__body").text.replace("\r","").strip()
                        matcher = re.match("^X Card members can enjoy a discount of \\$(\\d+\\.{0,1}\\d{0,2})/L$",t)
                        discount_value=float(matcher[1])
                        for i in range(0,cs):
                            discount.append({
                                "product": item['title'],
                                "name": discount_name,
                                "model": "membership",
                                "criteria":[
                                    {"membership-card": "X Card"},
                                    {"time_from": start_time},
                                    {"time_to": end_time}
                                ],
                                "discount_every_unit": discount_value
                            })
                    else:
                        print(detail.text)
                        raise Exception(f'Not expected discount type: {detail.text}')
            else:
                raise Exception(f"Not expected dicount name: {discount_name}")
        for index, d in enumerate(discount):
            if d is not None:
                d['date']=dates[index]
                d['date_of_week']=d['date'].strftime('%a')
                discounts.append(d)
        discount=[]
print(json.dumps(all, indent=2, default=str))