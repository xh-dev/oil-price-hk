python get-price-info.py > price-info.json
python digest-price-info-by-day.py --file price-info.json --days-after-today 0 > today-price-info.json
python digest-price-info-by-day.py --file price-info.json --days-after-today 1 > tomorrow-price-info.json
python digest-price-info-by-day.py --file price-info.json --days-after-today 2 > overmorrow-price-info.json
python update_md.py
