.PHONY: scrape_colgate scrape_cocacola all

scrape_colgate:
	python scripts/sec_fillings/generic_sec.py "https://investor.colgatepalmolive.com/sec-filings" "CL" --output JSONS/colgate_sec_filings.json

scrape_cocacola:
	python scripts/sec_fillings/generic_sec.py "https://investors.coca-colacompany.com/filings-reports/all-sec-filings" "KO" --output JSONS/cocacola_sec_filings.json

ralph_lauren:
	python scripts/sec_fillings/generic_sec.py https://investor.ralphlauren.com/financial-information/sec-filings "RL" --output JSONS/ralphlauren_sec_filings.json

campbells:
	python scripts/sec_fillings/generic_sec.py https://investor.thecampbellscompany.com/financials/sec-filings "CPB" --output JSONS/campbells_sec_filings.json

mondelez:
	python scripts/sec_fillings/generic_sec.py https://ir.mondelezinternational.com/financials/sec-filings "MDLZ" --output  JSONS/mondelez_sec_filings.json

walmart:
	python scripts/sec_fillings/generic_sec.py https://stock.walmart.com/sec-filings/all-sec-filings "WMT" --output JSONS/walmart_sec_filings.json

international_flavors:
	python scripts/sec_fillings/generic_sec.py https://ir.iff.com/financial-information/sec-filings "IFF" --output JSONS/international_flavors_sec_filings.json

iac:
	python scripts/sec_fillings/generic_sec.py https://ir.iac.com/sec-filings "IAC" --output JSONS/iac_sec_filings.json

core_scientific:
	python scripts/sec_fillings/generic_sec.py https://investors.corescientific.com/sec-filings/all-sec-filings "CLSK" --output JSONS/core_scientific_sec_filings.json

pvh:
	python scripts/sec_fillings/generic_sec.py https://www.pvh.com/investor-relations/sec-filings "PVH" --output JSONS/pvh_sec_filings.json

workday:
	python scripts/sec_fillings/workday_sec.py

nvidia:
	python scripts/sec_fillings/nvidia_sec.py

crawford:
	python scripts/sec_fillings/crawford_sec.py

all: scrape_colgate scrape_cocacola ralph_lauren campbells mondelez walmart international_flavors iac core_scientific workday nvidia crawford
