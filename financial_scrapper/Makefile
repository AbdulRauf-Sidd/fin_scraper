.PHONY: scrape_colgate scrape_cocacola all

scrape_colgate:
	python temp.py "https://investor.colgatepalmolive.com/sec-filings" "CL" --output colgate_sec_filings.json

scrape_cocacola:
	python temp.py "https://investors.coca-colacompany.com/filings-reports/all-sec-filings" "KO" --output cocacola_sec_filings.json

scrape_corescientific_press:
	python corz_press.py "https://investors.corescientific.com/news-events/press-releases?page=1" "CORZ" --output corz_press.json

scrape_corescientific_presentation:
	python corz_presentation.py "https://investors.corescientific.com/news-events/presentations" "CORZ" --output corz_presentation.json


scrape_corescientific_finance:
	python corz_finance.py "https://investors.corescientific.com/financial-information/financial-results" "CORZ" --output corz_finance.json

scrape_wday_press:
	python wday_press.py "https://investor.workday.com/press-releases" "WDAY" --output wday_press.json

scrape_wday_events:
	python wday_events.py "https://investor.workday.com/events#past:2025:3" "WDAY" --output wday_events.json

scrape_wday_quarterly:
	python wday_quarterly.py "https://investor.workday.com/quarterly-results" "WDAY" --output wday_quarterly.json

scrape_iff_press:
	python iff_press.py "https://ir.iff.com/press-releases?6975432388c93f18be7b4d8222cbf202d2f07feef130201ed2393ef8b833b15d_year%5Bvalue%5D=_none&op=Filter&6975432388c93f18be7b4d8222cbf202d2f07feef130201ed2393ef8b833b15d_widget_id=6975432388c93f18be7b4d8222cbf202d2f07feef130201ed2393ef8b833b15d&form_build_id=form-bkOO9-pFrxeEqyo53ECPHSIhD5BNRO5mz4vNrzsfUAg&form_id=widget_form_base" "IFF" --output iff_press.json

scrape_iff_presentations:
	python iff_presentations.py "https://ir.iff.com/events-presentations" "IFF" --output iff_presentations.json

scrape_givd_sec:
	python givd_sec.py "https://www.givaudan.com/investors/financial-results/results-centre" "GIVD" --output givd_sec.json

scrape_givd_news:
	python givd_news.py "https://www.givaudan.com/media/media-releases?keyword=&im_givaudan_publication_year=All&tm_vid_1_names=All&tm_vid_1_names_adhoc=All" "GIVD" --output givd_news.json



all: scrape_colgate scrape_cocacola


