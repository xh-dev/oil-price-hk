import datetime as dt
from zoneinfo import ZoneInfo
import json

def get_data(file):
    data = json.loads(open(file, "r", encoding='utf-8').read())
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
    return all


def build_table(table_data):
    headers=list(table_data[0].keys())
    table = ("| "+" | ".join([ header for header in headers]) + "| \n")
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

replacing_md("README.md","today_s_info",build_table(get_data("today-price-info.json")))
replacing_md("README.md","tomorrow_s_info",build_table(get_data("tomorrow-price-info.json")))
replacing_md("README.md","overmorrow_s_info",build_table(get_data("overmorrow-price-info.json")))
replacing_md("README.md","fourth_s_info",build_table(get_data("fourth-price-info.json")))
replacing_md("README.md","fifth_s_info",build_table(get_data("fifth-price-info.json")))
replacing_md("README.md","sixth_s_info",build_table(get_data("sixth-price-info.json")))
replacing_md("README.md","seventh_s_info",build_table(get_data("seventh-price-info.json")))

last_modified_str=f"Last updatetime: {str(dt.datetime.now().strftime('%Y-%m-%d (%a)'))}"
replacing_md("README.md","last_update_time", last_modified_str)
    
