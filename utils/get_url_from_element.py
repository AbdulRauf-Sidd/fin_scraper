import re
from typing import List, Optional
from bs4 import BeautifulSoup
from urllib.parse import urljoin

def get_urls_from_element(html_snippet: str, base_url: Optional[str] = None) -> List[str]:
    """
    Extracts all URLs from a given HTML snippet and optionally resolves relative URLs.
    Also attempts to parse URLs hidden inside a "javascript:void(window.open('...'))" call.

    :param html_snippet: A string containing HTML code (one snippet).
    :param base_url: (Optional) If provided, relative links will be transformed into absolute URLs
                     using this as the base.
    :return: A list of URLs (strings) extracted from all 'href' attributes in <a> tags.
    """
    soup = BeautifulSoup(html_snippet, 'html.parser')
    links = []

    # Regex to capture the URL within javascript:void(window.open('URL','WindowName',...));
    # Group 1 captures the actual URL inside the quotes.
    js_void_pattern = re.compile(r"^javascript:void\(window\.open\('([^']+)'.*\)\s*;?$", re.IGNORECASE)

    for a_tag in soup.find_all('a', href=True):
        href_value = a_tag['href'].strip()

        # 1) Check if href_value matches the "javascript:void(window.open('...'))" pattern
        js_match = js_void_pattern.match(href_value)
        if js_match:
            # Extract the real URL from inside window.open(...)
            extracted_url = js_match.group(1)

            # If base_url is provided, resolve relative
            if base_url:
                resolved_url = urljoin(base_url, extracted_url)
            else:
                resolved_url = extracted_url

            links.append(resolved_url)

        else:
            # 2) If not a javascript link, treat it like a normal href
            if base_url:
                resolved_url = urljoin(base_url, href_value)
            else:
                resolved_url = href_value
            
            links.append(resolved_url)

    return links



html_example = [
    "<!----><div class=\"list__content\"><h3> Q4 2024 PVH Corp. Earnings Conference Call </h3><!----><!----><p class=\"list__date\"> Apr 01, 2025 9am EDT / 6am PDT </p></div>",
    "<!----><div class=\"list__content\"><h3> Q3 2024 PVH Corp. Earnings Conference Call </h3><!----><p class=\"list__description list__webcast_link\"><a href=\"javascript:void(window.open('https://edge.media-server.com/mmc/p/zti77hw7','Window1','menubar=no,statusbar=no, width=800,height=600,toolbar=no,scrollbars=yes'));\">View Webcast</a></p><p class=\"list__date\"> Dec 05, 2024 9am EST / 6am PST </p></div>",
    "<!----><div class=\"list__content\"><h3> Goldman Sachs  Global Retailing Conference </h3><!----><p class=\"list__description list__webcast_link\"><a href=\"javascript:void(window.open('https://event.webcasts.com/starthere.jsp?ei=1685908&amp;tp_key=b9e65c5ffc&amp;tp_special=8','Window1','menubar=no,statusbar=no, width=800,height=600,toolbar=no,scrollbars=yes'));\">View Webcast</a></p><p class=\"list__date\"> Sep 05, 2024 10:20am EDT / 7:20am PDT </p></div>",
    "<!----><div class=\"list__content\"><h3> Q2 2024 PVH Corp. Earnings Conference Call </h3><!----><p class=\"list__description list__webcast_link\"><a href=\"javascript:void(window.open('https://edge.media-server.com/mmc/p/9tb7eys4','Window1','menubar=no,statusbar=no, width=800,height=600,toolbar=no,scrollbars=yes'));\">View Webcast</a></p><p class=\"list__date\"> Aug 28, 2024 9am EDT / 6am PDT </p></div>",
    "<!----><div class=\"list__content\"><h3> Q1 2024 PVH Corp. Earnings Conference Call </h3><!----><p class=\"list__description list__webcast_link\"><a href=\"javascript:void(window.open('https://edge.media-server.com/mmc/p/cjdfwpfm','Window1','menubar=no,statusbar=no, width=800,height=600,toolbar=no,scrollbars=yes'));\">View Webcast</a></p><p class=\"list__date\"> Jun 05, 2024 9am EDT / 6am PDT </p></div>",
    "<!----><div class=\"list__content\"><h3> Q4 2023 PVH Corp. Earnings Conference Call </h3><!----><p class=\"list__description list__webcast_link\"><a href=\"javascript:void(window.open('https://edge.media-server.com/mmc/p/cbo8m2h6','Window1','menubar=no,statusbar=no, width=800,height=600,toolbar=no,scrollbars=yes'));\">View Webcast</a></p><p class=\"list__date\"> Apr 02, 2024 9am EDT / 6am PDT </p></div>",
    "<a href=\"/investor-relations\" class=\"tile__category router-link-active\">Investors </a><!----><!----><!----><ul class=\"tile__links\"><li><a href=\"/investor-relations/financials\" class=\"\">Financials</a></li><li><a href=\"/investor-relations/sec-filings\" class=\"\">SEC Filings</a></li><li><a href=\"/investor-relations/governance\" class=\"\">Governance</a></li><li><a href=\"/-/media/Files/pvh/investor-relations/Investor-Day-2022-Presentation.pdf\" target=\"_blank\">Investor Day 2022 Presentation</a></li></ul>",
    "<a href=\"/-/media/Files/pvh/investor-relations/PVH-Year-in-Review-2023.pdf\" target=\"_blank\" class=\"tile__category tile--mainLink\">2023 Year in Review </a><!----><!----><!----><!---->",
    "<a href=\"/-/media/Files/pvh/investor-relations/PVH-Q3-2024-Earnings.pdf\" target=\"\" class=\"tile__category tile--mainLink\">2024 3Q Earnings</a><!----><!----><!----><!---->",
    "<a href=\"/-/media/Files/pvh/investor-relations/PVH-Q2-2024-Earnings.pdf\" target=\"_blank\" class=\"tile__category tile--mainLink\">2024 2Q Earnings</a><!----><!----><!----><!---->",
    "<!----><!----><h2 class=\"tile__title tile__title--\"><a href=\"/responsibility\" class=\"tile--mainLink\">Responsibility</a></h2><!----><!---->",
    "<!----><!----><h2 class=\"tile__title tile__title--\"><a href=\"/company/leadership\" class=\"tile--mainLink\">Leadership</a></h2><!----><!---->",
    "<!----><!----><h2 class=\"tile__title tile__title--\"><a href=\"/news\" class=\"tile--mainLink\">News</a></h2><!----><!---->"
    "<a href=\"/company\" class=\"\">Company</a><!----><div class=\"subnav\"><ul style=\"top: -238px;\"><li><a href=\"/company/leadership\" class=\"\" tabindex=\"-1\">Leadership</a></li><li><a href=\"/company/we-are-pvh\" class=\"\" tabindex=\"-1\">We Are PVH</a></li><li><a href=\"/company/inclusion-diversity\" class=\"\" tabindex=\"-1\">Inclusion &amp; Diversity</a></li><li><a href=\"/company/pvh-foundation\" class=\"\" tabindex=\"-1\">The PVH Foundation</a></li><li><a href=\"/company/archives\" class=\"\" tabindex=\"-1\">Archives</a></li></ul></div>",
    "<a href=\"/company/leadership\" class=\"\" tabindex=\"-1\">Leadership</a>",
    "<a href=\"/company/we-are-pvh\" class=\"\" tabindex=\"-1\">We Are PVH</a>",
    "<a href=\"/company/inclusion-diversity\" class=\"\" tabindex=\"-1\">Inclusion &amp; Diversity</a>",
    "<a href=\"/company/pvh-foundation\" class=\"\" tabindex=\"-1\">The PVH Foundation</a>",
    "<a href=\"/company/archives\" class=\"\" tabindex=\"-1\">Archives</a>",
    "<a href=\"/brands\" class=\"\">Brands</a><!----><div class=\"subnav\"><ul style=\"top: -130px;\"><li><a href=\"/brands/calvin-klein\" class=\"\" tabindex=\"-1\">Calvin Klein</a></li><li><a href=\"/brands/tommy-hilfiger\" class=\"\" tabindex=\"-1\">Tommy Hilfiger</a></li></ul></div>",
    "<a href=\"/brands/calvin-klein\" class=\"\" tabindex=\"-1\">Calvin Klein</a>",
    "<a href=\"/brands/tommy-hilfiger\" class=\"\" tabindex=\"-1\">Tommy Hilfiger</a>",
    "<a href=\"/responsibility\" class=\"\">Responsibility</a><!----><div class=\"subnav\"><ul style=\"top: -238px;\"><li><a href=\"/responsibility/climate\" class=\"\" tabindex=\"-1\">Climate</a></li><li><a href=\"/responsibility/human-rights\" class=\"\" tabindex=\"-1\">Human Rights</a></li><li><a href=\"/responsibility/inclusion-diversity\" class=\"\" tabindex=\"-1\">Inclusion &amp; Diversity</a></li><li><a href=\"/responsibility/resources\" class=\"\" tabindex=\"-1\">Resources</a></li><li><a href=\"https://www.pvh.com/-/media/Files/pvh/responsibility/PVH-CR-Report-2023.pdf\" target=\"_blank\" tabindex=\"-1\">2023 CR Report</a></li></ul></div>",
    "<a href=\"/responsibility/climate\" class=\"\" tabindex=\"-1\">Climate</a>",
    "<a href=\"/responsibility/human-rights\" class=\"\" tabindex=\"-1\">Human Rights</a>",
    "<a href=\"/responsibility/inclusion-diversity\" class=\"\" tabindex=\"-1\">Inclusion &amp; Diversity</a>",
    "<a href=\"/responsibility/resources\" class=\"\" tabindex=\"-1\">Resources</a>",
    "<a href=\"https://www.pvh.com/-/media/Files/pvh/responsibility/PVH-CR-Report-2023.pdf\" target=\"_blank\" tabindex=\"-1\">2023 CR Report</a>",
    "<a href=\"/investor-relations\" class=\"router-link-active\">Investors</a><!----><div class=\"subnav\"><ul style=\"top: -310px;\"><li><a href=\"/news?facets=content_type%3DEvents&amp;nofilter=true\" class=\"\" tabindex=\"-1\">Events</a></li><li><a href=\"/investor-relations/reports\" class=\"\" tabindex=\"-1\">Reports</a></li><li><a href=\"/investor-relations/sec-filings\" class=\"\" tabindex=\"-1\">SEC Filings</a></li><li><a href=\"/investor-relations/financials\" class=\"\" tabindex=\"-1\">Financials</a></li><li><a href=\"/investor-relations/stock-price\" class=\"\" tabindex=\"-1\">Stock Price</a></li><li><a href=\"/investor-relations/governance\" class=\"\" tabindex=\"-1\">Governance</a></li><li><a href=\"/investor-relations/sustainable-finance\" class=\"router-link-exact-active router-link-active\" tabindex=\"-1\">Sustainable Finance</a></li></ul></div>",
    "<a href=\"/news?facets=content_type%3DEvents&amp;nofilter=true\" class=\"\" tabindex=\"-1\">Events</a>",
    "<a href=\"/investor-relations/reports\" class=\"\" tabindex=\"-1\">Reports</a>",
    "<a href=\"/investor-relations/sec-filings\" class=\"\" tabindex=\"-1\">SEC Filings</a>",
    "<a href=\"/investor-relations/financials\" class=\"\" tabindex=\"-1\">Financials</a>",
    "<a href=\"/investor-relations/stock-price\" class=\"\" tabindex=\"-1\">Stock Price</a>",
    "<a href=\"/investor-relations/governance\" class=\"\" tabindex=\"-1\">Governance</a>",
    "<a href=\"/investor-relations/sustainable-finance\" class=\"router-link-exact-active router-link-active\" tabindex=\"-1\">Sustainable Finance</a>",
    "<a href=\"https://careers.pvh.com/global/en?utm_source=pvh&amp;utm_medium=navigation_header&amp;utm_campaign=careers\" target=\"_blank\">Careers</a><!----><div class=\"subnav\"><ul style=\"top: -166px;\"><li><a href=\"https://careers.pvh.com/global/en/search-results?utm_source=pvh&amp;utm_medium=navigation_header&amp;utm_campaign=careers_search\" target=\"_blank\" tabindex=\"-1\">Search All Jobs</a></li><li><a href=\"https://careers.pvh.com/global/en/why-work-with-us?utm_source=pvh&amp;utm_medium=navigation_header&amp;utm_campaign=why_work_with_us\" target=\"_blank\" tabindex=\"-1\">Why Work With Us</a></li><li><a href=\"https://careers.pvh.com/global/en/our-benefits?utm_source=pvh&amp;utm_medium=navigation_header&amp;utm_campaign=our_benefits\" target=\"_blank\" tabindex=\"-1\">Our Benefits</a></li></ul></div>",
    "<a href=\"https://careers.pvh.com/global/en/search-results?utm_source=pvh&amp;utm_medium=navigation_header&amp;utm_campaign=careers_search\" target=\"_blank\" tabindex=\"-1\">Search All Jobs</a>",
    "<a href=\"https://careers.pvh.com/global/en/why-work-with-us?utm_source=pvh&amp;utm_medium=navigation_header&amp;utm_campaign=why_work_with_us\" target=\"_blank\" tabindex=\"-1\">Why Work With Us</a>",
    "<a href=\"https://careers.pvh.com/global/en/our-benefits?utm_source=pvh&amp;utm_medium=navigation_header&amp;utm_campaign=our_benefits\" target=\"_blank\" tabindex=\"-1\">Our Benefits</a>",
    "<a href=\"/news\" class=\"\">News</a><!----><div class=\"subnav\"><ul style=\"top: -166px;\"><li><a href=\"/news?facets=content_type=Stories\" class=\"\" tabindex=\"-1\">Stories</a></li><li><a href=\"/news?facets=content_type=Press%20Releases\" class=\"\" tabindex=\"-1\">Press Releases</a></li><li><a href=\"https://www.pvh.com/-/media/Files/pvh/news/media-kit/PVH-Media-Kit.pdf\" target=\"_blank\" tabindex=\"-1\">Media Kit</a></li></ul></div>",
    "<a href=\"/news?facets=content_type=Stories\" class=\"\" tabindex=\"-1\">Stories</a>",
    "<a href=\"/news?facets=content_type=Press%20Releases\" class=\"\" tabindex=\"-1\">Press Releases</a>",
    "<a href=\"https://www.pvh.com/-/media/Files/pvh/news/media-kit/PVH-Media-Kit.pdf\" target=\"_blank\" tabindex=\"-1\">Media Kit</a>",
    "<a href=\"/-/media/Files/pvh/investor-relations/sustainable-finance/PVH-Green-Financing-Framework.pdf\" target=\"_blank\">PVH Green Financing Framework</a>",
    "<a href=\"/-/media/Files/pvh/investor-relations/sustainable-finance/PVH-Green-Financing-Framework-SecondParty-Opinion-sustainalyticscom.pdf\" target=\"_blank\">PVH Green Financing Framework Second-Party Opinion (sustainalytics.com)</a>",
    "<a href=\"/company/leadership\" class=\"\">Leadership</a>",
    "<a href=\"/company/we-are-pvh\" class=\"\">We Are PVH</a>",
    "<a href=\"/company/inclusion-diversity\" class=\"\">Inclusion &amp; Diversity</a>",
    "<a href=\"/company/pvh-foundation\" class=\"\">The PVH Foundation</a>",
    "<a href=\"/company/archives\" class=\"\">Archives</a>",
    "<a href=\"/brands/calvin-klein\" class=\"\">Calvin Klein</a>",
    "<a href=\"/brands/tommy-hilfiger\" class=\"\">Tommy Hilfiger</a>",
    "<a href=\"/responsibility/climate\" class=\"\">Climate</a>",
    "<a href=\"/responsibility/human-rights\" class=\"\">Human Rights</a>",
    "<a href=\"/responsibility/inclusion-diversity\" class=\"\">Inclusion &amp; Diversity</a>",
    "<a href=\"/responsibility/resources\" class=\"\">Resources</a>",
    "<a href=\"/-/media/Files/pvh/responsibility/PVH-CR-Report-2023.pdf\" target=\"_blank\">2023 CR Report</a>",
    "<a href=\"/news?facets=content_type%3DEvents&amp;nofilter=true\" class=\"\">Events</a>",
    "<a href=\"/investor-relations/reports\" class=\"\">Reports</a>",
    "<a href=\"/investor-relations/sec-filings\" class=\"\">SEC Filings</a>",
    "<a href=\"/investor-relations/financials\" class=\"\">Financials</a>",
    "<a href=\"/investor-relations/stock-price\" class=\"\">Stock Price</a>",
    "<a href=\"/investor-relations/governance\" class=\"\">Governance</a>",
    "<a href=\"/investor-relations/sustainable-finance\" class=\"router-link-exact-active router-link-active\">Sustainable Finance</a>",
    "<a href=\"https://careers.pvh.com/global/en/search-results?utm_source=pvh&amp;utm_medium=navigation_footer&amp;utm_campaign=careers_search\" target=\"_blank\">Search All Jobs</a>",
    "<a href=\"https://careers.pvh.com/global/en/why-work-with-us?utm_source=pvh&amp;utm_medium=navigation_footer&amp;utm_campaign=why_work_with_us\" target=\"_blank\">Why Work With Us</a>",
    "<a href=\"https://careers.pvh.com/global/en/our-benefits?utm_source=pvh&amp;utm_medium=navigation_footer&amp;utm_campaign=our_benefits\" target=\"_blank\">Our Benefits</a>",
    "<a href=\"/news?facets=content_type=Stories\" class=\"\">Stories</a>",
    "<a href=\"/news?facets=content_type=Press%20Releases\" class=\"\">Press Releases</a>",
    "<a href=\"/-/media/Files/pvh/news/media-kit/PVH-Media-Kit.pdf\" target=\"_blank\">Media Kit</a>",
    "<a href=\"https://www.facebook.com/PVH.Corp\" target=\"_blank\" rel=\"noopener noreferrer\" class=\"social-link\"><svg><use xlink:href=\"/dist/pvh-jss/img/icons.svg#facebook\"></use></svg></a>",
    "<a href=\"https://www.instagram.com/pvhcorp\" target=\"_blank\" rel=\"noopener noreferrer\" class=\"social-link\"><svg><use xlink:href=\"/dist/pvh-jss/img/icons.svg#instagram\"></use></svg></a>",
    "<a href=\"https://www.linkedin.com/company/pvh\" target=\"_blank\" rel=\"noopener noreferrer\" class=\"social-link\"><svg><use xlink:href=\"/dist/pvh-jss/img/icons.svg#linkedin\"></use></svg></a>",
    "<a href=\"https://twitter.com/pvhcorp\" target=\"_blank\" rel=\"noopener noreferrer\" class=\"social-link\"><svg><use xlink:href=\"/dist/pvh-jss/img/icons.svg#twitter\"></use></svg></a>",
    "<a href=\"https://www.youtube.com/channel/UCzTz3j0znFVFO-EM5Sd4Wmw\" target=\"_blank\" rel=\"noopener noreferrer\" class=\"social-link\"><svg><use xlink:href=\"/dist/pvh-jss/img/icons.svg#youtube\"></use></svg></a>",
    "<a href=\"/privacy-policy\" class=\"\">Privacy</a>",
    "<a href=\"/legal\" class=\"\">Legal</a>",
    "<a href=\"/-/media/Files/pvh/footer/PVH-Gender-Pay-Gap-Report.pdf\" target=\"_blank\">UK Gender Pay Gap Report</a>",
    "<a href=\"/canada-california-uk-australia-supply-chain-disclosure\" class=\"\">PVH Corp. Joint Modern Slavery Act Statement</a>",
    "<a href=\"/french-pay-gap-reporting\" class=\"\">French Pay Gap Report</a>",
    "<a href=\"/-/media/Files/pvh/footer/Ireland-Gender-Pay-Gap-Report.pdf\" target=\"_blank\">Ireland Gender Pay Gap Report</a>"
]
for x in html_example:
    found_links = get_urls_from_element(x,"https://www.BASEURLTEST.com/")
    print(found_links)