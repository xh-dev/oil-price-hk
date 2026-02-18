import argparse
import json

parser = argparse.ArgumentParser(description='Digest overal price info today.')
parser.add_argument('-f', '--file', type=str, default='price-info.json', help='The JSON file to read price information from.')

args = parser.parse_args()
file_to_read=args.file
data = json.loads(open(file_to_read, "r", encoding='utf-8').read())
overall_data=json.dumps([{"company":data[key]['company'], "product": data[key]['product'], 'price': data[key]['price']} for key in data], indent=2, ensure_ascii=False)
if len(overall_data) == 0:
    raise ValueError(f"No data found: {open(file_to_read, 'r', encoding='utf-8').read()}")

print(overall_data)

