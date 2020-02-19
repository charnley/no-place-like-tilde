
all: spider update apartments_dump.csv

view:
	sqlitebrowser database.db

install:
	pip install -r requirements.txt

install_view:
	@# https://sqlitebrowser.org/dl/
	sudo apt install sqlitebrowser

update:
	python3 updater.py --check_locations --check_internet

spider:
	python3 spiders.py

still_avaliable:
	python3 updater.py --check_avaliable

apartments_dump.csv: database.db get_apartmentcsv.py
	python3 get_apartmentcsv.py

