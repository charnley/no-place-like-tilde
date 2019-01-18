
all: spider update

update:
	python3 updater.py --check_locations --check_internet

spider:
	python3 spiders.py

still_avaliable:
	python3 updater.py --check_avaliable

out:
	python3 get_apartmentcsv.py

