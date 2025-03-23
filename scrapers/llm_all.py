import os
from mistralai import Mistral
import json


def llm_all(html):

    api_key = os.getenv('API_KEY')
    model = "mistral-large-latest"

    client = Mistral(api_key='eMbFOheAKGHjaEE7thfEr9nkGFWvlbwi')

    chat_response = client.chat.complete(
        model= model,
        messages = [
            {
                "role": "system",
                "content": '''You are a extraction system that can provide event names, dates, and the associated files from a raw html content into a json object. You will only respond with a list of JSON objects (ONLY. DON'T INCLUDE ANYTHING ELSE THAT WILL TROUBLE ME CONVERTING THE STRING TO JSON, INCLUDING HE JSON HEADING AT THE TOP) with the event name, date, and files (this will be a list of files where applicalble). where date is not available, use NULL as a place holder. 
                Where 'files' is empty list or event name is empty, DON'T INCLUDE IT IN THE EVENT LIST.
                            here is an example:

                            HTML:
<div class="main-content " bis_skin_checked="1">
                             
		
		<div class="year-filter" bis_skin_checked="1">
		<form class="redirect-select">
    		<div class="row" bis_skin_checked="1">
        		<div class="col-xs-12 col-sm-12 col-md-12" bis_skin_checked="1">
        		    <label class="sr-only" for="year">Year</label>
            		 <select class="selectpicker bs-select-hidden" id="year" data-style="main-select" name="year">
                 	 <option selected="" value="-1">All Years</option>
            		             		             				    <option>2025</option>
                                                                    		             		             				    <option>2024</option>
                                                                    		             		             				    <option>2023</option>
                                                                    		             		             				    <option>2022</option>
                                                                    		             		             				    <option>2021</option>
                                                                    		             		             				    <option>2020</option>
                                                                    		             		             				    <option>2019</option>
                                                                    		             		             				    <option>2018</option>
                                                                    		             		             				    <option>2017</option>
                                                                    		             		             				    <option>2016</option>
                                                                    		             		             				    <option>2015</option>
                                                                    		             		             				    <option>2014</option>
                                                                    		             		             				    <option>2013</option>
                                                                    		             		             				    <option>2012</option>
                                                                    		             		             				    <option>2011</option>
                                                                    		             		             				    <option>2010</option>
                                                                    		             		             				    <option>2009</option>
                                                                    		             		             				    <option>2008</option>
                                                                    		             		             				    <option>2007</option>
                                                                    		             		 </select><div class="btn-group bootstrap-select" bis_skin_checked="1"><button type="button" class="btn dropdown-toggle main-select" data-toggle="dropdown" data-id="year" title="All Years"><span class="filter-option pull-left">All Years</span>&nbsp;<span class="caret"></span></button><div class="dropdown-menu open" bis_skin_checked="1"><ul class="dropdown-menu inner" role="list"><li data-original-index="0" class="selected"><a tabindex="0" class="" style="" data-tokens="null"><span class="text">All Years</span><span class="DIN no-icon check-mark"></span></a></li><li data-original-index="1"><a tabindex="0" class="" style="" data-tokens="null"><span class="text">2025</span><span class="DIN no-icon check-mark"></span></a></li><li data-original-index="2"><a tabindex="0" class="" style="" data-tokens="null"><span class="text">2024</span><span class="DIN no-icon check-mark"></span></a></li><li data-original-index="3"><a tabindex="0" class="" style="" data-tokens="null"><span class="text">2023</span><span class="DIN no-icon check-mark"></span></a></li><li data-original-index="4"><a tabindex="0" class="" style="" data-tokens="null"><span class="text">2022</span><span class="DIN no-icon check-mark"></span></a></li><li data-original-index="5"><a tabindex="0" class="" style="" data-tokens="null"><span class="text">2021</span><span class="DIN no-icon check-mark"></span></a></li><li data-original-index="6"><a tabindex="0" class="" style="" data-tokens="null"><span class="text">2020</span><span class="DIN no-icon check-mark"></span></a></li><li data-original-index="7"><a tabindex="0" class="" style="" data-tokens="null"><span class="text">2019</span><span class="DIN no-icon check-mark"></span></a></li><li data-original-index="8"><a tabindex="0" class="" style="" data-tokens="null"><span class="text">2018</span><span class="DIN no-icon check-mark"></span></a></li><li data-original-index="9"><a tabindex="0" class="" style="" data-tokens="null"><span class="text">2017</span><span class="DIN no-icon check-mark"></span></a></li><li data-original-index="10"><a tabindex="0" class="" style="" data-tokens="null"><span class="text">2016</span><span class="DIN no-icon check-mark"></span></a></li><li data-original-index="11"><a tabindex="0" class="" style="" data-tokens="null"><span class="text">2015</span><span class="DIN no-icon check-mark"></span></a></li><li data-original-index="12"><a tabindex="0" class="" style="" data-tokens="null"><span class="text">2014</span><span class="DIN no-icon check-mark"></span></a></li><li data-original-index="13"><a tabindex="0" class="" style="" data-tokens="null"><span class="text">2013</span><span class="DIN no-icon check-mark"></span></a></li><li data-original-index="14"><a tabindex="0" class="" style="" data-tokens="null"><span class="text">2012</span><span class="DIN no-icon check-mark"></span></a></li><li data-original-index="15"><a tabindex="0" class="" style="" data-tokens="null"><span class="text">2011</span><span class="DIN no-icon check-mark"></span></a></li><li data-original-index="16"><a tabindex="0" class="" style="" data-tokens="null"><span class="text">2010</span><span class="DIN no-icon check-mark"></span></a></li><li data-original-index="17"><a tabindex="0" class="" style="" data-tokens="null"><span class="text">2009</span><span class="DIN no-icon check-mark"></span></a></li><li data-original-index="18"><a tabindex="0" class="" style="" data-tokens="null"><span class="text">2008</span><span class="DIN no-icon check-mark"></span></a></li><li data-original-index="19"><a tabindex="0" class="" style="" data-tokens="null"><span class="text">2007</span><span class="DIN no-icon check-mark"></span></a></li></ul></div></div>
            		 		             <label class="sr-only" for="category">Category</label>
            		 <select class="selectpicker bs-select-hidden" id="category" data-style="main-select" name="category">
            		                 		     <option value="all">All Releases</option>
            		                 		     <option value="financial">Financial Releases</option>
            		             		     </select><div class="btn-group bootstrap-select" bis_skin_checked="1"><button type="button" class="btn dropdown-toggle main-select" data-toggle="dropdown" data-id="category" title="All Releases"><span class="filter-option pull-left">All Releases</span>&nbsp;<span class="caret"></span></button><div class="dropdown-menu open" bis_skin_checked="1"><ul class="dropdown-menu inner" role="list"><li data-original-index="0" class="selected"><a tabindex="0" class="" style="" data-tokens="null"><span class="text">All Releases</span><span class="DIN no-icon check-mark"></span></a></li><li data-original-index="1"><a tabindex="0" class="" style="" data-tokens="null"><span class="text">Financial Releases</span><span class="DIN no-icon check-mark"></span></a></li></ul></div></div>
        		             		 </div><!--end col-->
    		 </div><!--end row-->
		</form>
		</div>
        
    

<article class="media">
    <div class="media-body" bis_skin_checked="1">
    
        <h2 class="media-heading">
            <a href="/news-events/press-releases/detail/1129/board-of-directors-of-the-coca-cola-company-approves-63rd">
                Board of Directors of The Coca-Cola Company Approves 63rd Consecutive Annual Dividend Increase            </a>
        </h2>
                <div class="date" bis_skin_checked="1"><time datetime="2025-02-20 13:00:00">Feb 20, 2025 1:00pm EST</time></div>
                
    </div>
</article>
<article class="media">
    <div class="media-body" bis_skin_checked="1">
    
        <h2 class="media-heading">
            <a href="/news-events/press-releases/detail/1128/coca-cola-reports-fourth-quarter-and-full-year-2024-results">
                Coca-Cola Reports Fourth Quarter and Full Year 2024 Results            </a>
        </h2>
                <div class="date" bis_skin_checked="1"><time datetime="2025-02-11 06:55:00">Feb 11, 2025 6:55am EST</time></div>
                
    </div>
</article>
<article class="media">
    <div class="media-body" bis_skin_checked="1">
    
        <h2 class="media-heading">
            <a href="/news-events/press-releases/detail/1127/the-coca-cola-company-announces-timing-of-fourth-quarter">
                The Coca-Cola Company Announces Timing of Fourth Quarter and Full Year 2024 Earnings Release            </a>
        </h2>
                <div class="date" bis_skin_checked="1"><time datetime="2025-01-14 10:00:00">Jan 14, 2025 10:00am EST</time></div>
                
    </div>
</article>
<article class="media">
    <div class="media-body" bis_skin_checked="1">
    
        <h2 class="media-heading">
            <a href="/news-events/press-releases/detail/1126/the-coca-cola-company-announces-retirement-of-director">
                The Coca-Cola Company Announces Retirement of Director            </a>
        </h2>
                <div class="date" bis_skin_checked="1"><time datetime="2024-12-16 06:55:00">Dec 16, 2024 6:55am EST</time></div>
                
    </div>
</article>
<article class="media">
    <div class="media-body" bis_skin_checked="1">
    
        <h2 class="media-heading">
            <a href="/news-events/press-releases/detail/1125/the-coca-cola-company-names-henrique-braun-executive-vice">
                The Coca-Cola Company Names Henrique Braun Executive Vice President and Chief Operating Officer            </a>
        </h2>
                <div class="date" bis_skin_checked="1"><time datetime="2024-12-11 16:15:00">Dec 11, 2024 4:15pm EST</time></div>
                
    </div>
</article>
<article class="media">
    <div class="media-body" bis_skin_checked="1">
    
        <h2 class="media-heading">
            <a href="/news-events/press-releases/detail/1124/the-coca-cola-company-evolves-voluntary-environmental-goals">
                The Coca-Cola Company Evolves Voluntary Environmental Goals            </a>
        </h2>
                <div class="date" bis_skin_checked="1"><time datetime="2024-12-02 16:07:00">Dec 02, 2024 4:07pm EST</time></div>
                
    </div>
</article>
<article class="media">
    <div class="media-body" bis_skin_checked="1">
    
        <h2 class="media-heading">
            <a href="/news-events/press-releases/detail/1123/the-coca-cola-company-announces-participation-in-morgan">
                The Coca-Cola Company Announces Participation in Morgan Stanley Global Consumer &amp; Retail Conference            </a>
        </h2>
                <div class="date" bis_skin_checked="1"><time datetime="2024-11-07 10:00:00">Nov 07, 2024 10:00am EST</time></div>
                
    </div>
</article>
<article class="media">
    <div class="media-body" bis_skin_checked="1">
    
        <h2 class="media-heading">
            <a href="/news-events/press-releases/detail/1122/the-coca-cola-company-announces-new-reporting-lines-for">
                The Coca-Cola Company Announces New Reporting Lines for Costa Coffee and innocent Businesses to Europe Operating Unit            </a>
        </h2>
                <div class="date" bis_skin_checked="1"><time datetime="2024-11-01 06:55:00">Nov 01, 2024 6:55am EDT</time></div>
                
    </div>
</article>
<article class="media">
    <div class="media-body" bis_skin_checked="1">
    
        <h2 class="media-heading">
            <a href="/news-events/press-releases/detail/1121/coca-cola-reports-third-quarter-2024-results-and-provides">
                Coca-Cola Reports Third Quarter 2024 Results and Provides Updated Guidance            </a>
        </h2>
                <div class="date" bis_skin_checked="1"><time datetime="2024-10-23 06:55:00">Oct 23, 2024 6:55am EDT</time></div>
                
    </div>
</article>
<article class="media">
    <div class="media-body" bis_skin_checked="1">
    
        <h2 class="media-heading">
            <a href="/news-events/press-releases/detail/1120/netflix-executive-bela-bajaria-elected-to-board-of">
                Netflix Executive Bela Bajaria Elected to Board of Directors of The Coca-Cola Company            </a>
        </h2>
                <div class="date" bis_skin_checked="1"><time datetime="2024-10-17 14:00:00">Oct 17, 2024 2:00pm EDT</time></div>
                
    </div>
</article>    	<div class="spr-ir-rss-icon rss-icon" bis_skin_checked="1">
    		<a href="https://investors.coca-colacompany.com/news-events/press-releases/rss" target="_blank">
    			<img src="https://d1io3yog0oux5.cloudfront.net/_2e64352bb48bdc5f4b77d6dc46c09d7e/cocacolacompany/files/theme/images/rssfeed.gif" alt="RSS">
    		</a>
    	</div>

			<div class="pagination-wrapper" bis_skin_checked="1">
            		<ul class="pagination">
			
            								<li class="pagination-link active"><a class="disabled">1</a></li>
												<li class="pagination-link"> <a href="https://investors.coca-colacompany.com/news-events/press-releases?page=2">2</a> </li>            
												<li class="pagination-link"> <a href="https://investors.coca-colacompany.com/news-events/press-releases?page=3">3</a> </li>            
												<li class="pagination-link"> <a href="https://investors.coca-colacompany.com/news-events/press-releases?page=4">4</a> </li>            
												<li class="pagination-link"> <a href="https://investors.coca-colacompany.com/news-events/press-releases?page=5">5</a> </li>            
												<li class="pagination-link"> <a href="https://investors.coca-colacompany.com/news-events/press-releases?page=6">6</a> </li>            
												<li class="pagination-link"> <a href="https://investors.coca-colacompany.com/news-events/press-releases?page=7">7</a> </li>            
												<li class="pagination-link"> <a href="https://investors.coca-colacompany.com/news-events/press-releases?page=8">8</a> </li>            
												<li class="pagination-link"> <a href="https://investors.coca-colacompany.com/news-events/press-releases?page=9">9</a> </li>            
												<li class="pagination-link"> <a href="https://investors.coca-colacompany.com/news-events/press-releases?page=10">10</a> </li>            
												<li class="pagination-link"> <a href="https://investors.coca-colacompany.com/news-events/press-releases?page=113">...113</a> </li>            
							            
		</ul>
					<div class="control next" bis_skin_checked="1"><a href="/news-events/press-releases?page=2"><span title="next" class="glyphicon glyphicon-menu-right"><span class="sr-only">Next</span></span></a></div>				    </div>
	    <div class="clear" bis_skin_checked="1"></div>
		                        </div>



Extraction:
[
	{
		event_name: Board of Directors of The Coca-Cola Company Approves 63rd Consecutive Annual Dividend Increase
		date: Feb 20, 2025
		url: [/news-events/press-releases/detail/1129/board-of-directors-of-the-coca-cola-company-approves-63rd]
		
	},
	{
		event_name: Coca-Cola Reports Fourth Quarter and Full Year 2024 Results
		date: Feb 11, 2025
		url: [/news-events/press-releases/detail/1128/coca-cola-reports-fourth-quarter-and-full-year-2024-results]
	},
	{
		event_name: The Coca-Cola Company Announces Timing of Fourth Quarter and Full Year 2024 Earnings Release
		date: Jan 14, 2025
		url: [/news-events/press-releases/detail/1127/the-coca-cola-company-announces-timing-of-fourth-quarter]
	},
	{
		event_name: The Coca-Cola Company Announces Retirement of Director
		date: Dec 16, 2024
		url: [/news-events/press-releases/detail/1126/the-coca-cola-company-announces-retirement-of-director]
	},
	{
		event_name: The Coca-Cola Company Names Henrique Braun Executive Vice President and Chief Operating Officer
		date: Dec 11, 2024
		url: [/news-events/press-releases/detail/1125/the-coca-cola-company-names-henrique-braun-executive-vice]
	},
	{
		event_name: The Coca-Cola Company Evolves Voluntary Environmental Goals
		date: Dec 02, 2024
		url: [/news-events/press-releases/detail/1124/the-coca-cola-company-evolves-voluntary-environmental-goals]
	},
	{
		event_name: The Coca-Cola Company Announces Participation in Morgan Stanley Global Consumer & Retail Conference
		date: Nov 07, 2024
		url: [/news-events/press-releases/detail/1123/the-coca-cola-company-announces-participation-in-morgan]
	},
	{
		event_name: The Coca-Cola Company Announces New Reporting Lines for Costa Coffee and innocent Businesses to Europe Operating Unit
		date: Nov 01, 2024
		url: [/news-events/press-releases/detail/1122/the-coca-cola-company-announces-new-reporting-lines-for]
	},
	{
		event_name: Coca-Cola Reports Third Quarter 2024 Results and Provides Updated Guidance
		date: Oct 23, 2024
		url: [/news-events/press-releases/detail/1121/coca-cola-reports-third-quarter-2024-results-and-provides]
	},
	{
		event_name: Netflix Executive Bela Bajaria Elected to Board of Directors of The Coca-Cola Company
		date: Oct 17, 2024
		url: [/news-events/press-releases/detail/1120/netflix-executive-bela-bajaria-elected-to-board-of]
	},
]'''
            },

            {
                "role": "user",
                "content": f'''{html}''',
            },
        ]
    )
    cleaned_text = chat_response.choices[0].message.content.replace('json', '')
    return json.loads(cleaned_text)


# a = llm_all('''<div class="content__main col-md-8 offset-md-0 order-md-1 col-12 order-2" bis_skin_checked="1"><!----><div class="list" bis_skin_checked="1"><ul><li class="list__item"><!----><div class="list__content" bis_skin_checked="1"><h3><a href="/news/press-releases/PVH-Corp-to-Host-Conference-Call-to-Discuss-Fourth-Quarter-and-YearEnd-2024-Earnings-Results">PVH Corp. to Host Conference Call to Discuss Fourth Quarter and Year-End 2024 Earnings Results</a></h3><p class="list__description">NEW YORK --(BUSINESS WIRE)--Mar. 17, 2025-- PVH Corp. (NYSE: PVH) today announced that it will release its fourth quarter and year-end 2024 earnings results on Monday, March 31, 2025 , after the market closes. PVH will sponsor a conference call on Tuesday, April 1, 2025 , beginning at 9:00 A.M.</p><!----><p class="list__date">Mar 17, 2025</p></div></li><li class="list__item"><!----><div class="list__content" bis_skin_checked="1"><h3><a href="/news/press-releases/23141-PVH-Corp-Declares-Quarterly-Cash-Dividend">PVH Corp. Declares Quarterly Cash Dividend</a></h3><p class="list__description">NEW YORK --(BUSINESS WIRE)--Feb. 5, 2025-- PVH Corp. [NYSE:PVH], announced the Executive Committee of the Board of Directors of PVH Corp. declared a quarterly cash dividend of $0.0375 per share payable on March 26, 2025 to stockholders of record on March 5, 2025 . About PVH Corp.</p><!----><p class="list__date">Feb 05, 2025</p></div></li><li class="list__item"><!----><div class="list__content" bis_skin_checked="1"><h3><a href="/news/press-releases/PVH-Corp-Reports-2024-Third-Quarter-Revenue-and-Earnings-Above-Guidance">PVH Corp. Reports 2024 Third Quarter Revenue and Earnings Above Guidance</a></h3><p class="list__description">Third quarter Revenue: Decreased 5% to $2.255 billion compared to the prior year period (decreased 6% on a constant currency basis), and exceeded guidance of a decrease of 6% to 7% (decrease of 7% to 8% on a constant currency basis) EPS: GAAP basis: $2.34 exceeded guidance of approximately $2.30</p><!----><p class="list__date">Dec 04, 2024</p></div></li><li class="list__item"><!----><div class="list__content" bis_skin_checked="1"><h3><a href="/news/press-releases/PVH-Corp-to-Host-Conference-Call-to-Discuss-Third-Quarter-2024-Earnings-Results">PVH Corp. to Host Conference Call to Discuss Third Quarter 2024 Earnings Results</a></h3><p class="list__description">NEW YORK --(BUSINESS WIRE)--Nov. 18, 2024-- PVH Corp. (NYSE: PVH) today announced that it will release its third quarter 2024 earnings results on Wednesday, December 4, 2024 , after the market closes. PVH will sponsor a conference call on Thursday, December 5, 2024 , beginning at 9:00 A.M.</p><!----><p class="list__date">Nov 18, 2024</p></div></li><li class="list__item"><!----><div class="list__content" bis_skin_checked="1"><h3><a href="/news/press-releases/PVH-Corp-Appoints-Jesper-Andersen-to-its-Board-of-Directors">PVH Corp. Appoints Jesper Andersen to its Board of Directors</a></h3><p class="list__description">NEW YORK --(BUSINESS WIRE)--Nov. 13, 2024-- PVH Corp. [NYSE: PVH] today announced the appointment of Jesper Andersen , Executive Vice President and Chief Financial Officer of the LEGO Group , to its Board of Directors, effective immediately. He has also been appointed to the Board’s Audit and Risk</p><!----><p class="list__date">Nov 13, 2024</p></div></li><li class="list__item"><!----><div class="list__content" bis_skin_checked="1"><h3><a href="/news/press-releases/23026-PVH-Corp-Declares-Quarterly-Cash-Dividend">PVH Corp. Declares Quarterly Cash Dividend</a></h3><p class="list__description">NEW YORK --(BUSINESS WIRE)--Oct. 30, 2024-- PVH Corp. [NYSE:PVH], announced the Executive Committee of the Board of Directors of PVH Corp. declared a quarterly cash dividend of $0.0375 per share payable on December 18, 2024 to stockholders of record on November 27, 2024 . About PVH Corp.</p><!----><p class="list__date">Oct 30, 2024</p></div></li><li class="list__item"><!----><div class="list__content" bis_skin_checked="1"><h3><a href="/news/press-releases/PVH-Corp-Names-CEO-of-PVH-EMEA">PVH Corp. Names CEO of PVH EMEA</a></h3><p class="list__description">Retail veteran Fredrik Olsson to build on the market-leading strength of Tommy Hilfiger and Calvin Klein and lead the next chapter of growth in the region NEW YORK --(BUSINESS WIRE)--Sep. 5, 2024-- PVH Corp. (NYSE:PVH) today announced the appointment of Fredrik Olsson as CEO of PVH EMEA.</p><!----><p class="list__date">Sep 05, 2024</p></div></li><li class="list__item"><!----><div class="list__content" bis_skin_checked="1"><h3><a href="/news/press-releases/PVH-Corp-to-Participate-in-the-Goldman-Sachs-31st-Annual-Global-Retailing-Conference-on-September-5">PVH Corp. to Participate in the Goldman Sachs 31st Annual Global Retailing Conference on September 5, 2024</a></h3><p class="list__description">NEW YORK --(BUSINESS WIRE)--Aug. 29, 2024-- PVH Corp. (NYSE: PVH) announced today that Stefan Larsson , Chief Executive Officer, and Zac Coughlin , Chief Financial Officer, will participate in a fireside chat at the Goldman Sachs 31st Annual Global Retailing Conference on Thursday, September 5,</p><!----><p class="list__date">Aug 29, 2024</p></div></li><li class="list__item"><!----><div class="list__content" bis_skin_checked="1"><h3><a href="/news/press-releases/PVH-Corp-Reports-2024-Second-Quarter-Earnings-Above-Guidance">PVH Corp. Reports 2024 Second Quarter Earnings Above Guidance</a></h3><p class="list__description">Second quarter Revenue: Decreased 6% to $2.074 billion compared to the prior year period (decreased 5% on a constant currency basis), in line with guidance of a decrease of 6% to 7% (decrease of 5% to 6% on a constant currency basis) EPS: GAAP basis: $2.80 exceeded guidance of approximately $2.25</p><!----><p class="list__date">Aug 27, 2024</p></div></li><li class="list__item"><!----><div class="list__content" bis_skin_checked="1"><h3><a href="/news/press-releases/PVH-Corp-to-Host-Conference-Call-to-Discuss-Second-Quarter-2024-Earnings-Results">PVH Corp. to Host Conference Call to Discuss Second Quarter 2024 Earnings Results</a></h3><p class="list__description">NEW YORK --(BUSINESS WIRE)--Aug. 12, 2024-- PVH Corp. (NYSE: PVH) today announced that it will release its second quarter 2024 earnings results on Tuesday, August 27, 2024 , after the market closes. PVH will sponsor a conference call on Wednesday, August 28, 2024 , beginning at 9:00 A.M.</p><!----><p class="list__date">Aug 12, 2024</p></div></li></ul></div><!----></div>''')
# print(a)
