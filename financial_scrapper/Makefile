.PHONY: scrape_colgate scrape_cocacola all

scrape_colgate:
	python temp.py "https://investor.colgatepalmolive.com/sec-filings" "CL" --output colgate_sec_filings.json

scrape_cocacola:
	python temp.py "https://investors.coca-colacompany.com/filings-reports/all-sec-filings" "KO" --output cocacola_sec_filings.json

scrape_corescientific_press:
	python corz_press.py "https://investors.corescientific.com/news-events/press-releases?page=1" "CORZ" --output corz_press.json

scrape_corescientific_presentation:
	python corz_press.py "https://investors.corescientific.com/news-events/presentations" "CORZ" --output corz_presentation.json


all: scrape_colgate scrape_cocacola


