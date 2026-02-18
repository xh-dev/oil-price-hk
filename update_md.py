import datetime as dt
from zoneinfo import ZoneInfo
import json
hkt=ZoneInfo("Asia/Hong_Kong")
base_dir='json-data'


def get_overall_data(file):
    try:
        data = json.loads(open(f"{base_dir}/{file}", "r", encoding='utf-8').read())
        title = f"Official Oil Price"
        all = []
        for d in data:
            dd = {}
            dd['company'] = d['company']
            dd['product'] = d['product']
            dd['price'] = f"${d['price']:.2f} / L"

            all.append(dd)
        return (title, all)
    except Exception as ex:
        print(f"Fail to build table data: \n{open(f"{base_dir}/{file}", "r", encoding='utf-8').read()}")
        raise ex

def build_overall_table(d):
    try:
        date_str, table_data = d
        headers=list(table_data[0].keys())
        table = f"## {date_str}\n"
        table += ("| "+" | ".join([ header for header in headers]) + "| \n")
        table += ("| "+" | ".join(['---' for header in headers]) + "|\n")
        for row in table_data:
            dd = [row['company'], f"{row['product']}", row['price']]
            table += ("| "+" | ".join([ c for c in dd]) + "| \n")
    except Exception as ex:
        print(f"Fail to build table data: \n{json.dumps(d, indent=4)}")
        raise ex


    return table


def get_data(file):
    data = json.loads(open(f"{base_dir}/{file}", "r", encoding='utf-8').read())
    title=f"{data[0]['date'][:10]} ({data[0]['date_of_week']})"
    all=[]
    for d in data:
        dd={}
        dd['product']=d['product']
        dd['value']=d['value']
        if d['name'] == 'Designated Station Discount':
            dd['locations'] = ",".join([c['locations'] for c in d['criteria'] if 'locations' in c][0])
        else:
            dd['locations'] = 'any'
    
        all.append(dd)
    return (title, all)


def build_table(d):
    date_str, table_data = d
    headers=list(table_data[0].keys())
    table = f"## {date_str}\n"
    table += ("| "+" | ".join([ header for header in headers]) + "| \n")
    table += ("| "+" | ".join(['---' for header in headers]) + "|\n")
    for row in table_data:
        dd = [row['product'], f"{row['value']:.2f}", row['locations']]
        table += ("| "+" | ".join([ c for c in dd]) + "| \n")

    return table



def replacing_md(file, block, data_to_replace):
    print(f"Working with block[{block}]")
    s=""
    started=False
    ended=False
    with open(file,"r", encoding='utf-8') as f:
        for line in f.readlines():
            line=line.strip()
            if not started:
                print(f"`{line}`")
                s+=line
                s+="\n"
                if f"<!-- {block} start -->" == line:
                    print("started")
                    started = True
                    s+=data_to_replace
                    s+="\n"
            elif started and not ended:
                if f"<!-- {block} end -->" == line:
                    s+=line
                    s+="\n"
                    print("ended")
                    ended = True
                continue
            else:
                s+=line
                s+="\n"

    with open(file, "w", encoding='utf-8') as f:
        print(s)
        f.write(s)

replacing_md("README.md","overall_price_info",build_overall_table(get_overall_data("overall.json")))
replacing_md("README.md","today_s_info",build_table(get_data("today-price-info.json")))
replacing_md("README.md","tomorrow_s_info",build_table(get_data("tomorrow-price-info.json")))
replacing_md("README.md","overmorrow_s_info",build_table(get_data("overmorrow-price-info.json")))
replacing_md("README.md","fourth_s_info",build_table(get_data("fourth-price-info.json")))
replacing_md("README.md","fifth_s_info",build_table(get_data("fifth-price-info.json")))
replacing_md("README.md","sixth_s_info",build_table(get_data("sixth-price-info.json")))
replacing_md("README.md","seventh_s_info",build_table(get_data("seventh-price-info.json")))

last_modified_str=f"Last updatetime: {str(dt.datetime.now(tz=hkt).strftime('%Y-%m-%d (%a)'))}"
replacing_md("README.md","last_update_time", last_modified_str)
    
