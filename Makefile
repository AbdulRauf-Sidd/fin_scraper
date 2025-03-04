.PHONY: scrape_colgate scrape_cocacola all

scrape_colgate:
	python scripts/sec_filings/generic_sec.py https://investor.colgatepalmolive.com/sec-filings "CL" --output JSONS/colgate_sec_filings.json

scrape_cocacola:
	python3 scripts/sec_filings/generic_sec.py https://investors.coca-colacompany.com/filings-reports/all-sec-filings "KO" --output JSONS/cocacola_sec_filings.json

ralph_lauren:
		python scripts/sec_filings/generic_sec.py https://investor.ralphlauren.com/financial-information/sec-filings "RL" --output JSONS/ralphlauren_sec_filings.json

campbells:
		python scripts/sec_filings/generic_sec.py https://investor.thecampbellscompany.com/financials/sec-filings "CPB" --output JSONS/campbells_sec_filings.json

mondelez:
	python scripts/sec_filings/generic_sec.py https://ir.mondelezinternational.com/financials/sec-filings "MDLZ" --output  JSONS/mondelez_sec_filings.json

walmart:
	python scripts/sec_filings/generic_sec.py https://stock.walmart.com/sec-filings/all-sec-filings "WMT" --output JSONS/walmart_sec_filings.json

international_flavors:
	python scripts/sec_filings/generic_sec.py https://ir.iff.com/financial-information/sec-filings "IFF" --output JSONS/international_flavors_sec_filings.json

iac:
	python scripts/sec_filings/generic_sec.py https://ir.iac.com/sec-filings "IAC" --output JSONS/iac_sec_filings.json

core_scientific:
	python scripts/sec_filings/generic_sec.py https://investors.corescientific.com/sec-filings/all-sec-filings "CLSK" --output JSONS/core_scientific_sec_filings.json

pvh:
	python scripts/sec_filings/generic_sec.py https://www.pvh.com/investor-relations/sec-filings "PVH" --output JSONS/pvh_sec_filings.json

pinterest:
	python3 scripts/sec_filings/generic_sec.py https://investor.pinterestinc.com/financials/sec-filings/default.aspx "PINS" --output JSONS/pinterest.json

workday:
	python scripts/sec_filings/workday_sec.py

nvidia:
	python scripts/sec_filings/nvidia_sec.py

crawford:
	python scripts/sec_filings/crawford_sec.py

sec_filings:
	scrape_colgate scrape_cocacola ralph_lauren campbells mondelez walmart international_flavors iac core_scientific workday nvidia crawford pinterest

CL_media-announcements:
	python scripts/CL_media-announcements.py

CL_shareholder-pattern:
	python scripts/CL_shareholder-pattern.py

CL-investor-relations
	python scripts/CL-investor-relations.py

KO_company-updates:
	python scripts/KO_company-updates.py

KO_poclicies-practices-reports:
	python scripts/KO_poclicies-practices-reports.py

KO_press-release:
	python scripts/KO_press-release.py

KO_sustainable-resource-center:
	python scripts/KO_sustainable-resource-center.py

PVH_events:
	python scripts/PVH_events.py

PVH_news:
	python scripts/PVH_news.py

PVH_reports:
	python scripts/PVH_reports.py

PVH_resources:
	python scripts/PVH_resources.py

PVH_sustainable-finance:
	python scripts/PVH_sustainable-finance.py

RL_newsroom:
	python scripts/RL_newsroom.py

all: scrape_colgate scrape_cocacola ralph_lauren campbells mondelez walmart international_flavors iac core_scientific workday nvidia crawford pinterest CL_media-announcements CL_shareholder-pattern CL-investor-relations KO_company-updates KO_poclicies-practices-reports KO_press-release KO_sustainable-resource-center PVH_events PVH_news PVH_reports PVH_resources PVH_sustainable-finance RL_newsroom
