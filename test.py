import json
strin = '''[
        {
                "event_name": "Our Purpose and Vision",
                "date": "NULL",
                "files": ["/about-us/purpose-and-vision"]
        },
        {
                "event_name": "Privacy Policy (U.S.)",
                "date": "NULL",
                "files": ["https://www.coca-cola.com/us/en/legal/privacy-policy"]
        },
        {
                "event_name": "Cookie Policy (U.S.)",
                "date": NULL,
                "files": ["https://www.coca-cola.com/us/en/legal/cookies-policy"]
        },
        {
                "event_name": "Terms of Service (U.S.)",
                "date": NULL,
                "files": ["https://www.coca-cola.com/us/en/legal/terms-of-service"]
        },
        {
                "event_name": "Usage Rights Requests (U.S.)",
                "date": NULL,
                "files": ["/policies-and-practices/usage-rights-requests"]
        },
        {
                "event_name": "Vulnerability Disclosure Policy",
                "date": NULL,
                "files": ["/policies-and-practices/vulnerability-disclosure"]
        },
        {
                "event_name": "Overview of Country Sugar Study on Labor Practices",
                "date": NULL,
                "files": ["/content/dam/company/us/en/policies/pdf/human-workplace-rights/addressing-global-issues/human-rights-in-the-coca-cola-sugar-supply-chain.pdf"]
        },
        {
                "event_name": "Sugar Study Methodology",
                "date": NULL,
                "files": ["/content/dam/company/us/en/reports/pdf/sugar-study-methodology-overview.pdf"]
        },
        {
                "event_name": "Country Reports",
                "date": NULL,
                "files": ["/policies-and-practices/country-sugar-studies"]
        },
        {
                "event_name": "Transparency in Partnerships",
                "date": NULL,
                "files": ["https://www.coca-colacompany.com/policies-and-practices/transparency"]
        },
        {
                "event_name": "2023 Environmental Update",
                "date": 2023,
                "files": ["/content/dam/company/us/en/reports/2023-environmental-update/2023-environmental-update.pdf"]
        },
        {
                "event_name": "2023 CDP Climate Change Response",
                "date": 2023,
                "files": ["https://www.coca-colacompany.com/content/dam/company/us/en/policies/pdf/sustainability/2023-cdp-climate-change-response.pdf"]
        },
        {
                "event_name": "2023 CDP Forests Response",
                "date": 2023,
                "files": ["/content/dam/company/us/en/policies/pdf/sustainability/2023-CDP-Forests-Response.pdf"]
        },
        {
                "event_name": "2023 CDP Water Response",
                "date": 2023,
                "files": ["/content/dam/company/us/en/policies/pdf/sustainability/2023-CDP-Water-Response.pdf"]
        },
        {
                "event_name": "2022 Business & Sustainability Report",
                "date": 2022,
                "files": ["/content/dam/company/us/en/reports/coca-cola-business-sustainability-report-2022.pdf"]
        },
        {
                "event_name": "2022 Business & Sustainability Report Highlights",
                "date": 2022,
                "files": ["/content/dam/company/us/en/reports/2022-business-report/coca-cola-business-and-sustainability-report-2022-highlights.pdf"]
        },
        {
                "event_name": "2022 Reporting Frameworks & SDGs",
                "date": 2022,
                "files": ["/content/company/us/en/reports/2022-business-report/2022-reporting-framework-indexes.pdf"]
        },
        {
                "event_name": "2022 CDP Climate Change Response",
                "date": 2022,
                "files": ["https://www.coca-colacompany.com/content/dam/company/us/en/policies/pdf/sustainability/2022-cdp-climate-change-response.pdf"]
        },
        {
                "event_name": "2022 CDP Forests Response",
                "date": 2022,
                "files": ["/content/dam/company/us/en/policies/pdf/sustainability/2022-cdp-forests-response.pdf"]
        },
        {
                "event_name": "2022 CDP Water Response",
                "date": 2022,
                "files": ["/content/dam/company/us/en/policies/pdf/sustainability/2022-cdp-water-response.pdf"]
        },
        {
                "event_name": "2021 Business & Environmental, Social and Governance Report",
                "date": 2021,
                "files": ["/content/dam/company/us/en/reports/coca-cola-business-environmental-social-governance-report-2021.pdf"]
        },
        {
                "event_name": "2021 Business & Environmental, Social and Governance Report Highlights",
                "date": 2021,
                "files": ["/content/dam/company/us/en/reports/coca-cola-business-environmental-social-governance-report-2021-highlights.pdf"]
        },
        {
                "event_name": "2021 Reporting Frameworks & SDGs",
                "date": 2021,
                "files": ["/content/dam/company/us/en/policies/pdf/sustainability/2021-reporting-framework-indexes.pdf"]
        },
        {
                "event_name": "2021 World Without Waste Report",
                "date": 2021,
                "files": ["/reports/world-without-waste-2021"]
        },
        {
                "event_name": "2021 Carbon Accounting Manual",
                "date": 2021,
                "files": ["/content/dam/company/us/en/policies/pdf/sustainability/2021-tccc-carbon-accounting-manual.pdf"]
        },
        {
                "event_name": "2021 CDP Climate Change Response",
                "date": 2021,
                "files": ["https://www.coca-colacompany.com/content/dam/company/us/en/policies/pdf/sustainability/2021-cdp-climate-change-response.pdf"]
        },
        {
                "event_name": "2021 CDP Forests Response",
                "date": 2021,
                "files": ["/content/dam/company/us/en/policies/pdf/sustainability/2021-cdp-forests-response.pdf"]
        },
        {
                "event_name": "2021 CDP Water Response",
                "date": 2021,
                "files": ["/content/dam/company/us/en/policies/pdf/sustainability/2021-cdp-water-response.pdf"]
        },
        {
                "event_name": "2020 Business & Environmental, Social and Governance Report",
                "date": 2020,
                "files": ["/reports/business-environmental-social-governance-report-2020"]
        },
        {
                "event_name": "2020 Business & Environmental, Social and Governance Report Highlights",
                "date": 2020,
                "files": ["/content/dam/company/us/en/reports/coca-cola-business-environmental-social-governance-report-2020-highlights.pdf"]
        },
        {
                "event_name": "2020 Reporting Frameworks & SDGs",
                "date": 2020,
                "files": ["/content/dam/company/us/en/policies/pdf/sustainability/2020-reporting-framework-indexes.pdf"]
        },
        {
                "event_name": "2020 World Without Waste Report",
                "date": 2020,
                "files": ["/reports/world-without-waste-2020"]
        },
        {
                "event_name": "2020 5by20 Report",
                "date": 2020,
                "files": ["/content/dam/company/us/en/reports/pdf/coca-cola-5by20-report-march-2021.pdf"]
        },
        {
                "event_name": "2020 CDP Climate Change Response",
                "date": 2020,
                "files": ["https://www.coca-colacompany.com/content/dam/company/us/en/policies/pdf/sustainability/2020-cdp-climate-change-response.pdf"]
        },
        {
                "event_name": "2020 CDP Water Response",
                "date": 2020,
                "files": ["/content/dam/company/us/en/policies/pdf/sustainability/2020-cdp-water-response.pdf"]
        },
        {
                "event_name": "2019 Business & Sustainability Report",
                "date": 2019,
                "files": ["/content/dam/company/us/en/reports/coca-cola-business-and-sustainability-report-2019.pdf"]
        },
        {
                "event_name": "2019 Business & Sustainability Report Highlights",
                "date": 2019,
                "files": ["/content/dam/company/us/en/reports/coca-cola-business-and-sustainability-report-highlights-2019.pdf"]
        },
        {
                "event_name": "2019 Reporting Framework Indexes",
                "date": 2019,
                "files": ["/content/dam/company/us/en/reports/pdf/2019-reporting-framework-indexes.pdf"]
        },
        {
                "event_name": "2019 World Without Waste Report",
                "date": 2019,
                "files": ["/content/dam/company/us/en/reports/pdf/coca-cola-world-without-waste-report-2019.pdf"]
        },
        {
                "event_name": "2019 Water Progress Update",
                "date": 2019,
                "files": ["/content/dam/company/us/en/reports/pdf/water-progress-update-2019.pdf"]
        },
        {
                "event_name": "2019 Water Replenishment Projects",
                "date": 2019,
                "files": ["/content/dam/company/us/en/reports/pdf/2019-Water-Replenishment-Projects.pdf"]
        },
        {
                "event_name": "2019 Sustainable Ingredients Policy",
                "date": 2019,
                "files": ["/content/dam/company/us/en/reports/pdf/sustainable-ingredients-policy.pdf"]
        },
        {
                "event_name": "2019 CDP Climate Change Response",
                "date": 2019,
                "files": ["https://www.coca-colacompany.com/content/dam/company/us/en/policies/pdf/sustainability/2019-cdp-climate-change-response.pdf"]
        },
        {
                "event_name": "2019 CDP Water Response",
                "date": 2019,
                "files": ["/content/dam/company/us/en/policies/pdf/sustainability/2019-cdp-water-response.pdf"]
        },
        {
                "event_name": "2018 Business & Sustainability Report",
                "date": 2018,
                "files": ["/content/dam/company/us/en/policies/pdf/sustainability/coca-cola-business-and-sustainability-report-2018.pdf"]
        },
        {
                "event_name": "2018 World Without Waste Progress Report",
                "date": 2018,
                "files": ["/content/dam/company/us/en/reports/pdf/world-without-waste-report-2018.pdf"]
        },
        {
                "event_name": "2018 Water Stewardship Progress Report",
                "date": 2018,
                "files": ["/content/dam/company/us/en/policies/pdf/sustainability/coca-cola-business-and-sustainability-report-2018.pdf#page=26"]
        },
        {
                "event_name": "2018 Climate Report",
                "date": 2018,
                "files": ["/content/dam/company/us/en/policies/pdf/sustainability/2018-climate-report.pdf"]
        },
        {
                "event_name": "2018 CDP Climate Change Response",
                "date": 2018,
                "files": ["https://www.coca-colacompany.com/content/dam/company/us/en/policies/pdf/sustainability/2018-cdp-climate-change-response.pdf"]
        },
        {
                "event_name": "2018 CDP Water Response",
                "date": 2018,
                "files": ["/content/dam/company/us/en/policies/pdf/sustainability/2018-cdp-water-response.pdf"]
        },
        {
                "event_name": "2018 GRI Index",
                "date": 2018,
                "files": ["/content/dam/company/us/en/policies/pdf/sustainability/gri-index-2018.pdf"]
        },
        {
                "event_name": "2017 Sustainability Report",
                "date": 2017,
                "files": ["/content/dam/company/us/en/policies/pdf/sustainability/2017-sustainability-report-the-coca-cola-company.pdf"]
        },
        {
                "event_name": "2016 Sustainability Report",
                "date": 2016,
                "files": ["/content/dam/company/us/en/policies/pdf/sustainability/2016-sustainability-report-the-coca-cola-company.pdf"]
        },
        {
                "event_name": "Principles for Sustainable Agriculture",
                "date": NULL,
                "files": ["/policies-and-practices/principles-for-sustainable-agriculture"]
        },
        {
                "event_name": "Animal Health and Welfare Guiding Principles",
                "date": NULL,
                "files": ["/policies-and-practices/animal-health-and-welfare-guiding-principles"]
        },
        {
                "event_name": "Occupational Health & Safety Policy",
                "date": NULL,
                "files": ["/policies-and-practices/occupational-health-and-safety-policy"]
        },
        {
                "event_name": "Quality & Food Safety Policy",
                "date": NULL,
                "files": ["/policies-and-practices/quality-and-food-safety-policy"]
        },
        {
                "event_name": "Environmental Policy",
                "date": NULL,
                "files": ["/policies-and-practices/environmental-policy"]
        },
        {
                "event_name": "Coca-Cola Commitment to the UN Global Compact",
                "date": NULL,
                "files": ["/policies-and-practices/coca-cola-commitment-to-the-un-global-compact"]
        },
        {
                "event_name": "2024 Sustainable Commercial Paper Program Indication Report",
                "date": 2024,
                "files": ["/content/dam/company/us/en/policies/pdf/sustainability/2024-Sustainable-Commerical-Paper-Program-Indication-Report.pdf"]
        },
        {
                "event_name": "Code of Business Conduct",
                "date": NULL,
                "files": ["/policies-and-practices/code-of-business-conduct"]
        },
        {
                "event_name": "Anti-Bribery Policy",
                "date": NULL,
                "files": ["/policies-and-practices/anti-bribery-policy"]
        },
        {
                "event_name": "Reporting Ethics Concerns",
                "date": NULL,
                "files": ["/policies-and-practices/reporting-ethics-concerns"]
        },
        {
                "event_name": "Responsible Marketing Policy",
                "date": NULL,
                "files": ["/policies-and-practices/responsible-marketing-policy"]
        },
        {
                "event_name": "Digital Media Principles",
                "date": NULL,
                "files": ["/policies-and-practices/responsible-digital-media-principles"]
        },
        {
                "event_name": "Marketing Responsibly in the U.S.",
                "date": NULL,
                "files": ["/policies-and-practices/marketing-responsibly-in-the-united-states"]
        },
        {
                "event_name": "Global School Beverage Policy",
                "date": NULL,
                "files": ["/policies-and-practices/global-school-beverage-policy"]
        },
        {
                "event_name": "Responsible Alcohol Marketing Policy",
                "date": NULL,
                "files": ["/policies-and-practices/responsible-alcohol-marketing-policy"]
        },
        {
                "event_name": "Hateful Activity Policy",
                "date": NULL,
                "files": ["/policies-and-practices/hateful-activity-policy"]
        },
        {
                "event_name": "DMCA Requests",
                "date": NULL,
                "files": ["/policies-and-practices/dmca-request"]
        },
        {
                "event_name": "Prohibition on Cartel Activity",
                "date": NULL,
                "files": ["/policies-and-practices/prohibition-on-cartel-activity"]
        },
        {
                "event_name": "Alcohol Social Media Community Guidelines",
                "date": NULL,
                "files": ["/content/dam/company/us/en/reports/The-Coca-Cola-Company-Alcohol-Social-Media-Community-Guidelines.pdf"]
        },
        {
                "event_name": "Shareowners Main Page",
                "date": NULL,
                "files": ["https://investors.coca-colacompany.com/shareowners"]
        },
        {
                "event_name": "Public Policy & Political Engagement",
                "date": NULL,
                "files": ["/policies-and-practices/public-policy-and-political-engagement"]
        },
        {
                "event_name": "Coca-Cola PAC & Corporate Political Contributions",
                "date": NULL,
                "files": ["/policies-and-practices/political-contributions"]
        },
        {
                "event_name": "Lobbying Disclosure Reports (LD-2 & LD-203)",
                "date": NULL,
                "files": ["/policies-and-practices/lobbying-disclosure-reports"]
        },
        {
                "event_name": "2023 Human Rights Update",
                "date": 2023,
                "files": ["/content/dam/company/us/en/reports/2023-data-updates/2023-human-rights-update.pdf"]
        },
        {
                "event_name": "2023 Workplace and Safety Update",
                "date": 2023,
                "files": ["/content/dam/company/us/en/reports/2023-data-updates/2023-workplace-and-safety-update.pdf"]
        },
        {
                "event_name": "2022 Human Rights Overview",
                "date": 2022,
                "files": ["/content/dam/company/us/en/policies/pdf/social/human-rights-overview-2022.pdf"]
        },
        {
                "event_name": "Global Human Rights Policy (English)",
                "date": NULL,
                "files": ["/content/dam/company/us/en/reports/pdf/CocaCola_Global%20Human%20Rights%20Policy_Document_20240419_v9.15.pdf"]
        },
        {
                "event_name": "Global Human Rights Policy (Translations)",
                "date": NULL,
                "files": ["/policies-and-practices/human-rights-policy-languages"]
        },
        {
                "event_name": "Human Rights Policy Poster (English)",
                "date": NULL,
                "files": ["/content/dam/company/us/en/reports/pdf/2024-04%20-%20Coca-Cola%20-%20HRP%20poster%20-%20English%20-%20ONLINE%20-%20v2.4.pdf"]
        },
        {
                "event_name": "Human Rights Policy Poster (Translations)",
                "date": NULL,
                "files": ["/policies-and-practices/human-rights-policy-posters"]
        },
        {
                "event_name": "Supplier Guiding Principles",
                "date": NULL,
                "files": ["/policies-and-practices/supplier-guiding-principles"]
        },
        {
                "event_name": "Supplier Guiding Principles - Languages",
                "date": NULL,
                "files": ["/policies-and-practices/supplier-guiding-principles-languages"]
        },
        {
                "event_name": "Supplier Code of Business Conduct",
                "date": NULL,
                "files": ["/policies-and-practices/supplier-code-of-business-conduct"]
        },
        {
                "event_name": "Supplier Code of Business Conduct - Languages",
                "date": NULL,
                "files": ["/policies-and-practices/supplier-code-of-business-conduct-languages"]
        },
        {
                "event_name": "Human Rights Report",
                "date": NULL,
                "files": ["/content/dam/company/us/en/policies/pdf/human-workplace-rights/addressing-global-issues/the-coca-cola-companys-human-rights-report.pdf"]
        },
        {
                "event_name": "Human & Workplace Rights Materials for Employees",
                "date": NULL,
                "files": ["/policies-and-practices/human-and-workplace-rights-materials-for-employees"]
        },
        {
                "event_name": "Safety & Health",
                "date": NULL,
                "files": ["/policies-and-practices/safety-and-health"]
        },
        {
                "event_name": "Addressing Global Issues",
                "date": NULL,
                "files": ["/policies-and-practices/addressing-global-issues"]
        },
        {
                "event_name": "Human Rights - Engaging Stakeholders",
                "date": NULL,
                "files": ["/policies-and-practices/human-rights-engaging-stakeholders"]
        },
        {
                "event_name": "California Transparency in Supply Chain Act",
                "date": NULL,
                "files": ["/policies-and-practices/california-transparency-in-supply-chain-act"]
        },
        {
                "event_name": "SGP Guidance Documents",
                "date": NULL,
                "files": ["/policies-and-practices/sgp-guidance-documents"]
        },
        {
                "event_name": "SGP Guidance Documents - Languages",
                "date": NULL,
                "files": ["/policies-and-practices/sgp-implementation-guide-languages"]
        },
        {
                "event_name": "Human Rights Self Assessment",
                "date": NULL,
                "files": ["/policies-and-practices/human-rights-self-assessment-checklists"]
        },
        {
                "event_name": "Human Rights Restructuring Guidelines",
                "date": NULL,
                "files": ["/content/dam/company/us/en/policies/pdf/human-workplace-rights/human-rights-restructuring-guidelines/human-rights-restructuring-guidelines-2020-framework.pdf"]
        },
        {
                "event_name": "Corporate Governance Guidelines",
                "date": 2023,
                "files": ["https://d1io3yog0oux5.cloudfront.net/_fd6a3e721c8feb0db6fa2e45899401ee/cocacolacompany/db/719/7231/file/Corporate+Governance+Guidelines+as+of+October+19%2C+2023.pdf"]
        },
        {
                "event_name": "Code of Business Conduct (English PDF)",
                "date": NULL,
                "files": ["/content/dam/company/us/en/policies/pdf/corporate-governance/code-of-business-conduct/coca-cola-coc-external.pdf"]
        },
        {
                "event_name": "Certificate of Incorporation",
                "date": NULL,
                "files": ["https://d1io3yog0oux5.cloudfront.net/_fd6a3e721c8feb0db6fa2e45899401ee/cocacolacompany/db/719/7229/file/Binder1.pdf"]
        },
        {
                "event_name": "Company Bylaws",
                "date": 2023,
                "files": ["https://d1io3yog0oux5.cloudfront.net/_fd6a3e721c8feb0db6fa2e45899401ee/cocacolacompany/db/719/7230/file/2023-10-19+Amended+and+Restated+Bylaws+as+of+October+19%2C+2023+%28FINAL%29.pdf"]
        },
        {
                "event_name": "Code of Business Conduct for Non Employee Directors (English)",
                "date": NULL,
                "files": ["/content/dam/company/us/en/policies/pdf/corporate-governance/code-of-business-conduct/directors-code-2018.pdf"]
        },
        {
                "event_name": "Code of Business Conduct (Other Languages)",
                "date": NULL,
                "files": ["/policies-and-practices/supplier-code-of-business-conduct-languages"]
        },
        {
                "event_name": "2023 Giving Back Update",
                "date": 2023,
                "files": ["/content/dam/company/us/en/reports/2023-data-updates/2023-giving-back-update.pdf"]
        },
        {
                "event_name": "2023 The Coca-Cola Foundation Form 990-PF Return",
                "date": 2023,
                "files": ["content/dam/company/us/en/reports/pdf/2023-TCCF-Tax-Return-Form-990.pdf"]
        },
        {
                "event_name": "2021 The Coca-Cola Foundation Form 990-PF Return",
                "date": 2021,
                "files": ["/content/dam/company/us/en/policies/pdf/the-coca-cola-foundation/the-coca-cola%20foundation-inc-%202021-tax-return-copy-for-public-inspection.pdf"]
        },
        {
                "event_name": "2020 Coca-Cola Foundation Form 990 PF Return",
                "date": 2020,
                "files": ["/content/dam/company/us/en/policies/pdf/the-coca-cola-foundation/2020-CCF-Form-990-PF.pdf"]
        },
        {
                "event_name": "2019 Charitable Contributions Report",
                "date": 2019,
                "files": ["/content/dam/company/us/en/policies/pdf/the-coca-cola-foundation/The-Coca-Cola-Foundation-Charitable-Giving-List-2019.pdf"]
        },
        {
                "event_name": "2018 Charitable Contributions Report",
                "date": 2018,
                "files": ["/content/dam/company/us/en/policies/pdf/the-coca-cola-foundation/2018-charitable-contributions-report-amended.pdf"]
        },
        {
                "event_name": "Application Form for Grants",
                "date": NULL,
                "files": ["https://coca-cola.smartsimple.com/s_Login.jsp"]
        },
        {
                "event_name": "Become a Supplier",
                "date": NULL,
                "files": ["https://tccc.starssmp.com/"]
        },
        {
                "event_name": "Supplier Requirements",
                "date": NULL,
                "files": ["/policies-and-practices/supplier-requirements"]
        },
        {
                "event_name": "Principles for Sustainable Agriculture Supplier Guide",
                "date": NULL,
                "files": ["/content/dam/company/us/en/policies/pdf/supplier-requirements/principles-for-sustainable-agriculture-supplier-guide.pdf"]
        },
        {
                "event_name": "Patent License Terms for Suppliers",
                "date": NULL,
                "files": ["/policies-and-practices/patent-license-for-suppliers"]
        },
        {
                "event_name": "Artwork, Labeling & Intellectual Property",
                "date": NULL,
                "files": ["/content/dam/company/us/en/policies/pdf/legal-and-practices/artwork-labeling-and-intellectual-property.pdf"]
        },
        {
                "event_name": "General Supplier Requirements [KORE]",
                "date": NULL,
                "files": ["/content/dam/company/us/en/policies/pdf/legal-and-practices/KORE-General-Supplier-Requirements-General.pdf"]
        },
        {
                "event_name": "Ingredient Supplier Requirements [KORE]",
                "date": NULL,
                "files": ["/content/dam/company/us/en/policies/pdf/legal-and-practices/kore-ingredient-supplier-requirements.pdf"]
        },
        {
                "event_name": "Ingredient – Pre-Pack – Supplier Requirements [KORE]",
                "date": NULL,
                "files": ["/content/dam/company/us/en/policies/pdf/legal-and-practices/KORE-Ingredient-Supplier-Requirements-Pre-Pack.pdf"]
        },
        {
                "event_name": "Ingredient – Food Allergen Sensitivity - Supplier Requirements [KORE]",
                "date": NULL,
                "files": ["/content/dam/company/us/en/policies/pdf/legal-and-practices/KORE-Ingredient-Supplier-Requirements-Food-Allergen-and-Sensitivity-Control.pdf"]
        },
        {
                "event_name": "Global Purchase Order Terms and Conditions",
                "date": NULL,
                "files": ["/policies-and-practices/global-purchase-order-terms-and-conditions"]
        },
        {
                "event_name": "Global Food Allergen and Sensitivity Template",
                "date": NULL,
                "files": ["/content/dam/company/us/en/policies/pdf/legal-and-practices/global-food-allergen-and-sensitivity-template.pdf"]
        },
        {
                "event_name": "Supplier Invoicing Guide",
                "date": 2024,
                "files": ["/content/dam/company/us/en/policies/pdf/supplier-requirements/The%20Coca-Cola%20Company%20Supplier%20Invoicing%20Guide_version%20Nov.%202024.pdf"]
        }
]'''
print(json.loads(strin.replace(' ', '')))