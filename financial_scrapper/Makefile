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

scrape_sy1_sec:
	python sy1_sec.py "https://www.symrise.com/investors/financial-results/" "SY1" --output sy1_sec.json

scrape_sy1_news:
	python sy1_news.py "https://www.symrise.com/newsroom/press-releases/" "SY1" --output sy1_news.json

scrape_sy1_events:
	python sy1_events.py "https://www.symrise.com/investors/financial-calendar-and-presentations/" "SY1" --output sy1_events.json

scrape_crda_sec:
	python crda_sec.py "https://www.croda.com/en-gb/investors/results-presentations-and-reports/" "CRDA" --output crda_sec.json

scrape_crda_news:
	python crda_news.py "https://www.croda.com/en-gb/investors/regulatory-news" "CRDA" --output crda_news.json

scrape_crda_esg:
	python crda_esg.py "https://www.croda.com/en-gb/investors/environmental-social-and-governance-esg" "CRDA" --output crda_esg.json

scrape_dsm_press:
	python dsm_press.py "https://investors.dsm-firmenich.com/en/investors/historical-information/results-presentations.html" "CRDA" --output dsm_press.json

scrape_nvda_press:
	python3 nvda_press.py "https://investor.nvidia.com/events-and-presentations/events-and-presentations/default.aspx" "NVDA" --output nvda_press.json

scrape_wmt_events:
	python3 wmt_events.py "https://corporate.walmart.com/news/events" "WMT" --output wmt_events.json

scrape_wmt_esg:
	python3 wmt_esg.py "https://stock.walmart.com/governance/governance-documents" "WMT" --output wmt_esg.json

scrape_wmt_quarterly:
	python3 wmt_quarterly.py "https://stock.walmart.com/financial-information/vizio-historical-financials" "WMT" --output wmt_quarterly.json

scrape_wmt_news:
	python3 wmt_news.py "https://corporate.walmart.com/content/corporate/en_us/news.tag=corporate:finance.html" "WMT" --output wmt_news.json



all: scrape_colgate scrape_cocacola


