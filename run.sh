python get-price-info.py > price-info.json
python digest-price-info-by-day.py --file price-info.json --days-after-today 0 > today-price-info.json
python digest-price-info-by-day.py --file price-info.json --days-after-today 1 > tomorrow-price-info.json
python digest-price-info-by-day.py --file price-info.json --days-after-today 2 > overmorrow-price-info.json
python digest-price-info-by-day.py --file price-info.json --days-after-today 3 > fourth-price-info.json
python digest-price-info-by-day.py --file price-info.json --days-after-today 4 > fifth-price-info.json
python digest-price-info-by-day.py --file price-info.json --days-after-today 5 > sixth-price-info.json
python digest-price-info-by-day.py --file price-info.json --days-after-today 6 > seventh-price-info.json
python update_md.py
