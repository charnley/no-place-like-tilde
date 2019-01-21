
all: spider update apartments_dump.csv

update:
	python3 updater.py --check_locations --check_internet

spider:
	python3 spiders.py

still_avaliable:
	python3 updater.py --check_avaliable

apartments_dump.csv: database.db get_apartmentcsv.py
	python3 get_apartmentcsv.py

