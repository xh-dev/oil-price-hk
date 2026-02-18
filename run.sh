python get-price-info.py > price-info.json
cat price-info.json
python digest-overall-price-info.py --file price-info.json > json-data/overall.json
python digest-price-info-by-day.py --file price-info.json --days-after-today 0 > json-data/today-price-info.json
python digest-price-info-by-day.py --file price-info.json --days-after-today 1 > json-data/tomorrow-price-info.json
python digest-price-info-by-day.py --file price-info.json --days-after-today 2 > json-data/overmorrow-price-info.json
python digest-price-info-by-day.py --file price-info.json --days-after-today 3 > json-data/fourth-price-info.json
python digest-price-info-by-day.py --file price-info.json --days-after-today 4 > json-data/fifth-price-info.json
python digest-price-info-by-day.py --file price-info.json --days-after-today 5 > json-data/sixth-price-info.json
python digest-price-info-by-day.py --file price-info.json --days-after-today 6 > json-data/seventh-price-info.json
python update_md.py
