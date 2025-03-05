.PHONY: scrape_colgate scrape_cocacola all


ralph_lauren:
		python scripts/RL/generic_sec.py https://investor.ralphlauren.com/financial-information/sec-filings "RL" --output JSONS/ralphlauren_sec_filings.json

campbells:
		python scripts/CPB/generic_sec.py https://investor.thecampbellscompany.com/financials/sec-filings "CPB" --output JSONS/campbells_sec_filings.json

mondelez:
	python scripts/MDLZ/generic_sec.py https://ir.mondelezinternational.com/financials/sec-filings "MDLZ" --output  JSONS/mondelez_sec_filings.json

walmart:
	python scripts/WMT/generic_sec.py https://stock.walmart.com/sec-filings/all-sec-filings "WMT" --output JSONS/walmart_sec_filings.json

international_flavors:
	python scripts/IFF/generic_sec.py https://ir.iff.com/financial-information/sec-filings "IFF" --output JSONS/international_flavors_sec_filings.json

iac:
	python scripts/IAC/generic_sec.py https://ir.iac.com/sec-filings "IAC" --output JSONS/iac_sec_filings.json

core_scientific:
	python scripts/CORZ/generic_sec.py https://investors.corescientific.com/sec-filings/all-sec-filings "CORZ" --output JSONS/core_scientific_sec_filings.json

pvh:
	python scripts/PVH/generic_sec.py https://www.pvh.com/investor-relations/sec-filings "PVH" --output JSONS/pvh_sec_filings.json

pinterest:
	python3 scripts/PINS/generic_sec.py https://investor.pinterestinc.com/financials/sec-filings/default.aspx "PINS" --output JSONS/pinterest.json

workday:
	python scripts/WDAY/workday_sec.py

nvidia:
	python scripts/NVDA/nvidia_sec.py

crawford:
	python scripts/CRDA/crawford_sec.py

sec_filings:
	scrape_colgate scrape_cocacola ralph_lauren campbells mondelez walmart international_flavors iac core_scientific workday nvidia crawford pinterest

CL_media-announcements:
	python scripts/CL/CL_media-announcements.py

CL_shareholder-pattern:
	python scripts/CL/CL_shareholder-pattern.py

CL-investor-relations:
	python scripts/CL/CL-investor-relations.py

KO_company-updates:
	python scripts/KO/KO_company-updates.py

KO_poclicies-practices-reports:
	python scripts/KO/KO_poclicies-practices-reports.py

KO_press-release:
	python scripts/KO/KO_press-release.py

KO_sustainable-resource-center:
	python scripts/KO/KO_sustainable-resource-center.py

PVH_events:
	python scripts/PVH/PVH_events.py

PVH_news:
	python scripts/PVH/PVH_news.py

PVH_reports:
	python scripts/PVH/PVH_reports.py

PVH_resources:
	python scripts/PVH/PVH_resources.py

PVH_sustainable-finance:
	python scripts/PVH/PVH_sustainable-finance.py

RL_newsroom:
	python scripts/RL/RL_newsroom.py

cl_press:
	python scripts/CL/cl_press.py

corz_finance:
	python scripts/CORZ/corz_finance.py

corz_presentation:
	python scripts/CORZ/corz_presentation.py

corz_press:
	python scripts/CORZ/corz_press.py

cpb_events:
	python scripts/CPB/cpb_events.py

cpb_news:
	python scripts/CPB/cpb_news.py

crda_esg:
	python scripts/CRDA/crda_esg.py

crda_sec:
	python scripts/CRDA/crda_sec.py

dsfir_news:
	python scripts/DSFIR/dsfir_news.py

dsfir_press:
	python scripts/DSFIR/dsfir_press.py

givd_news:
	python scripts/GIVD/givd_news.py

givd_sec:
	python scripts/GIVD/givd_sec.py

iff_presentations:
	python scripts/IFF/iff_presentations.py

iff_press:
	python scripts/IFF/iff_press.py

nvda_news:
	python scripts/NVDA/nvda_news.py

nvda_press:
	python scripts/NVDA/nvda_press.py

pinterest_news:
	python scripts/PINS/pinterest_news.py

sy1_events:
	python scripts/SY1/sy1_events.py

sy1_news:
	python scripts/SY1/sy1_news.py

sy1_sec:
	python scripts/SY1/sy1_sec.py

unlv_presentations:
	python scripts/UNLV/unlv_presentations.py

unlv_press:
	python scripts/UNLV/unlv_press.py

wday_events:
	python scripts/WDAY/wday_events.py

wday_press:
	python scripts/WDAY/wday_press.py

wday_quaterly:
	python scripts/WDAY/wday_quaterly.py

wmt_esg:
	python scripts/WMT/wmt_esg.py

wmt_events:
	python scripts/WMT/wmt_events.py

wmt_news:
	python scripts/WMT/wmt_news.py

wmt_quaterly:
	python scripts/WMT/wmt_quaterly.py

merge_all:
	python scripts/WMT/mergedOutput.py

remove_duplicateLinks:
	python scripts/UTILS/remove_duplicateLinks.py

all: ralph_lauren campbells mondelez walmart international_flavors iac core_scientific workday nvidia crawford pinterest CL_media-announcements CL_shareholder-pattern CL-investor-relations KO_company-updates KO_poclicies-practices-reports KO_press-release KO_sustainable-resource-center PVH_events PVH_news PVH_reports PVH_resources PVH_sustainable-finance RL_newsroom cl_press corz_finance corz_presentation corz_press cpb_events cpb_news crda_esg crda_sec dsfir_news dfirm_press givd_news givd_sec iff_presentations iff_press nvda_news nvda_press pinterest_news sy1_events sy1_news sy1_sec unlv_presentations unlv_press wday_events wday_press wday_quaterly wmt_esg wmt_events wmt_news wmt_quaterly merge_all remove_duplicateLinks

all2:  corz_press cpb_events cpb_news crda_esg crda_sec dsfir_news dsfir_press givd_news givd_sec iff_presentations iff_press nvda_news nvda_press pinterest_news sy1_events sy1_news sy1_sec unlv_presentations unlv_press wday_events wday_press wday_quaterly wmt_esg wmt_events wmt_news wmt_quaterly merge_all remove_duplicateLinks