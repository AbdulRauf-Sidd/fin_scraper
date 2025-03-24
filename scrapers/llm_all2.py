import os
from mistralai import Mistral
import json


def llm_all2(html):

    api_key = os.getenv('API_KEY')
    model = "mistral-large-latest"

    client = Mistral(api_key='eMbFOheAKGHjaEE7thfEr9nkGFWvlbwi')

    chat_response = client.chat.complete(
        model= model,
        messages = [
            {
                "role": "system",
                "content": '''You are a extraction system that can provide event names, dates, and the associated files from a raw html content into a json object. You will only respond with a list of JSON objects (ONLY. DON'T INCLUDE ANYTHING ELSE THAT WILL TROUBLE ME CONVERTING THE STRING TO JSON. EXCLUDE THE JSON HEADING AT THE TOP) with the event name, date, and files (this will be a list of files where applicalble). where date is not available, use NULL as a place holder. 
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
"Board of Directors of The Coca-Cola Company Approves 63rd Consecutive Annual Dividend Increase | Feb 20, 2025 | /news-events/press-releases/detail/1129/board-of-directors-of-the-coca-cola-company-approves-63rd \n
		
	},
	{
		"event_name": "Coca-Cola Reports Fourth Quarter and Full Year 2024 Results"
		"date": "Feb 11, 2025"
		"files": ["/news-events/press-releases/detail/1128/coca-cola-reports-fourth-quarter-and-full-year-2024-results"]
	},
	{
		"event_name": "The Coca-Cola Company Announces Timing of Fourth Quarter and Full Year 2024 Earnings Release"
		"date": "Jan 14, 2025"
		"files": ["/news-events/press-releases/detail/1127/the-coca-cola-company-announces-timing-of-fourth-quarter"]
	},
	{
		"event_name": "The Coca-Cola Company Announces Retirement of Director"
		"date": "Dec 16, 2024"
		"files": ["/news-events/press-releases/detail/1126/the-coca-cola-company-announces-retirement-of-director"]
	},
	{
		"event_name": "The Coca-Cola Company Names Henrique Braun Executive Vice President and Chief Operating Officer"
		"date": "Dec 11, 2024"
		"files": ["/news-events/press-releases/detail/1125/the-coca-cola-company-names-henrique-braun-executive-vice"]
	},
	{
		"event_name": "The Coca-Cola Company Evolves Voluntary Environmental Goals"
		"date": "Dec 02, 2024"
		"files": ["/news-events/press-releases/detail/1124/the-coca-cola-company-evolves-voluntary-environmental-goals"]
	},
	{
		event_name: "The Coca-Cola Company Announces Participation in Morgan Stanley Global Consumer & Retail Conference"
		date: "Nov 07, 2024"
		"files": ["/news-events/press-releases/detail/1123/the-coca-cola-company-announces-participation-in-morgan"]
	},
	{
		event_name: "The Coca-Cola Company Announces New Reporting Lines for Costa Coffee and innocent Businesses to Europe Operating Unit"
		date: "Nov 01, 2024"
		"files": ["/news-events/press-releases/detail/1122/the-coca-cola-company-announces-new-reporting-lines-for"]
	},
	{
		event_name: "Coca-Cola Reports Third Quarter 2024 Results and Provides Updated Guidance"
		date: "Oct 23, 2024"
		"files": ["/news-events/press-releases/detail/1121/coca-cola-reports-third-quarter-2024-results-and-provides"]
	},
	{
		event_name: "Netflix Executive Bela Bajaria Elected to Board of Directors of The Coca-Cola Company"
		date: "Oct 17, 2024"
		"files": ["/news-events/press-releases/detail/1120/netflix-executive-bela-bajaria-elected-to-board-of"]
	},
]


Here's another example. this one is a lot different so adjust accordingly:
HTML:
<div id="container-e4e0b86b80" class="cmp-container" bis_skin_checked="1">

        

        
        <div class="accordion panelcontainer faq" bis_skin_checked="1">
<div id="accordion-4151fd9fe7" class="cmp-accordion" data-cmp-data-layer="{&quot;accordion-4151fd9fe7&quot;:{&quot;shownItems&quot;:[&quot;accordion-4151fd9fe7-item-adefddf132&quot;,&quot;accordion-4151fd9fe7-item-7ea3f98ce4&quot;,&quot;accordion-4151fd9fe7-item-837d094e55&quot;,&quot;accordion-4151fd9fe7-item-db0a8c4be8&quot;],&quot;@type&quot;:&quot;cep/components/accordion&quot;,&quot;repo:modifyDate&quot;:&quot;2023-04-24T14:51:36Z&quot;}}" data-placeholder-text="false" bis_skin_checked="1">
    <div class="cmp-accordion__item" data-cmp-hook-accordion="item" data-cmp-data-layer="{&quot;accordion-4151fd9fe7-item-adefddf132&quot;:{&quot;@type&quot;:&quot;cep/components/accordion/item&quot;,&quot;dc:title&quot;:&quot;Company Overview&quot;}}" id="accordion-4151fd9fe7-item-adefddf132" data-cmp-expanded="" bis_skin_checked="1">
        <h3 class="cmp-accordion__header">
            <button id="accordion-4151fd9fe7-item-adefddf132-button" class="cmp-accordion__button cmp-accordion__button--expanded" type="button" aria-controls="accordion-4151fd9fe7-item-adefddf132-panel" data-cmp-hook-accordion="button" aria-expanded="true">
                <span class="cmp-accordion__title">Company Overview</span>
                <span class="cmp-accordion__icon"></span>
            </button>
        </h3>
        <div data-cmp-hook-accordion="panel" id="accordion-4151fd9fe7-item-adefddf132-panel" class="cmp-accordion__panel cmp-accordion__panel--expanded" role="region" aria-labelledby="accordion-4151fd9fe7-item-adefddf132-button" aria-hidden="false" bis_skin_checked="1"><div class="container responsivegrid" bis_skin_checked="1">

    
    <div id="container-adefddf132" class="cmp-container" bis_skin_checked="1">
        


<div class="aem-Grid aem-Grid--12 aem-Grid--default--12 " bis_skin_checked="1">
    
    <div class="text aem-GridColumn aem-GridColumn--default--12" bis_skin_checked="1">
<div data-cmp-data-layer="{&quot;text-e397727dc1&quot;:{&quot;@type&quot;:&quot;cep/components/text&quot;,&quot;repo:modifyDate&quot;:&quot;2025-01-14T19:01:07Z&quot;,&quot;xdm:text&quot;:&quot;<ul>\r\n<li><a href=\&quot;/content/company/us/en/about-us/purpose-and-vision.html\&quot;>Our Purpose and Vision</a></li>\r\n</ul>\r\n&quot;}}" id="text-e397727dc1" class="cmp-text" bis_skin_checked="1">
    <ul><li><a href="/about-us/purpose-and-vision">Our Purpose and Vision</a></li></ul>

</div>

    

</div>

    
</div>

    </div>

    
</div>
</div>
    </div>
<div class="cmp-accordion__item" data-cmp-hook-accordion="item" data-cmp-data-layer="{&quot;accordion-4151fd9fe7-item-7ea3f98ce4&quot;:{&quot;@type&quot;:&quot;cep/components/accordion/item&quot;,&quot;dc:title&quot;:&quot;Privacy &amp; Data Protection&quot;}}" id="accordion-4151fd9fe7-item-7ea3f98ce4" data-cmp-expanded="" bis_skin_checked="1">
        <h3 class="cmp-accordion__header">
            <button id="accordion-4151fd9fe7-item-7ea3f98ce4-button" class="cmp-accordion__button cmp-accordion__button--expanded" type="button" aria-controls="accordion-4151fd9fe7-item-7ea3f98ce4-panel" data-cmp-hook-accordion="button" aria-expanded="true">
                <span class="cmp-accordion__title">Privacy &amp; Data Protection</span>
                <span class="cmp-accordion__icon"></span>
            </button>
        </h3>
        <div data-cmp-hook-accordion="panel" id="accordion-4151fd9fe7-item-7ea3f98ce4-panel" class="cmp-accordion__panel cmp-accordion__panel--expanded" role="region" aria-labelledby="accordion-4151fd9fe7-item-7ea3f98ce4-button" aria-hidden="false" bis_skin_checked="1"><div class="container responsivegrid" bis_skin_checked="1">

    
    <div id="container-7ea3f98ce4" class="cmp-container" bis_skin_checked="1">
        


<div class="aem-Grid aem-Grid--12 aem-Grid--default--12 " bis_skin_checked="1">
    
    <div class="text aem-GridColumn aem-GridColumn--default--12" bis_skin_checked="1">
<div data-cmp-data-layer="{&quot;text-1480ee97d6&quot;:{&quot;@type&quot;:&quot;cep/components/text&quot;,&quot;repo:modifyDate&quot;:&quot;2024-09-13T20:04:03Z&quot;,&quot;xdm:text&quot;:&quot;<ul>\r\n<li><a href=\&quot;https://www.coca-cola.com/us/en/legal/privacy-policy\&quot;>Privacy Policy (U.S.)</a></li>\r\n<li><a href=\&quot;https://www.coca-cola.com/us/en/legal/cookies-policy\&quot;>Cookie Policy (U.S.)</a></li>\r\n<li><a href=\&quot;https://www.coca-cola.com/us/en/legal/terms-of-service\&quot;>Terms of Service (U.S.)</a></li>\r\n<li><a href=\&quot;/content/company/us/en/policies-and-practices/usage-rights-requests.html\&quot;>Usage Rights Requests (U.S.)</a></li>\r\n<li><a href=\&quot;/content/company/us/en/policies-and-practices/vulnerability-disclosure.html\&quot;>Vulnerability Disclosure Policy</a></li>\r\n</ul>\r\n&quot;}}" id="text-1480ee97d6" class="cmp-text" bis_skin_checked="1">
    <ul><li><a href="https://www.coca-cola.com/us/en/legal/privacy-policy">Privacy Policy (U.S.)</a></li><li><a href="https://www.coca-cola.com/us/en/legal/cookies-policy">Cookie Policy (U.S.)</a></li><li><a href="https://www.coca-cola.com/us/en/legal/terms-of-service">Terms of Service (U.S.)</a></li><li><a href="/policies-and-practices/usage-rights-requests">Usage Rights Requests (U.S.)</a></li><li><a href="/policies-and-practices/vulnerability-disclosure">Vulnerability Disclosure Policy</a></li></ul>

</div>

    

</div>

    
</div>

    </div>

    
</div>
</div>
    </div>
<div class="cmp-accordion__item" data-cmp-hook-accordion="item" data-cmp-data-layer="{&quot;accordion-4151fd9fe7-item-837d094e55&quot;:{&quot;@type&quot;:&quot;cep/components/accordion/item&quot;,&quot;repo:modifyDate&quot;:&quot;2023-03-30T14:38:51Z&quot;,&quot;dc:title&quot;:&quot;Research &amp; Studies&quot;}}" id="accordion-4151fd9fe7-item-837d094e55" data-cmp-expanded="" bis_skin_checked="1">
        <h3 class="cmp-accordion__header">
            <button id="accordion-4151fd9fe7-item-837d094e55-button" class="cmp-accordion__button cmp-accordion__button--expanded" type="button" aria-controls="accordion-4151fd9fe7-item-837d094e55-panel" data-cmp-hook-accordion="button" aria-expanded="true">
                <span class="cmp-accordion__title">Research &amp; Studies</span>
                <span class="cmp-accordion__icon"></span>
            </button>
        </h3>
        <div data-cmp-hook-accordion="panel" id="accordion-4151fd9fe7-item-837d094e55-panel" class="cmp-accordion__panel cmp-accordion__panel--expanded" role="region" aria-labelledby="accordion-4151fd9fe7-item-837d094e55-button" aria-hidden="false" bis_skin_checked="1"><div class="container responsivegrid" bis_skin_checked="1">

    
    
    
    
    <div id="container-837d094e55" class="cmp-container" bis_skin_checked="1">

        

        
        <div class="text" bis_skin_checked="1">
<div data-cmp-data-layer="{&quot;text-4e914879ae&quot;:{&quot;@type&quot;:&quot;cep/components/text&quot;,&quot;repo:modifyDate&quot;:&quot;2025-01-29T15:18:43Z&quot;,&quot;xdm:text&quot;:&quot;<ul>\r\n<li><a href=\&quot;/content/dam/company/us/en/policies/pdf/human-workplace-rights/addressing-global-issues/human-rights-in-the-coca-cola-sugar-supply-chain.pdf\&quot;>Overview of Country Sugar Study on Labor Practices</a></li>\r\n<li><a href=\&quot;/content/dam/company/us/en/reports/pdf/sugar-study-methodology-overview.pdf\&quot;>Sugar Study Methodology</a></li>\r\n<li><a href=\&quot;/content/company/us/en/policies-and-practices/country-sugar-studies.html\&quot;>Country Reports</a></li>\r\n<li><a href=\&quot;https://www.coca-colacompany.com/policies-and-practices/transparency\&quot;>Transparency in Partnerships</a></li>\r\n</ul>\r\n&quot;}}" id="text-4e914879ae" class="cmp-text" bis_skin_checked="1">
    <ul><li><a href="/content/dam/company/us/en/policies/pdf/human-workplace-rights/addressing-global-issues/human-rights-in-the-coca-cola-sugar-supply-chain.pdf">Overview of Country Sugar Study on Labor Practices</a></li><li><a href="/content/dam/company/us/en/reports/pdf/sugar-study-methodology-overview.pdf">Sugar Study Methodology</a></li><li><a href="/policies-and-practices/country-sugar-studies">Country Reports</a></li><li><a href="https://www.coca-colacompany.com/policies-and-practices/transparency">Transparency in Partnerships</a></li></ul>

</div>

    

</div>

        
    </div>

</div>
</div>
    </div>
<div class="cmp-accordion__item" data-cmp-hook-accordion="item" data-cmp-data-layer="{&quot;accordion-4151fd9fe7-item-db0a8c4be8&quot;:{&quot;@type&quot;:&quot;cep/components/accordion/item&quot;,&quot;repo:modifyDate&quot;:&quot;2023-04-20T08:23:00Z&quot;,&quot;dc:title&quot;:&quot;Employment&quot;}}" id="accordion-4151fd9fe7-item-db0a8c4be8" data-cmp-expanded="" bis_skin_checked="1">
        <h3 class="cmp-accordion__header">
            <button id="accordion-4151fd9fe7-item-db0a8c4be8-button" class="cmp-accordion__button cmp-accordion__button--expanded" type="button" aria-controls="accordion-4151fd9fe7-item-db0a8c4be8-panel" data-cmp-hook-accordion="button" aria-expanded="true">
                <span class="cmp-accordion__title">Employment</span>
                <span class="cmp-accordion__icon"></span>
            </button>
        </h3>
        <div data-cmp-hook-accordion="panel" id="accordion-4151fd9fe7-item-db0a8c4be8-panel" class="cmp-accordion__panel cmp-accordion__panel--expanded" role="region" aria-labelledby="accordion-4151fd9fe7-item-db0a8c4be8-button" aria-hidden="false" bis_skin_checked="1"><div class="container responsivegrid" bis_skin_checked="1">

    
    
    
    
    <div id="container-db0a8c4be8" class="cmp-container" bis_skin_checked="1">

        

        
        <div class="text" bis_skin_checked="1">
<div data-cmp-data-layer="{&quot;text-ddea1cb10c&quot;:{&quot;@type&quot;:&quot;cep/components/text&quot;,&quot;repo:modifyDate&quot;:&quot;2024-11-22T16:05:45Z&quot;,&quot;xdm:text&quot;:&quot;<ul>\r\n<li><a href=\&quot;/content/dam/company/us/en/reports/2023-data-updates/2023-workplace-representation-update.pdf\&quot;>2023 Workplace Representation Update</a></li>\r\n<li><a href=\&quot;/content/company/us/en/policies-and-practices/equal-employment-opportunity.html\&quot;>Equal Employment Opportunity</a></li>\r\n<li><a href=\&quot;/content/dam/company/us/en/policies/pdf/employment/coca-cola-applicant-privacy-notice-Oct2023.pdf\&quot;>Global&amp;nbsp;Applicant Privacy Notice&amp;nbsp;- English</a></li>\r\n<li><a href=\&quot;/content/company/us/en/policies-and-practices/global-applicant-privacy-notice-translated-by-country.html\&quot;>Global Applicant Privacy Notice - Translated by Country</a></li>\r\n<li><a href=\&quot;/content/company/us/en/policies-and-practices/equal-employment-opportunity-and-affirmative-action-2020-english.html\&quot;>Equal Employment Opportunity and Affirmative Action Policy</a></li>\r\n<li><a href=\&quot;/content/company/us/en/policies-and-practices/equal-employment-opportunity-and-affirmative-action-spanish.html\&quot;>Equal Employment Opportunity and Affirmative Action Policy - Spanish</a></li>\r\n<li><a href=\&quot;/content/dam/company/us/en/policies/pdf/employment/equal-employment-opportunity-law-poster-2009.pdf\&quot;>Equal Employment Opportunity is the Law (EEO)&amp;nbsp;</a></li>\r\n<li><a href=\&quot;/content/dam/company/us/en/policies/pdf/employment/equal-employment-opportunity-supplement-2009.pdf\&quot;>EEO is the Law Poster Supplement</a></li>\r\n<li><a href=\&quot;/content/dam/company/us/en/reports/pdf/uniformed-services-employment-and-reemployment-rights-act-2017.pdf\&quot;>USERRA Rights</a></li>\r\n<li><a href=\&quot;/content/dam/company/us/en/reports/pdf/employee-family-and-medical-leave-act-2016.pdf\&quot;>Family and Medical Leave Act (FMLA)</a></li>\r\n<li><a href=\&quot;/content/dam/company/us/en/policies/pdf/employment/employee-polygraph-protection-act-2016.pdf\&quot;>Employee Polygraph Protection Act (EPPA)</a></li>\r\n<li><a href=\&quot;/content/dam/company/us/en/policies/pdf/employment/e-verify-participation-poster-2017.pdf\&quot; target=\&quot;_blank\&quot; rel=\&quot;noopener noreferrer\&quot;>E-Verify (English and Spanish)</a></li>\r\n<li><a href=\&quot;/content/dam/company/us/en/reports/pdf/immigrant-and-employee-rights-right-to-work-poster-english-2019.pdf\&quot;>Right to Work (English)</a></li>\r\n<li><a href=\&quot;/content/dam/company/us/en/reports/pdf/pay-transparency-nondirscrimination-provision-english.pdf\&quot;>Pay Transparency Nondiscrimination Provision (English)</a></li>\r\n<li><a href=\&quot;/content/dam/company/us/en/policies/pdf/employment/immigrant-and-employee-rights-right-to-work-poster-spanish-2019.pdf\&quot;>Right to Work (Spanish)</a></li>\r\n<li><a href=\&quot;/content/dam/company/us/en/reports/pdf/pay-transparency-nondirscrimination-provision-spanish.pdf\&quot;>Pay Transparency Nondiscrimination Provision (Spanish)</a></li>\r\n<li><a href=\&quot;/content/company/us/en/policies-and-practices/recruitment-scams-fraudulent-activity.html\&quot;>Recruitment Scams &amp;amp; Fraudulent activity</a></li>\r\n<li><a href=\&quot;/content/dam/company/us/en/policies/pdf/employment/coca-cola-business-strategy-leadership-model-december-2020.pdf\&quot;>Business Strategy, Priorities &amp;amp; Leadership Model</a></li>\r\n<li><a href=\&quot;/content/company/us/en/policies-and-practices/equal-employment-opportunity-employer-reports.html\&quot;>Equal Employment Opportunity Employer Information Reports (EEO-1)</a></li>\r\n<li><a href=\&quot;https://health1.aetna.com/app/public/#/one/insurerCode=AETNACVS_I&amp;amp;brandCode=ALICSI/machine-readable-transparency-in-coverage?searchTerm=263764&amp;amp;lock=true\&quot;>Price Transparency Requirements for Healthcare Coverage</a></li>\r\n<li><a href=\&quot;https://mcs.com.pr/en/Pages/Transparency.aspx#\&quot;>Price Transparency Requirements for Healthcare Coverage (Puerto Rico)</a></li>\r\n<li><a href=\&quot;/content/company/us/en/policies-and-practices/accommodation-and-accessibility-request.html\&quot;>Accommodation and Accessibility Request</a></li>\r\n<li><a href=\&quot;/content/company/us/en/policies-and-practices/leadership-growth-insights-privacy-policy.html\&quot;>Leadership Growth Insights Privacy Policies</a></li>\r\n</ul>\r\n&quot;}}" id="text-ddea1cb10c" class="cmp-text" bis_skin_checked="1">
    <ul><li><a href="/content/dam/company/us/en/reports/2023-data-updates/2023-workplace-representation-update.pdf">2023 Workplace Representation Update</a></li><li><a href="/policies-and-practices/equal-employment-opportunity">Equal Employment Opportunity</a></li><li><a href="/content/dam/company/us/en/policies/pdf/employment/coca-cola-applicant-privacy-notice-Oct2023.pdf">Global&nbsp;Applicant Privacy Notice&nbsp;- English</a></li><li><a href="/policies-and-practices/global-applicant-privacy-notice-translated-by-country">Global Applicant Privacy Notice - Translated by Country</a></li><li><a href="/policies-and-practices/equal-employment-opportunity-and-affirmative-action-2020-english">Equal Employment Opportunity and Affirmative Action Policy</a></li><li><a href="/policies-and-practices/equal-employment-opportunity-and-affirmative-action-spanish">Equal Employment Opportunity and Affirmative Action Policy - Spanish</a></li><li><a href="/content/dam/company/us/en/policies/pdf/employment/equal-employment-opportunity-law-poster-2009.pdf">Equal Employment Opportunity is the Law (EEO)&nbsp;</a></li><li><a href="/content/dam/company/us/en/policies/pdf/employment/equal-employment-opportunity-supplement-2009.pdf">EEO is the Law Poster Supplement</a></li><li><a href="/content/dam/company/us/en/reports/pdf/uniformed-services-employment-and-reemployment-rights-act-2017.pdf">USERRA Rights</a></li><li><a href="/content/dam/company/us/en/reports/pdf/employee-family-and-medical-leave-act-2016.pdf">Family and Medical Leave Act (FMLA)</a></li><li><a href="/content/dam/company/us/en/policies/pdf/employment/employee-polygraph-protection-act-2016.pdf">Employee Polygraph Protection Act (EPPA)</a></li><li><a href="/content/dam/company/us/en/policies/pdf/employment/e-verify-participation-poster-2017.pdf" target="_blank" rel="noopener noreferrer">E-Verify (English and Spanish)</a></li><li><a href="/content/dam/company/us/en/reports/pdf/immigrant-and-employee-rights-right-to-work-poster-english-2019.pdf">Right to Work (English)</a></li><li><a href="/content/dam/company/us/en/reports/pdf/pay-transparency-nondirscrimination-provision-english.pdf">Pay Transparency Nondiscrimination Provision (English)</a></li><li><a href="/content/dam/company/us/en/policies/pdf/employment/immigrant-and-employee-rights-right-to-work-poster-spanish-2019.pdf">Right to Work (Spanish)</a></li><li><a href="/content/dam/company/us/en/reports/pdf/pay-transparency-nondirscrimination-provision-spanish.pdf">Pay Transparency Nondiscrimination Provision (Spanish)</a></li><li><a href="/policies-and-practices/recruitment-scams-fraudulent-activity">Recruitment Scams &amp; Fraudulent activity</a></li><li><a href="/content/dam/company/us/en/policies/pdf/employment/coca-cola-business-strategy-leadership-model-december-2020.pdf">Business Strategy, Priorities &amp; Leadership Model</a></li><li><a href="/policies-and-practices/equal-employment-opportunity-employer-reports">Equal Employment Opportunity Employer Information Reports (EEO-1)</a></li><li><a href="https://health1.aetna.com/app/public/#/one/insurerCode=AETNACVS_I&amp;brandCode=ALICSI/machine-readable-transparency-in-coverage?searchTerm=263764&amp;lock=true">Price Transparency Requirements for Healthcare Coverage</a></li><li><a href="https://mcs.com.pr/en/Pages/Transparency.aspx#">Price Transparency Requirements for Healthcare Coverage (Puerto Rico)</a></li><li><a href="/policies-and-practices/accommodation-and-accessibility-request">Accommodation and Accessibility Request</a></li><li><a href="/policies-and-practices/leadership-growth-insights-privacy-policy">Leadership Growth Insights Privacy Policies</a></li></ul>

</div>

    

</div>

        
    </div>

</div>
</div>
    </div>

    
</div>
</div>
<div class="accordion panelcontainer faq" bis_skin_checked="1">
<div id="accordion-574708b73f" class="cmp-accordion" data-cmp-data-layer="{&quot;accordion-574708b73f&quot;:{&quot;shownItems&quot;:[&quot;accordion-574708b73f-item-0576454e4a&quot;,&quot;accordion-574708b73f-item-dd25c9f5f6&quot;,&quot;accordion-574708b73f-item-189ea892db&quot;,&quot;accordion-574708b73f-item-bc70e195d5&quot;],&quot;@type&quot;:&quot;cep/components/accordion&quot;,&quot;repo:modifyDate&quot;:&quot;2023-04-24T14:50:08Z&quot;}}" data-placeholder-text="false" bis_skin_checked="1">
    <div class="cmp-accordion__item" data-cmp-hook-accordion="item" data-cmp-data-layer="{&quot;accordion-574708b73f-item-0576454e4a&quot;:{&quot;@type&quot;:&quot;cep/components/accordion/item&quot;,&quot;repo:modifyDate&quot;:&quot;2023-04-20T09:31:04Z&quot;,&quot;dc:title&quot;:&quot;Sustainability&quot;}}" id="accordion-574708b73f-item-0576454e4a" data-cmp-expanded="" bis_skin_checked="1">
        <h3 class="cmp-accordion__header">
            <button id="accordion-574708b73f-item-0576454e4a-button" class="cmp-accordion__button cmp-accordion__button--expanded" type="button" aria-controls="accordion-574708b73f-item-0576454e4a-panel" data-cmp-hook-accordion="button" aria-expanded="true">
                <span class="cmp-accordion__title">Sustainability</span>
                <span class="cmp-accordion__icon"></span>
            </button>
        </h3>
        <div data-cmp-hook-accordion="panel" id="accordion-574708b73f-item-0576454e4a-panel" class="cmp-accordion__panel cmp-accordion__panel--expanded" role="region" aria-labelledby="accordion-574708b73f-item-0576454e4a-button" aria-hidden="false" bis_skin_checked="1"><div class="container responsivegrid" bis_skin_checked="1">

    
    
    
    
    <div id="container-0576454e4a" class="cmp-container" bis_skin_checked="1">

        

        
        <div class="text" bis_skin_checked="1">
<div data-cmp-data-layer="{&quot;text-a06b92da0a&quot;:{&quot;@type&quot;:&quot;cep/components/text&quot;,&quot;repo:modifyDate&quot;:&quot;2025-01-29T15:30:44Z&quot;,&quot;xdm:text&quot;:&quot;<ul>\r\n<li><a href=\&quot;/content/dam/company/us/en/reports/2023-environmental-update/2023-environmental-update.pdf\&quot;>2023 Environmental Update</a></li>\r\n</ul>\r\n<div>&amp;nbsp;</div>\r\n<ul>\r\n<li><a href=\&quot;https://www.coca-colacompany.com/content/dam/company/us/en/policies/pdf/sustainability/2023-cdp-climate-change-response.pdf\&quot; target=\&quot;_blank\&quot; rel=\&quot;noopener noreferrer\&quot;>2023 CDP Climate Change Response</a></li>\r\n<li><a href=\&quot;/content/dam/company/us/en/policies/pdf/sustainability/2023-CDP-Forests-Response.pdf\&quot;>2023 CDP Forests Response</a></li>\r\n<li><u><a href=\&quot;/content/dam/company/us/en/policies/pdf/sustainability/2023-CDP-Water-Response.pdf\&quot;>2023 CDP Water Response</a></u></li>\r\n</ul>\r\n<p>&amp;nbsp;</p>\r\n<ul>\r\n<li><a href=\&quot;/content/dam/company/us/en/reports/coca-cola-business-sustainability-report-2022.pdf\&quot;>2022 Business &amp;amp; Sustainability Report</a><br>\r\n</li>\r\n<li><a href=\&quot;/content/dam/company/us/en/reports/2022-business-report/coca-cola-business-and-sustainability-report-2022-highlights.pdf\&quot;>2022 Business &amp;amp; Sustainability Report Highlights</a></li>\r\n<li><a href=\&quot;/content/company/us/en/reports/2022-business-report/2022-reporting-framework-indexes.pdf\&quot;>2022 Reporting Frameworks &amp;amp; SDGs</a></li>\r\n<li><a href=\&quot;https://www.coca-colacompany.com/content/dam/company/us/en/policies/pdf/sustainability/2022-cdp-climate-change-response.pdf\&quot;>2022 CDP Climate Change Response</a></li>\r\n<li><a href=\&quot;/content/dam/company/us/en/policies/pdf/sustainability/2022-cdp-forests-response.pdf\&quot;>2022 CDP Forests Response</a><br>\r\n</li>\r\n<li><a href=\&quot;/content/dam/company/us/en/policies/pdf/sustainability/2022-cdp-water-response.pdf\&quot;>2022 CDP Water Response</a></li>\r\n</ul>\r\n<p>&amp;nbsp;</p>\r\n<ul>\r\n<li><a href=\&quot;/content/dam/company/us/en/reports/coca-cola-business-environmental-social-governance-report-2021.pdf\&quot;>2021 Business &amp;amp; Environmental, Social and Governance Report</a></li>\r\n<li><a href=\&quot;/content/dam/company/us/en/reports/coca-cola-business-environmental-social-governance-report-2021-highlights.pdf\&quot;>2021 Business &amp;amp; Environmental, Social and Governance Report Highlights</a></li>\r\n<li><a href=\&quot;/content/dam/company/us/en/policies/pdf/sustainability/2021-reporting-framework-indexes.pdf\&quot;>2021 Reporting Frameworks &amp;amp; SDGs</a><br>\r\n</li>\r\n<li><a href=\&quot;/content/company/us/en/reports/world-without-waste-2021.html\&quot;>2021 World Without Waste Report</a></li>\r\n<li><a href=\&quot;/content/dam/company/us/en/policies/pdf/sustainability/2021-tccc-carbon-accounting-manual.pdf\&quot;>2021 Carbon Accounting Manual</a></li>\r\n<li><a href=\&quot;https://www.coca-colacompany.com/content/dam/company/us/en/policies/pdf/sustainability/2021-cdp-climate-change-response.pdf\&quot; target=\&quot;_blank\&quot; rel=\&quot;noopener noreferrer\&quot;>2021 CDP Climate Change Response</a></li>\r\n<li><a href=\&quot;/content/dam/company/us/en/policies/pdf/sustainability/2021-cdp-forests-response.pdf\&quot;>2021 CDP Forests Response</a></li>\r\n<li><a href=\&quot;/content/dam/company/us/en/policies/pdf/sustainability/2021-cdp-water-response.pdf\&quot;>2021 CDP Water Response</a></li>\r\n</ul>\r\n<p>&amp;nbsp;</p>\r\n<ul>\r\n<li><a href=\&quot;/content/company/us/en/reports/business-environmental-social-governance-report-2020.html\&quot;>2020 Business &amp;amp; Environmental, Social and Governance Report</a><br>\r\n</li>\r\n<li><a href=\&quot;/content/dam/company/us/en/reports/coca-cola-business-environmental-social-governance-report-2020-highlights.pdf\&quot;>2020 Business &amp;amp; Environmental, Social and Governance Report Highlights</a></li>\r\n<li><a href=\&quot;/content/dam/company/us/en/policies/pdf/sustainability/2020-reporting-framework-indexes.pdf\&quot;>2020 Reporting Frameworks &amp;amp; SDGs</a></li>\r\n<li><a href=\&quot;/content/company/us/en/reports/world-without-waste-2020.html\&quot;>2020 World Without Waste Report</a></li>\r\n<li><a href=\&quot;/content/dam/company/us/en/reports/pdf/coca-cola-5by20-report-march-2021.pdf\&quot;>2020 5by20 Report</a></li>\r\n<li><a href=\&quot;https://www.coca-colacompany.com/content/dam/company/us/en/policies/pdf/sustainability/2020-cdp-climate-change-response.pdf\&quot; target=\&quot;_blank\&quot; rel=\&quot;noopener noreferrer\&quot;>2020 CDP Climate Change Response</a></li>\r\n<li><a href=\&quot;/content/dam/company/us/en/policies/pdf/sustainability/2020-cdp-water-response.pdf\&quot;>2020 CDP Water Response</a></li>\r\n</ul>\r\n<p>&amp;nbsp;</p>\r\n<ul>\r\n<li><a href=\&quot;/content/dam/company/us/en/reports/coca-cola-business-and-sustainability-report-2019.pdf\&quot;>2019 Business &amp;amp; Sustainability Report</a></li>\r\n<li><a href=\&quot;/content/dam/company/us/en/reports/coca-cola-business-and-sustainability-report-highlights-2019.pdf\&quot;>2019 Business &amp;amp; Sustainability Report Highlights</a></li>\r\n<li><a href=\&quot;/content/dam/company/us/en/reports/pdf/2019-reporting-framework-indexes.pdf\&quot;>2019 Reporting Framework Indexes</a></li>\r\n<li><a href=\&quot;/content/dam/company/us/en/reports/pdf/coca-cola-world-without-waste-report-2019.pdf\&quot;>2019 World Without Waste Report</a></li>\r\n<li><a href=\&quot;/content/dam/company/us/en/reports/pdf/water-progress-update-2019.pdf\&quot;>2019 Water Progress Update</a></li>\r\n<li><a href=\&quot;/content/dam/company/us/en/reports/pdf/2019-Water-Replenishment-Projects.pdf\&quot;>2019 Water Replenishment Projects</a></li>\r\n<li><a href=\&quot;/content/dam/company/us/en/reports/pdf/sustainable-ingredients-policy.pdf\&quot;>2019 Sustainable Ingredients Policy</a></li>\r\n<li><a href=\&quot;https://www.coca-colacompany.com/content/dam/company/us/en/policies/pdf/sustainability/2019-cdp-climate-change-response.pdf\&quot;>2019 CDP Climate Change Response</a></li>\r\n<li><a href=\&quot;/content/dam/company/us/en/policies/pdf/sustainability/2019-cdp-water-response.pdf\&quot;>2019 CDP Water Response</a></li>\r\n</ul>\r\n<p>&amp;nbsp;</p>\r\n<ul>\r\n<li><a href=\&quot;/content/dam/company/us/en/policies/pdf/sustainability/coca-cola-business-and-sustainability-report-2018.pdf\&quot;>2018 Business &amp;amp; Sustainability Report</a></li>\r\n<li><a href=\&quot;/content/dam/company/us/en/reports/pdf/world-without-waste-report-2018.pdf\&quot;>2018 World Without Waste Progress Report</a></li>\r\n<li><a href=\&quot;/content/dam/company/us/en/policies/pdf/sustainability/coca-cola-business-and-sustainability-report-2018.pdf#page=26\&quot;>2018 Water Stewardship Progress Report</a></li>\r\n<li><a href=\&quot;/content/dam/company/us/en/policies/pdf/sustainability/2018-climate-report.pdf\&quot;>2018 Climate Report</a></li>\r\n<li><a href=\&quot;https://www.coca-colacompany.com/content/dam/company/us/en/policies/pdf/sustainability/2018-cdp-climate-change-response.pdf\&quot; target=\&quot;_blank\&quot; rel=\&quot;noopener noreferrer\&quot;>2018 CDP Climate Change Response</a></li>\r\n<li><a href=\&quot;/content/dam/company/us/en/policies/pdf/sustainability/2018-cdp-water-response.pdf\&quot;>2018 CDP Water Response</a></li>\r\n<li><a href=\&quot;/content/dam/company/us/en/policies/pdf/sustainability/gri-index-2018.pdf\&quot;>2018 GRI Index</a></li>\r\n</ul>\r\n<p>&amp;nbsp;</p>\r\n<ul>\r\n<li><a href=\&quot;/content/dam/company/us/en/policies/pdf/sustainability/2017-sustainability-report-the-coca-cola-company.pdf\&quot;>2017 Sustainability Report</a></li>\r\n</ul>\r\n<p>&amp;nbsp;</p>\r\n<ul>\r\n<li><a href=\&quot;/content/dam/company/us/en/policies/pdf/sustainability/2016-sustainability-report-the-coca-cola-company.pdf\&quot;>2016 Sustainability Report</a></li>\r\n</ul>\r\n<p>&amp;nbsp;</p>\r\n<ul>\r\n<li><a href=\&quot;/content/company/us/en/policies-and-practices/principles-for-sustainable-agriculture.html\&quot;>Principles for Sustainable Agriculture</a><br>\r\n</li>\r\n<li><a href=\&quot;/content/company/us/en/policies-and-practices/animal-health-and-welfare-guiding-principles.html\&quot;>Animal Health and Welfare Guiding Principles</a></li>\r\n<li><a href=\&quot;/content/company/us/en/policies-and-practices/occupational-health-and-safety-policy.html\&quot;>Occupational Health &amp;amp; Safety Policy</a></li>\r\n<li><a href=\&quot;/content/company/us/en/policies-and-practices/quality-and-food-safety-policy.html\&quot;>Quality &amp;amp; Food Safety Policy</a></li>\r\n<li><a href=\&quot;/content/company/us/en/policies-and-practices/environmental-policy.html\&quot;>Environmental Policy</a></li>\r\n<li><a href=\&quot;/content/company/us/en/policies-and-practices/coca-cola-commitment-to-the-un-global-compact.html\&quot;>Coca-Cola Commitment to the UN Global Compact</a></li>\r\n<li><a href=\&quot;/content/dam/company/us/en/policies/pdf/sustainability/2024-Sustainable-Commerical-Paper-Program-Indication-Report.pdf\&quot; target=\&quot;_blank\&quot; rel=\&quot;noopener noreferrer\&quot;>2024 Sustainable Commercial Paper Program Indication Report</a></li>\r\n</ul>\r\n&quot;}}" id="text-a06b92da0a" class="cmp-text" bis_skin_checked="1">
    <ul><li><a href="/content/dam/company/us/en/reports/2023-environmental-update/2023-environmental-update.pdf">2023 Environmental Update</a></li></ul>
<div bis_skin_checked="1">&nbsp;</div>
<ul><li><a href="https://www.coca-colacompany.com/content/dam/company/us/en/policies/pdf/sustainability/2023-cdp-climate-change-response.pdf" target="_blank" rel="noopener noreferrer">2023 CDP Climate Change Response</a></li><li><a href="/content/dam/company/us/en/policies/pdf/sustainability/2023-CDP-Forests-Response.pdf">2023 CDP Forests Response</a></li><li><u><a href="/content/dam/company/us/en/policies/pdf/sustainability/2023-CDP-Water-Response.pdf">2023 CDP Water Response</a></u></li></ul>
<p>&nbsp;</p>
<ul><li><a href="/content/dam/company/us/en/reports/coca-cola-business-sustainability-report-2022.pdf">2022 Business &amp; Sustainability Report</a><br>
</li><li><a href="/content/dam/company/us/en/reports/2022-business-report/coca-cola-business-and-sustainability-report-2022-highlights.pdf">2022 Business &amp; Sustainability Report Highlights</a></li><li><a href="/content/company/us/en/reports/2022-business-report/2022-reporting-framework-indexes.pdf">2022 Reporting Frameworks &amp; SDGs</a></li><li><a href="https://www.coca-colacompany.com/content/dam/company/us/en/policies/pdf/sustainability/2022-cdp-climate-change-response.pdf">2022 CDP Climate Change Response</a></li><li><a href="/content/dam/company/us/en/policies/pdf/sustainability/2022-cdp-forests-response.pdf">2022 CDP Forests Response</a><br>
</li><li><a href="/content/dam/company/us/en/policies/pdf/sustainability/2022-cdp-water-response.pdf">2022 CDP Water Response</a></li></ul>
<p>&nbsp;</p>
<ul><li><a href="/content/dam/company/us/en/reports/coca-cola-business-environmental-social-governance-report-2021.pdf">2021 Business &amp; Environmental, Social and Governance Report</a></li><li><a href="/content/dam/company/us/en/reports/coca-cola-business-environmental-social-governance-report-2021-highlights.pdf">2021 Business &amp; Environmental, Social and Governance Report Highlights</a></li><li><a href="/content/dam/company/us/en/policies/pdf/sustainability/2021-reporting-framework-indexes.pdf">2021 Reporting Frameworks &amp; SDGs</a><br>
</li><li><a href="/reports/world-without-waste-2021">2021 World Without Waste Report</a></li><li><a href="/content/dam/company/us/en/policies/pdf/sustainability/2021-tccc-carbon-accounting-manual.pdf">2021 Carbon Accounting Manual</a></li><li><a href="https://www.coca-colacompany.com/content/dam/company/us/en/policies/pdf/sustainability/2021-cdp-climate-change-response.pdf" target="_blank" rel="noopener noreferrer">2021 CDP Climate Change Response</a></li><li><a href="/content/dam/company/us/en/policies/pdf/sustainability/2021-cdp-forests-response.pdf">2021 CDP Forests Response</a></li><li><a href="/content/dam/company/us/en/policies/pdf/sustainability/2021-cdp-water-response.pdf">2021 CDP Water Response</a></li></ul>
<p>&nbsp;</p>
<ul><li><a href="/reports/business-environmental-social-governance-report-2020">2020 Business &amp; Environmental, Social and Governance Report</a><br>
</li><li><a href="/content/dam/company/us/en/reports/coca-cola-business-environmental-social-governance-report-2020-highlights.pdf">2020 Business &amp; Environmental, Social and Governance Report Highlights</a></li><li><a href="/content/dam/company/us/en/policies/pdf/sustainability/2020-reporting-framework-indexes.pdf">2020 Reporting Frameworks &amp; SDGs</a></li><li><a href="/reports/world-without-waste-2020">2020 World Without Waste Report</a></li><li><a href="/content/dam/company/us/en/reports/pdf/coca-cola-5by20-report-march-2021.pdf">2020 5by20 Report</a></li><li><a href="https://www.coca-colacompany.com/content/dam/company/us/en/policies/pdf/sustainability/2020-cdp-climate-change-response.pdf" target="_blank" rel="noopener noreferrer">2020 CDP Climate Change Response</a></li><li><a href="/content/dam/company/us/en/policies/pdf/sustainability/2020-cdp-water-response.pdf">2020 CDP Water Response</a></li></ul>
<p>&nbsp;</p>
<ul><li><a href="/content/dam/company/us/en/reports/coca-cola-business-and-sustainability-report-2019.pdf">2019 Business &amp; Sustainability Report</a></li><li><a href="/content/dam/company/us/en/reports/coca-cola-business-and-sustainability-report-highlights-2019.pdf">2019 Business &amp; Sustainability Report Highlights</a></li><li><a href="/content/dam/company/us/en/reports/pdf/2019-reporting-framework-indexes.pdf">2019 Reporting Framework Indexes</a></li><li><a href="/content/dam/company/us/en/reports/pdf/coca-cola-world-without-waste-report-2019.pdf">2019 World Without Waste Report</a></li><li><a href="/content/dam/company/us/en/reports/pdf/water-progress-update-2019.pdf">2019 Water Progress Update</a></li><li><a href="/content/dam/company/us/en/reports/pdf/2019-Water-Replenishment-Projects.pdf">2019 Water Replenishment Projects</a></li><li><a href="/content/dam/company/us/en/reports/pdf/sustainable-ingredients-policy.pdf">2019 Sustainable Ingredients Policy</a></li><li><a href="https://www.coca-colacompany.com/content/dam/company/us/en/policies/pdf/sustainability/2019-cdp-climate-change-response.pdf">2019 CDP Climate Change Response</a></li><li><a href="/content/dam/company/us/en/policies/pdf/sustainability/2019-cdp-water-response.pdf">2019 CDP Water Response</a></li></ul>
<p>&nbsp;</p>
<ul><li><a href="/content/dam/company/us/en/policies/pdf/sustainability/coca-cola-business-and-sustainability-report-2018.pdf">2018 Business &amp; Sustainability Report</a></li><li><a href="/content/dam/company/us/en/reports/pdf/world-without-waste-report-2018.pdf">2018 World Without Waste Progress Report</a></li><li><a href="/content/dam/company/us/en/policies/pdf/sustainability/coca-cola-business-and-sustainability-report-2018.pdf#page=26">2018 Water Stewardship Progress Report</a></li><li><a href="/content/dam/company/us/en/policies/pdf/sustainability/2018-climate-report.pdf">2018 Climate Report</a></li><li><a href="https://www.coca-colacompany.com/content/dam/company/us/en/policies/pdf/sustainability/2018-cdp-climate-change-response.pdf" target="_blank" rel="noopener noreferrer">2018 CDP Climate Change Response</a></li><li><a href="/content/dam/company/us/en/policies/pdf/sustainability/2018-cdp-water-response.pdf">2018 CDP Water Response</a></li><li><a href="/content/dam/company/us/en/policies/pdf/sustainability/gri-index-2018.pdf">2018 GRI Index</a></li></ul>
<p>&nbsp;</p>
<ul><li><a href="/content/dam/company/us/en/policies/pdf/sustainability/2017-sustainability-report-the-coca-cola-company.pdf">2017 Sustainability Report</a></li></ul>
<p>&nbsp;</p>
<ul><li><a href="/content/dam/company/us/en/policies/pdf/sustainability/2016-sustainability-report-the-coca-cola-company.pdf">2016 Sustainability Report</a></li></ul>
<p>&nbsp;</p>
<ul><li><a href="/policies-and-practices/principles-for-sustainable-agriculture">Principles for Sustainable Agriculture</a><br>
</li><li><a href="/policies-and-practices/animal-health-and-welfare-guiding-principles">Animal Health and Welfare Guiding Principles</a></li><li><a href="/policies-and-practices/occupational-health-and-safety-policy">Occupational Health &amp; Safety Policy</a></li><li><a href="/policies-and-practices/quality-and-food-safety-policy">Quality &amp; Food Safety Policy</a></li><li><a href="/policies-and-practices/environmental-policy">Environmental Policy</a></li><li><a href="/policies-and-practices/coca-cola-commitment-to-the-un-global-compact">Coca‑Cola Commitment to the UN Global Compact</a></li><li><a href="/content/dam/company/us/en/policies/pdf/sustainability/2024-Sustainable-Commerical-Paper-Program-Indication-Report.pdf" target="_blank" rel="noopener noreferrer">2024 Sustainable Commercial Paper Program Indication Report</a></li></ul>

</div>

    

</div>

        
    </div>

</div>
</div>
    </div>
<div class="cmp-accordion__item" data-cmp-hook-accordion="item" data-cmp-data-layer="{&quot;accordion-574708b73f-item-dd25c9f5f6&quot;:{&quot;@type&quot;:&quot;cep/components/accordion/item&quot;,&quot;repo:modifyDate&quot;:&quot;2023-04-20T09:31:04Z&quot;,&quot;dc:title&quot;:&quot;Legal &amp; Practices&quot;}}" id="accordion-574708b73f-item-dd25c9f5f6" data-cmp-expanded="" bis_skin_checked="1">
        <h3 class="cmp-accordion__header">
            <button id="accordion-574708b73f-item-dd25c9f5f6-button" class="cmp-accordion__button cmp-accordion__button--expanded" type="button" aria-controls="accordion-574708b73f-item-dd25c9f5f6-panel" data-cmp-hook-accordion="button" aria-expanded="true">
                <span class="cmp-accordion__title">Legal &amp; Practices</span>
                <span class="cmp-accordion__icon"></span>
            </button>
        </h3>
        <div data-cmp-hook-accordion="panel" id="accordion-574708b73f-item-dd25c9f5f6-panel" class="cmp-accordion__panel cmp-accordion__panel--expanded" role="region" aria-labelledby="accordion-574708b73f-item-dd25c9f5f6-button" aria-hidden="false" bis_skin_checked="1"><div class="container responsivegrid" bis_skin_checked="1">

    
    
    
    
    <div id="container-dd25c9f5f6" class="cmp-container" bis_skin_checked="1">

        

        
        <div class="text" bis_skin_checked="1">
<div data-cmp-data-layer="{&quot;text-a3c334d275&quot;:{&quot;@type&quot;:&quot;cep/components/text&quot;,&quot;repo:modifyDate&quot;:&quot;2023-04-20T11:48:11Z&quot;,&quot;xdm:text&quot;:&quot;<ul>\r\n<li><a href=\&quot;/content/company/us/en/policies-and-practices/code-of-business-conduct.html\&quot;>Code of Business Conduct</a></li>\r\n<li><a href=\&quot;/content/company/us/en/policies-and-practices/anti-bribery-policy.html\&quot;>Anti-Bribery Policy</a></li>\r\n<li><a href=\&quot;/content/company/us/en/policies-and-practices/reporting-ethics-concerns.html\&quot;>Reporting Ethics Concerns</a></li>\r\n<li><a href=\&quot;/content/company/us/en/policies-and-practices/responsible-marketing-policy.html\&quot;>Responsible Marketing Policy</a></li>\r\n<li><a href=\&quot;/content/company/us/en/policies-and-practices/responsible-digital-media-principles.html\&quot;>Digital Media Principles</a></li>\r\n<li><a href=\&quot;/content/company/us/en/policies-and-practices/marketing-responsibly-in-the-united-states.html\&quot;>Marketing Responsibly in the U.S.</a></li>\r\n<li><a href=\&quot;/content/company/us/en/policies-and-practices/global-school-beverage-policy.html\&quot;>Global School Beverage Policy</a></li>\r\n<li><a href=\&quot;/content/company/us/en/policies-and-practices/responsible-alcohol-marketing-policy.html\&quot;>Responsible Alcohol Marketing Policy</a></li>\r\n<li><a href=\&quot;/content/company/us/en/policies-and-practices/hateful-activity-policy.html\&quot;>Hateful Activity Policy</a></li>\r\n<li><a href=\&quot;/content/company/us/en/policies-and-practices/dmca-request.html\&quot;>DMCA Requests</a></li>\r\n<li><a href=\&quot;/content/company/us/en/policies-and-practices/prohibition-on-cartel-activity.html\&quot;>Prohibition on Cartel Activity</a></li>\r\n<li><a href=\&quot;/content/dam/company/us/en/reports/The-Coca-Cola-Company-Alcohol-Social-Media-Community-Guidelines.pdf\&quot;>Alcohol Social Media Community Guidelines</a></li>\r\n</ul>\r\n&quot;}}" id="text-a3c334d275" class="cmp-text" bis_skin_checked="1">
    <ul><li><a href="/policies-and-practices/code-of-business-conduct">Code of Business Conduct</a></li><li><a href="/policies-and-practices/anti-bribery-policy">Anti-Bribery Policy</a></li><li><a href="/policies-and-practices/reporting-ethics-concerns">Reporting Ethics Concerns</a></li><li><a href="/policies-and-practices/responsible-marketing-policy">Responsible Marketing Policy</a></li><li><a href="/policies-and-practices/responsible-digital-media-principles">Digital Media Principles</a></li><li><a href="/policies-and-practices/marketing-responsibly-in-the-united-states">Marketing Responsibly in the U.S.</a></li><li><a href="/policies-and-practices/global-school-beverage-policy">Global School Beverage Policy</a></li><li><a href="/policies-and-practices/responsible-alcohol-marketing-policy">Responsible Alcohol Marketing Policy</a></li><li><a href="/policies-and-practices/hateful-activity-policy">Hateful Activity Policy</a></li><li><a href="/policies-and-practices/dmca-request">DMCA Requests</a></li><li><a href="/policies-and-practices/prohibition-on-cartel-activity">Prohibition on Cartel Activity</a></li><li><a href="/content/dam/company/us/en/reports/The-Coca-Cola-Company-Alcohol-Social-Media-Community-Guidelines.pdf">Alcohol Social Media Community Guidelines</a></li></ul>

</div>

    

</div>

        
    </div>

</div>
</div>
    </div>
<div class="cmp-accordion__item" data-cmp-hook-accordion="item" data-cmp-data-layer="{&quot;accordion-574708b73f-item-189ea892db&quot;:{&quot;@type&quot;:&quot;cep/components/accordion/item&quot;,&quot;dc:title&quot;:&quot;Shareowner Services&quot;}}" id="accordion-574708b73f-item-189ea892db" data-cmp-expanded="" bis_skin_checked="1">
        <h3 class="cmp-accordion__header">
            <button id="accordion-574708b73f-item-189ea892db-button" class="cmp-accordion__button cmp-accordion__button--expanded" type="button" aria-controls="accordion-574708b73f-item-189ea892db-panel" data-cmp-hook-accordion="button" aria-expanded="true">
                <span class="cmp-accordion__title">Shareowner Services</span>
                <span class="cmp-accordion__icon"></span>
            </button>
        </h3>
        <div data-cmp-hook-accordion="panel" id="accordion-574708b73f-item-189ea892db-panel" class="cmp-accordion__panel cmp-accordion__panel--expanded" role="region" aria-labelledby="accordion-574708b73f-item-189ea892db-button" aria-hidden="false" bis_skin_checked="1"><div class="container responsivegrid" bis_skin_checked="1">

    
    <div id="container-189ea892db" class="cmp-container" bis_skin_checked="1">
        


<div class="aem-Grid aem-Grid--12 aem-Grid--default--12 " bis_skin_checked="1">
    
    <div class="text aem-GridColumn aem-GridColumn--default--12" bis_skin_checked="1">
<div data-cmp-data-layer="{&quot;text-45806e6d8f&quot;:{&quot;@type&quot;:&quot;cep/components/text&quot;,&quot;repo:modifyDate&quot;:&quot;2025-01-29T15:23:01Z&quot;,&quot;xdm:text&quot;:&quot;<ul>\r\n<li><a href=\&quot;https://investors.coca-colacompany.com/shareowners\&quot;>Shareowners Main Page</a></li>\r\n</ul>\r\n&quot;}}" id="text-45806e6d8f" class="cmp-text" bis_skin_checked="1">
    <ul><li><a href="https://investors.coca-colacompany.com/shareowners">Shareowners Main Page</a></li></ul>

</div>

    

</div>

    
</div>

    </div>

    
</div>
</div>
    </div>
<div class="cmp-accordion__item" data-cmp-hook-accordion="item" data-cmp-data-layer="{&quot;accordion-574708b73f-item-bc70e195d5&quot;:{&quot;@type&quot;:&quot;cep/components/accordion/item&quot;,&quot;dc:title&quot;:&quot;Advocacy &amp; Political Engagement&quot;}}" id="accordion-574708b73f-item-bc70e195d5" data-cmp-expanded="" bis_skin_checked="1">
        <h3 class="cmp-accordion__header">
            <button id="accordion-574708b73f-item-bc70e195d5-button" class="cmp-accordion__button cmp-accordion__button--expanded" type="button" aria-controls="accordion-574708b73f-item-bc70e195d5-panel" data-cmp-hook-accordion="button" aria-expanded="true">
                <span class="cmp-accordion__title">Advocacy &amp; Political Engagement</span>
                <span class="cmp-accordion__icon"></span>
            </button>
        </h3>
        <div data-cmp-hook-accordion="panel" id="accordion-574708b73f-item-bc70e195d5-panel" class="cmp-accordion__panel cmp-accordion__panel--expanded" role="region" aria-labelledby="accordion-574708b73f-item-bc70e195d5-button" aria-hidden="false" bis_skin_checked="1"><div class="container responsivegrid" bis_skin_checked="1">

    
    <div id="container-bc70e195d5" class="cmp-container" bis_skin_checked="1">
        


<div class="aem-Grid aem-Grid--12 aem-Grid--default--12 " bis_skin_checked="1">
    
    <div class="text aem-GridColumn aem-GridColumn--default--12" bis_skin_checked="1">
<div data-cmp-data-layer="{&quot;text-d955937f1c&quot;:{&quot;@type&quot;:&quot;cep/components/text&quot;,&quot;repo:modifyDate&quot;:&quot;2025-01-29T15:29:41Z&quot;,&quot;xdm:text&quot;:&quot;<ul>\r\n<li><a href=\&quot;/content/company/us/en/policies-and-practices/public-policy-and-political-engagement.html\&quot;>Public Policy &amp;amp; Political Engagement</a></li>\r\n<li><a href=\&quot;/content/company/us/en/policies-and-practices/political-contributions.html\&quot;>Coca-Cola PAC &amp;amp; Corporate Political Contributions</a></li>\r\n<li><a href=\&quot;/content/company/us/en/policies-and-practices/lobbying-disclosure-reports.html\&quot;>Lobbying Disclosure Reports (LD-2 &amp;amp; LD-203)</a></li>\r\n</ul>\r\n&quot;}}" id="text-d955937f1c" class="cmp-text" bis_skin_checked="1">
    <ul><li><a href="/policies-and-practices/public-policy-and-political-engagement">Public Policy &amp; Political Engagement</a></li><li><a href="/policies-and-practices/political-contributions">Coca‑Cola PAC &amp; Corporate Political Contributions</a></li><li><a href="/policies-and-practices/lobbying-disclosure-reports">Lobbying Disclosure Reports (LD-2 &amp; LD-203)</a></li></ul>

</div>

    

</div>

    
</div>

    </div>

    
</div>
</div>
    </div>

    
</div>
</div>
<div class="accordion panelcontainer faq" bis_skin_checked="1">
<div id="accordion-8a8af91dd2" class="cmp-accordion" data-cmp-data-layer="{&quot;accordion-8a8af91dd2&quot;:{&quot;shownItems&quot;:[&quot;accordion-8a8af91dd2-item-1ba6e0c065&quot;,&quot;accordion-8a8af91dd2-item-032612c674&quot;,&quot;accordion-8a8af91dd2-item-2f47059882&quot;,&quot;accordion-8a8af91dd2-item-2f69f95f1a&quot;],&quot;@type&quot;:&quot;cep/components/accordion&quot;,&quot;repo:modifyDate&quot;:&quot;2023-04-20T13:43:07Z&quot;}}" data-placeholder-text="false" bis_skin_checked="1">
    <div class="cmp-accordion__item" data-cmp-hook-accordion="item" data-cmp-data-layer="{&quot;accordion-8a8af91dd2-item-1ba6e0c065&quot;:{&quot;@type&quot;:&quot;cep/components/accordion/item&quot;,&quot;repo:modifyDate&quot;:&quot;2023-04-20T09:32:32Z&quot;,&quot;dc:title&quot;:&quot;Human &amp; Workplace Rights&quot;}}" id="accordion-8a8af91dd2-item-1ba6e0c065" data-cmp-expanded="" bis_skin_checked="1">
        <h3 class="cmp-accordion__header">
            <button id="accordion-8a8af91dd2-item-1ba6e0c065-button" class="cmp-accordion__button cmp-accordion__button--expanded" type="button" aria-controls="accordion-8a8af91dd2-item-1ba6e0c065-panel" data-cmp-hook-accordion="button" aria-expanded="true">
                <span class="cmp-accordion__title">Human &amp; Workplace Rights</span>
                <span class="cmp-accordion__icon"></span>
            </button>
        </h3>
        <div data-cmp-hook-accordion="panel" id="accordion-8a8af91dd2-item-1ba6e0c065-panel" class="cmp-accordion__panel cmp-accordion__panel--expanded" role="region" aria-labelledby="accordion-8a8af91dd2-item-1ba6e0c065-button" aria-hidden="false" bis_skin_checked="1"><div class="container responsivegrid" bis_skin_checked="1">

    
    
    
    
    <div id="container-1ba6e0c065" class="cmp-container" bis_skin_checked="1">

        

        
        <div class="text" bis_skin_checked="1">
<div data-cmp-data-layer="{&quot;text-93cc2b8642&quot;:{&quot;@type&quot;:&quot;cep/components/text&quot;,&quot;repo:modifyDate&quot;:&quot;2025-01-29T15:23:55Z&quot;,&quot;xdm:text&quot;:&quot;<ul>\r\n<li><a href=\&quot;/content/dam/company/us/en/reports/2023-data-updates/2023-human-rights-update.pdf\&quot;>2023 Human Rights Update</a></li>\r\n<li><a href=\&quot;/content/dam/company/us/en/reports/2023-data-updates/2023-workplace-and-safety-update.pdf\&quot;>2023 Workplace and Safety Update</a></li>\r\n<li><a href=\&quot;/content/dam/company/us/en/policies/pdf/social/human-rights-overview-2022.pdf\&quot;>2022 Human Rights Overview</a></li>\r\n<li><a href=\&quot;/content/dam/company/us/en/reports/pdf/CocaCola_Global%20Human%20Rights%20Policy_Document_20240419_v9.15.pdf\&quot;>Global Human Rights Policy (English)</a></li>\r\n<li><a href=\&quot;/content/company/us/en/policies-and-practices/human-rights-policy-languages.html\&quot;>Global Human Rights Policy (Translations)</a>&amp;nbsp;&amp;nbsp;</li>\r\n<li><a href=\&quot;/content/dam/company/us/en/reports/pdf/2024-04%20-%20Coca-Cola%20-%20HRP%20poster%20-%20English%20-%20ONLINE%20-%20v2.4.pdf\&quot;>Human Rights Policy Poster (English)</a></li>\r\n<li><a href=\&quot;/content/company/us/en/policies-and-practices/human-rights-policy-posters.html\&quot;>Human Rights Policy Poster (Translations)</a></li>\r\n<li><a href=\&quot;/content/company/us/en/policies-and-practices/supplier-guiding-principles.html\&quot;>Supplier Guiding Principles</a></li>\r\n<li><a href=\&quot;/content/company/us/en/policies-and-practices/supplier-guiding-principles-languages.html\&quot;>Supplier Guiding Principles - Languages</a></li>\r\n<li><a href=\&quot;/content/company/us/en/policies-and-practices/supplier-code-of-business-conduct.html\&quot;>Supplier Code of Business Conduct</a></li>\r\n<li><a href=\&quot;/content/company/us/en/policies-and-practices/supplier-code-of-business-conduct-languages.html\&quot;>Supplier Code of Business Conduct - Languages</a></li>\r\n<li><a href=\&quot;/content/dam/company/us/en/policies/pdf/human-workplace-rights/addressing-global-issues/the-coca-cola-companys-human-rights-report.pdf\&quot;>Human Rights Report</a></li>\r\n<li><a href=\&quot;/content/company/us/en/policies-and-practices/human-and-workplace-rights-materials-for-employees.html\&quot;>Human &amp;amp; Workplace Rights Materials for Employees</a></li>\r\n<li><a href=\&quot;/content/company/us/en/policies-and-practices/safety-and-health.html\&quot;>Safety &amp;amp; Health</a></li>\r\n<li><a href=\&quot;/content/company/us/en/policies-and-practices/addressing-global-issues.html\&quot;>Addressing Global Issues</a></li>\r\n<li><a href=\&quot;/content/company/us/en/policies-and-practices/human-rights-engaging-stakeholders.html\&quot;>Human Rights - Engaging Stakeholders</a></li>\r\n<li><a href=\&quot;/content/company/us/en/policies-and-practices/california-transparency-in-supply-chain-act.html\&quot;>California Transparency in Supply Chain Act</a></li>\r\n<li><a href=\&quot;/content/company/us/en/policies-and-practices/sgp-guidance-documents.html\&quot;>SGP Guidance Documents</a></li>\r\n<li><a href=\&quot;/content/company/us/en/policies-and-practices/sgp-implementation-guide-languages.html\&quot;>SGP Guidance Documents - Languages</a></li>\r\n<li><a href=\&quot;/content/company/us/en/policies-and-practices/human-rights-self-assessment-checklists.html\&quot;>Human Rights Self Assessment</a></li>\r\n<li><a href=\&quot;/content/dam/company/us/en/policies/pdf/human-workplace-rights/human-rights-restructuring-guidelines/human-rights-restructuring-guidelines-2020-framework.pdf\&quot;>Human Rights Restructuring Guidelines</a></li>\r\n</ul>\r\n&quot;}}" id="text-93cc2b8642" class="cmp-text" bis_skin_checked="1">
    <ul><li><a href="/content/dam/company/us/en/reports/2023-data-updates/2023-human-rights-update.pdf">2023 Human Rights Update</a></li><li><a href="/content/dam/company/us/en/reports/2023-data-updates/2023-workplace-and-safety-update.pdf">2023 Workplace and Safety Update</a></li><li><a href="/content/dam/company/us/en/policies/pdf/social/human-rights-overview-2022.pdf">2022 Human Rights Overview</a></li><li><a href="/content/dam/company/us/en/reports/pdf/CocaCola_Global%20Human%20Rights%20Policy_Document_20240419_v9.15.pdf">Global Human Rights Policy (English)</a></li><li><a href="/policies-and-practices/human-rights-policy-languages">Global Human Rights Policy (Translations)</a>&nbsp;&nbsp;</li><li><a href="/content/dam/company/us/en/reports/pdf/2024-04%20-%20Coca-Cola%20-%20HRP%20poster%20-%20English%20-%20ONLINE%20-%20v2.4.pdf">Human Rights Policy Poster (English)</a></li><li><a href="/policies-and-practices/human-rights-policy-posters">Human Rights Policy Poster (Translations)</a></li><li><a href="/policies-and-practices/supplier-guiding-principles">Supplier Guiding Principles</a></li><li><a href="/policies-and-practices/supplier-guiding-principles-languages">Supplier Guiding Principles - Languages</a></li><li><a href="/policies-and-practices/supplier-code-of-business-conduct">Supplier Code of Business Conduct</a></li><li><a href="/policies-and-practices/supplier-code-of-business-conduct-languages">Supplier Code of Business Conduct - Languages</a></li><li><a href="/content/dam/company/us/en/policies/pdf/human-workplace-rights/addressing-global-issues/the-coca-cola-companys-human-rights-report.pdf">Human Rights Report</a></li><li><a href="/policies-and-practices/human-and-workplace-rights-materials-for-employees">Human &amp; Workplace Rights Materials for Employees</a></li><li><a href="/policies-and-practices/safety-and-health">Safety &amp; Health</a></li><li><a href="/policies-and-practices/addressing-global-issues">Addressing Global Issues</a></li><li><a href="/policies-and-practices/human-rights-engaging-stakeholders">Human Rights - Engaging Stakeholders</a></li><li><a href="/policies-and-practices/california-transparency-in-supply-chain-act">California Transparency in Supply Chain Act</a></li><li><a href="/policies-and-practices/sgp-guidance-documents">SGP Guidance Documents</a></li><li><a href="/policies-and-practices/sgp-implementation-guide-languages">SGP Guidance Documents - Languages</a></li><li><a href="/policies-and-practices/human-rights-self-assessment-checklists">Human Rights Self Assessment</a></li><li><a href="/content/dam/company/us/en/policies/pdf/human-workplace-rights/human-rights-restructuring-guidelines/human-rights-restructuring-guidelines-2020-framework.pdf">Human Rights Restructuring Guidelines</a></li></ul>

</div>

    

</div>

        
    </div>

</div>
</div>
    </div>
<div class="cmp-accordion__item" data-cmp-hook-accordion="item" data-cmp-data-layer="{&quot;accordion-8a8af91dd2-item-032612c674&quot;:{&quot;@type&quot;:&quot;cep/components/accordion/item&quot;,&quot;repo:modifyDate&quot;:&quot;2023-03-30T14:40:33Z&quot;,&quot;dc:title&quot;:&quot;Corporate Governance&quot;}}" id="accordion-8a8af91dd2-item-032612c674" data-cmp-expanded="" bis_skin_checked="1">
        <h3 class="cmp-accordion__header">
            <button id="accordion-8a8af91dd2-item-032612c674-button" class="cmp-accordion__button cmp-accordion__button--expanded" type="button" aria-controls="accordion-8a8af91dd2-item-032612c674-panel" data-cmp-hook-accordion="button" aria-expanded="true">
                <span class="cmp-accordion__title">Corporate Governance</span>
                <span class="cmp-accordion__icon"></span>
            </button>
        </h3>
        <div data-cmp-hook-accordion="panel" id="accordion-8a8af91dd2-item-032612c674-panel" class="cmp-accordion__panel cmp-accordion__panel--expanded" role="region" aria-labelledby="accordion-8a8af91dd2-item-032612c674-button" aria-hidden="false" bis_skin_checked="1"><div class="container responsivegrid" bis_skin_checked="1">

    
    
    
    
    <div id="container-032612c674" class="cmp-container" bis_skin_checked="1">

        

        
        <div class="text" bis_skin_checked="1">
<div data-cmp-data-layer="{&quot;text-e461cd6830&quot;:{&quot;@type&quot;:&quot;cep/components/text&quot;,&quot;repo:modifyDate&quot;:&quot;2025-01-29T15:26:36Z&quot;,&quot;xdm:text&quot;:&quot;<ul>\r\n<li><a href=\&quot;https://d1io3yog0oux5.cloudfront.net/_fd6a3e721c8feb0db6fa2e45899401ee/cocacolacompany/db/719/7231/file/Corporate+Governance+Guidelines+as+of+October+19%2C+2023.pdf\&quot;>Corporate Governance Guidelines</a></li>\r\n<li><a href=\&quot;/content/dam/company/us/en/policies/pdf/corporate-governance/code-of-business-conduct/coca-cola-coc-external.pdf\&quot;>Code of Business Conduct (English PDF)</a></li>\r\n<li><a href=\&quot;/content/company/us/en/policies-and-practices/supplier-code-of-business-conduct.html\&quot;>Code of Business Conduct</a></li>\r\n<li><a href=\&quot;https://d1io3yog0oux5.cloudfront.net/_fd6a3e721c8feb0db6fa2e45899401ee/cocacolacompany/db/719/7229/file/Binder1.pdf\&quot;>Certificate of Incorporation</a></li>\r\n<li><a href=\&quot;https://d1io3yog0oux5.cloudfront.net/_fd6a3e721c8feb0db6fa2e45899401ee/cocacolacompany/db/719/7230/file/2023-10-19+Amended+and+Restated+Bylaws+as+of+October+19%2C+2023+%28FINAL%29.pdf\&quot;>Company Bylaws</a></li>\r\n<li><a href=\&quot;/content/dam/company/us/en/policies/pdf/corporate-governance/code-of-business-conduct/directors-code-2018.pdf\&quot;>Code of Business Conduct for Non Employee Directors (English)</a></li>\r\n<li><a href=\&quot;/content/company/us/en/policies-and-practices/supplier-code-of-business-conduct-languages.html\&quot;>Code of Business Conduct (Other Languages)</a></li>\r\n</ul>\r\n&quot;}}" id="text-e461cd6830" class="cmp-text" bis_skin_checked="1">
    <ul><li><a href="https://d1io3yog0oux5.cloudfront.net/_fd6a3e721c8feb0db6fa2e45899401ee/cocacolacompany/db/719/7231/file/Corporate+Governance+Guidelines+as+of+October+19%2C+2023.pdf">Corporate Governance Guidelines</a></li><li><a href="/content/dam/company/us/en/policies/pdf/corporate-governance/code-of-business-conduct/coca-cola-coc-external.pdf">Code of Business Conduct (English PDF)</a></li><li><a href="/policies-and-practices/supplier-code-of-business-conduct">Code of Business Conduct</a></li><li><a href="https://d1io3yog0oux5.cloudfront.net/_fd6a3e721c8feb0db6fa2e45899401ee/cocacolacompany/db/719/7229/file/Binder1.pdf">Certificate of Incorporation</a></li><li><a href="https://d1io3yog0oux5.cloudfront.net/_fd6a3e721c8feb0db6fa2e45899401ee/cocacolacompany/db/719/7230/file/2023-10-19+Amended+and+Restated+Bylaws+as+of+October+19%2C+2023+%28FINAL%29.pdf">Company Bylaws</a></li><li><a href="/content/dam/company/us/en/policies/pdf/corporate-governance/code-of-business-conduct/directors-code-2018.pdf">Code of Business Conduct for Non Employee Directors (English)</a></li><li><a href="/policies-and-practices/supplier-code-of-business-conduct-languages">Code of Business Conduct (Other Languages)</a></li></ul>

</div>

    

</div>

        
    </div>

</div>
</div>
    </div>
<div class="cmp-accordion__item" data-cmp-hook-accordion="item" data-cmp-data-layer="{&quot;accordion-8a8af91dd2-item-2f47059882&quot;:{&quot;@type&quot;:&quot;cep/components/accordion/item&quot;,&quot;dc:title&quot;:&quot;The Coca-Cola Foundation&quot;}}" id="accordion-8a8af91dd2-item-2f47059882" data-cmp-expanded="" bis_skin_checked="1">
        <h3 class="cmp-accordion__header">
            <button id="accordion-8a8af91dd2-item-2f47059882-button" class="cmp-accordion__button cmp-accordion__button--expanded" type="button" aria-controls="accordion-8a8af91dd2-item-2f47059882-panel" data-cmp-hook-accordion="button" aria-expanded="true">
                <span class="cmp-accordion__title">The Coca‑Cola Foundation</span>
                <span class="cmp-accordion__icon"></span>
            </button>
        </h3>
        <div data-cmp-hook-accordion="panel" id="accordion-8a8af91dd2-item-2f47059882-panel" class="cmp-accordion__panel cmp-accordion__panel--expanded" role="region" aria-labelledby="accordion-8a8af91dd2-item-2f47059882-button" aria-hidden="false" bis_skin_checked="1"><div class="container responsivegrid" bis_skin_checked="1">

    
    <div id="container-2f47059882" class="cmp-container" bis_skin_checked="1">
        


<div class="aem-Grid aem-Grid--12 aem-Grid--default--12 " bis_skin_checked="1">
    
    <div class="text aem-GridColumn aem-GridColumn--default--12" bis_skin_checked="1">
<div data-cmp-data-layer="{&quot;text-024ca464ad&quot;:{&quot;@type&quot;:&quot;cep/components/text&quot;,&quot;repo:modifyDate&quot;:&quot;2025-01-29T15:29:02Z&quot;,&quot;xdm:text&quot;:&quot;<ul>\r\n<li><a href=\&quot;/content/dam/company/us/en/reports/2023-data-updates/2023-giving-back-update.pdf\&quot;>2023 Giving Back Update</a></li>\r\n<li><a href=\&quot;content/dam/company/us/en/reports/pdf/2023-TCCF-Tax-Return-Form-990.pdf\&quot;>2023 The Coca-Cola Foundation Form 990-PF Return</a></li>\r\n<li><a href=\&quot;/content/dam/company/us/en/policies/pdf/the-coca-cola-foundation/the-coca-cola%20foundation-inc-%202021-tax-return-copy-for-public-inspection.pdf\&quot;>2021 The Coca-Cola Foundation Form 990-PF Return</a></li>\r\n<li><a href=\&quot;/content/dam/company/us/en/policies/pdf/the-coca-cola-foundation/2020-CCF-Form-990-PF.pdf\&quot;>2020 Coca-Cola Foundation Form 990 PF Return</a></li>\r\n<li><a href=\&quot;/content/dam/company/us/en/policies/pdf/the-coca-cola-foundation/The-Coca-Cola-Foundation-Charitable-Giving-List-2019.pdf\&quot;>2019 Charitable Contributions Report</a></li>\r\n<li><a href=\&quot;/content/dam/company/us/en/policies/pdf/the-coca-cola-foundation/2018-charitable-contributions-report-amended.pdf\&quot;>2018 Charitable Contributions Report</a></li>\r\n<li><a href=\&quot;https://coca-cola.smartsimple.com/s_Login.jsp\&quot;>Application Form for Grants</a></li>\r\n</ul>\r\n&quot;}}" id="text-024ca464ad" class="cmp-text" bis_skin_checked="1">
    <ul><li><a href="/content/dam/company/us/en/reports/2023-data-updates/2023-giving-back-update.pdf">2023 Giving Back Update</a></li><li><a href="content/dam/company/us/en/reports/pdf/2023-TCCF-Tax-Return-Form-990.pdf">2023 The Coca‑Cola Foundation Form 990-PF Return</a></li><li><a href="/content/dam/company/us/en/policies/pdf/the-coca-cola-foundation/the-coca-cola%20foundation-inc-%202021-tax-return-copy-for-public-inspection.pdf">2021 The Coca‑Cola Foundation Form 990-PF Return</a></li><li><a href="/content/dam/company/us/en/policies/pdf/the-coca-cola-foundation/2020-CCF-Form-990-PF.pdf">2020 Coca‑Cola Foundation Form 990 PF Return</a></li><li><a href="/content/dam/company/us/en/policies/pdf/the-coca-cola-foundation/The-Coca-Cola-Foundation-Charitable-Giving-List-2019.pdf">2019 Charitable Contributions Report</a></li><li><a href="/content/dam/company/us/en/policies/pdf/the-coca-cola-foundation/2018-charitable-contributions-report-amended.pdf">2018 Charitable Contributions Report</a></li><li><a href="https://coca-cola.smartsimple.com/s_Login.jsp">Application Form for Grants</a></li></ul>

</div>

    

</div>

    
</div>

    </div>

    
</div>
</div>
    </div>
<div class="cmp-accordion__item" data-cmp-hook-accordion="item" data-cmp-data-layer="{&quot;accordion-8a8af91dd2-item-2f69f95f1a&quot;:{&quot;@type&quot;:&quot;cep/components/accordion/item&quot;,&quot;dc:title&quot;:&quot;Supplier Requirements&quot;}}" id="accordion-8a8af91dd2-item-2f69f95f1a" data-cmp-expanded="" bis_skin_checked="1">
        <h3 class="cmp-accordion__header">
            <button id="accordion-8a8af91dd2-item-2f69f95f1a-button" class="cmp-accordion__button cmp-accordion__button--expanded" type="button" aria-controls="accordion-8a8af91dd2-item-2f69f95f1a-panel" data-cmp-hook-accordion="button" aria-expanded="true">
                <span class="cmp-accordion__title">Supplier Requirements</span>
                <span class="cmp-accordion__icon"></span>
            </button>
        </h3>
        <div data-cmp-hook-accordion="panel" id="accordion-8a8af91dd2-item-2f69f95f1a-panel" class="cmp-accordion__panel cmp-accordion__panel--expanded" role="region" aria-labelledby="accordion-8a8af91dd2-item-2f69f95f1a-button" aria-hidden="false" bis_skin_checked="1"><div class="container responsivegrid" bis_skin_checked="1">

    
    <div id="container-2f69f95f1a" class="cmp-container" bis_skin_checked="1">
        


<div class="aem-Grid aem-Grid--12 aem-Grid--default--12 " bis_skin_checked="1">
    
    <div class="text aem-GridColumn aem-GridColumn--default--12" bis_skin_checked="1">
<div data-cmp-data-layer="{&quot;text-63e9822116&quot;:{&quot;@type&quot;:&quot;cep/components/text&quot;,&quot;repo:modifyDate&quot;:&quot;2025-01-29T17:42:45Z&quot;,&quot;xdm:text&quot;:&quot;<ul>\r\n<li><a href=\&quot;https://tccc.starssmp.com/\&quot;>Become a Supplier</a></li>\r\n<li><a href=\&quot;/content/company/us/en/policies-and-practices/supplier-requirements.html\&quot;>Supplier Requirements</a></li>\r\n<li><a href=\&quot;/content/dam/company/us/en/policies/pdf/supplier-requirements/principles-for-sustainable-agriculture-supplier-guide.pdf\&quot;>Principles for Sustainable Agriculture Supplier Guide</a></li>\r\n<li><a href=\&quot;/content/company/us/en/policies-and-practices/patent-license-for-suppliers.html\&quot;>Patent License Terms for Suppliers</a></li>\r\n<li><a href=\&quot;/content/dam/company/us/en/policies/pdf/legal-and-practices/artwork-labeling-and-intellectual-property.pdf\&quot;>Artwork, Labeling &amp;amp; Intellectual Property</a></li>\r\n<li><a href=\&quot;/content/dam/company/us/en/policies/pdf/legal-and-practices/KORE-General-Supplier-Requirements-General.pdf\&quot;>General Supplier Requirements [KORE]</a></li>\r\n<li><a href=\&quot;/content/dam/company/us/en/policies/pdf/legal-and-practices/kore-ingredient-supplier-requirements.pdf\&quot;>Ingredient Supplier Requirements [KORE]</a></li>\r\n<li><a href=\&quot;/content/dam/company/us/en/policies/pdf/legal-and-practices/KORE-Ingredient-Supplier-Requirements-Pre-Pack.pdf\&quot;>Ingredient – Pre-Pack – Supplier Requirements [KORE]</a></li>\r\n<li><a href=\&quot;/content/dam/company/us/en/policies/pdf/legal-and-practices/KORE-Ingredient-Supplier-Requirements-Food-Allergen-and-Sensitivity-Control.pdf\&quot;>Ingredient – Food Allergen Sensitivity - Supplier Requirements [KORE]</a></li>\r\n<li><a href=\&quot;/content/company/us/en/policies-and-practices/global-purchase-order-terms-and-conditions.html\&quot;>Global Purchase Order Terms and Conditions</a></li>\r\n<li><a href=\&quot;/content/dam/company/us/en/policies/pdf/legal-and-practices/global-food-allergen-and-sensitivity-template.pdf\&quot;>Global Food Allergen and Sensitivity Template</a></li>\r\n<li><a href=\&quot;/content/dam/company/us/en/policies/pdf/supplier-requirements/The%20Coca-Cola%20Company%20Supplier%20Invoicing%20Guide_version%20Nov.%202024.pdf\&quot;>Supplier Invoicing Guide</a></li>\r\n</ul>\r\n&quot;}}" id="text-63e9822116" class="cmp-text" bis_skin_checked="1">
    <ul><li><a href="https://tccc.starssmp.com/">Become a Supplier</a></li><li><a href="/policies-and-practices/supplier-requirements">Supplier Requirements</a></li><li><a href="/content/dam/company/us/en/policies/pdf/supplier-requirements/principles-for-sustainable-agriculture-supplier-guide.pdf">Principles for Sustainable Agriculture Supplier Guide</a></li><li><a href="/policies-and-practices/patent-license-for-suppliers">Patent License Terms for Suppliers</a></li><li><a href="/content/dam/company/us/en/policies/pdf/legal-and-practices/artwork-labeling-and-intellectual-property.pdf">Artwork, Labeling &amp; Intellectual Property</a></li><li><a href="/content/dam/company/us/en/policies/pdf/legal-and-practices/KORE-General-Supplier-Requirements-General.pdf">General Supplier Requirements [KORE]</a></li><li><a href="/content/dam/company/us/en/policies/pdf/legal-and-practices/kore-ingredient-supplier-requirements.pdf">Ingredient Supplier Requirements [KORE]</a></li><li><a href="/content/dam/company/us/en/policies/pdf/legal-and-practices/KORE-Ingredient-Supplier-Requirements-Pre-Pack.pdf">Ingredient – Pre-Pack – Supplier Requirements [KORE]</a></li><li><a href="/content/dam/company/us/en/policies/pdf/legal-and-practices/KORE-Ingredient-Supplier-Requirements-Food-Allergen-and-Sensitivity-Control.pdf">Ingredient – Food Allergen Sensitivity - Supplier Requirements [KORE]</a></li><li><a href="/policies-and-practices/global-purchase-order-terms-and-conditions">Global Purchase Order Terms and Conditions</a></li><li><a href="/content/dam/company/us/en/policies/pdf/legal-and-practices/global-food-allergen-and-sensitivity-template.pdf">Global Food Allergen and Sensitivity Template</a></li><li><a href="/content/dam/company/us/en/policies/pdf/supplier-requirements/The%20Coca-Cola%20Company%20Supplier%20Invoicing%20Guide_version%20Nov.%202024.pdf">Supplier Invoicing Guide</a></li></ul>

</div>

    

</div>

    
</div>

    </div>

    
</div>
</div>
    </div>

    
</div>
</div>

        
    </div>
    Extraction:
[
	{
		"event_name": "Our Purpose and Vision"
		"date": "NULL"
		"files": ["/about-us/purpose-and-vision"]
		
	},
	{
		"event_name": "Privacy Policy (U.S.)"
		"date": "NULL"
		"files": ["https://www.coca-cola.com/us/en/legal/privacy-policy"]
	},
	{
		"event_name": "Cookie Policy (U.S.)"
		"date": "NULL"
		"files": ["https://www.coca-cola.com/us/en/legal/cookies-policy"]
	},
    ...
    
    
	{
		"event_name": "Overview of Country Sugar Study on Labor Practices"
		"date": "NULL"
		"files": ["/content/dam/company/us/en/policies/pdf/human-workplace-rights/addressing-global-issues/human-rights-in-the-coca-cola-sugar-supply-chain.pdf"]
	},
    
    ...
    
	{
		"event_name": "2023 Workplace Representation Update"
		"date": "2023"
		"files": ["/content/dam/company/us/en/reports/2023-data-updates/2023-workplace-representation-update.pdf"]
	},
    
    ...
    
	{
		"event_name": "2023 Environmental Update"
		"date": "2023"
		"files": ["/content/dam/company/us/en/reports/2023-environmental-update/2023-environmental-update.pdf"]
	},
	{
		event_name: "2023 CDP Climate Change Response"
		date: "2023"
		"files": ["https://www.coca-colacompany.com/content/dam/company/us/en/policies/pdf/sustainability/2023-cdp-climate-change-response.pdf"]
	},
    
    ...
    
	{
		event_name: "2018 CDP Climate Change Response"
		date: "2018"
		"files": ["https://www.coca-colacompany.com/content/dam/company/us/en/policies/pdf/sustainability/2018-cdp-climate-change-response.pdf"]
	},
    
    ...
    
	{
		event_name: "2023 Human Rights Update"
		date: "2023"
		"files": ["/content/dam/company/us/en/reports/2023-data-updates/2023-human-rights-update.pdf"]
	},
	
    ...]
    '''
            },

            {
                "role": "user",
                "content": f'''{html}''',
            },
        ]
    )
    cleaned_text = chat_response.choices[0].message.content.replace('json', '')
    print(cleaned_text)
    return json.loads(cleaned_text)


# a = llm_all('''<div id="container-e4e0b86b80" class="cmp-container" bis_skin_checked="1">

'''
        
        <div class="accordion panelcontainer faq" bis_skin_checked="1">
<div id="accordion-4151fd9fe7" class="cmp-accordion" data-cmp-data-layer="{&quot;accordion-4151fd9fe7&quot;:{&quot;shownItems&quot;:[&quot;accordion-4151fd9fe7-item-adefddf132&quot;,&quot;accordion-4151fd9fe7-item-7ea3f98ce4&quot;,&quot;accordion-4151fd9fe7-item-837d094e55&quot;,&quot;accordion-4151fd9fe7-item-db0a8c4be8&quot;],&quot;@type&quot;:&quot;cep/components/accordion&quot;,&quot;repo:modifyDate&quot;:&quot;2023-04-24T14:51:36Z&quot;}}" data-placeholder-text="false" bis_skin_checked="1">
    <div class="cmp-accordion__item" data-cmp-hook-accordion="item" data-cmp-data-layer="{&quot;accordion-4151fd9fe7-item-adefddf132&quot;:{&quot;@type&quot;:&quot;cep/components/accordion/item&quot;,&quot;dc:title&quot;:&quot;Company Overview&quot;}}" id="accordion-4151fd9fe7-item-adefddf132" data-cmp-expanded="" bis_skin_checked="1">
        <h3 class="cmp-accordion__header">
            <button id="accordion-4151fd9fe7-item-adefddf132-button" class="cmp-accordion__button cmp-accordion__button--expanded" type="button" aria-controls="accordion-4151fd9fe7-item-adefddf132-panel" data-cmp-hook-accordion="button" aria-expanded="true">
                <span class="cmp-accordion__title">Company Overview</span>
                <span class="cmp-accordion__icon"></span>
            </button>
        </h3>
        <div data-cmp-hook-accordion="panel" id="accordion-4151fd9fe7-item-adefddf132-panel" class="cmp-accordion__panel cmp-accordion__panel--expanded" role="region" aria-labelledby="accordion-4151fd9fe7-item-adefddf132-button" aria-hidden="false" bis_skin_checked="1"><div class="container responsivegrid" bis_skin_checked="1">

    
    <div id="container-adefddf132" class="cmp-container" bis_skin_checked="1">
        


<div class="aem-Grid aem-Grid--12 aem-Grid--default--12 " bis_skin_checked="1">
    
    <div class="text aem-GridColumn aem-GridColumn--default--12" bis_skin_checked="1">
<div data-cmp-data-layer="{&quot;text-e397727dc1&quot;:{&quot;@type&quot;:&quot;cep/components/text&quot;,&quot;repo:modifyDate&quot;:&quot;2025-01-14T19:01:07Z&quot;,&quot;xdm:text&quot;:&quot;<ul>\r\n<li><a href=\&quot;/content/company/us/en/about-us/purpose-and-vision.html\&quot;>Our Purpose and Vision</a></li>\r\n</ul>\r\n&quot;}}" id="text-e397727dc1" class="cmp-text" bis_skin_checked="1">
    <ul><li><a href="/about-us/purpose-and-vision">Our Purpose and Vision</a></li></ul>

</div>

    

</div>

    
</div>

    </div>

    
</div>
</div>
    </div>
<div class="cmp-accordion__item" data-cmp-hook-accordion="item" data-cmp-data-layer="{&quot;accordion-4151fd9fe7-item-7ea3f98ce4&quot;:{&quot;@type&quot;:&quot;cep/components/accordion/item&quot;,&quot;dc:title&quot;:&quot;Privacy &amp; Data Protection&quot;}}" id="accordion-4151fd9fe7-item-7ea3f98ce4" data-cmp-expanded="" bis_skin_checked="1">
        <h3 class="cmp-accordion__header">
            <button id="accordion-4151fd9fe7-item-7ea3f98ce4-button" class="cmp-accordion__button cmp-accordion__button--expanded" type="button" aria-controls="accordion-4151fd9fe7-item-7ea3f98ce4-panel" data-cmp-hook-accordion="button" aria-expanded="true">
                <span class="cmp-accordion__title">Privacy &amp; Data Protection</span>
                <span class="cmp-accordion__icon"></span>
            </button>
        </h3>
        <div data-cmp-hook-accordion="panel" id="accordion-4151fd9fe7-item-7ea3f98ce4-panel" class="cmp-accordion__panel cmp-accordion__panel--expanded" role="region" aria-labelledby="accordion-4151fd9fe7-item-7ea3f98ce4-button" aria-hidden="false" bis_skin_checked="1"><div class="container responsivegrid" bis_skin_checked="1">

    
    <div id="container-7ea3f98ce4" class="cmp-container" bis_skin_checked="1">
        


<div class="aem-Grid aem-Grid--12 aem-Grid--default--12 " bis_skin_checked="1">
    
    <div class="text aem-GridColumn aem-GridColumn--default--12" bis_skin_checked="1">
<div data-cmp-data-layer="{&quot;text-1480ee97d6&quot;:{&quot;@type&quot;:&quot;cep/components/text&quot;,&quot;repo:modifyDate&quot;:&quot;2024-09-13T20:04:03Z&quot;,&quot;xdm:text&quot;:&quot;<ul>\r\n<li><a href=\&quot;https://www.coca-cola.com/us/en/legal/privacy-policy\&quot;>Privacy Policy (U.S.)</a></li>\r\n<li><a href=\&quot;https://www.coca-cola.com/us/en/legal/cookies-policy\&quot;>Cookie Policy (U.S.)</a></li>\r\n<li><a href=\&quot;https://www.coca-cola.com/us/en/legal/terms-of-service\&quot;>Terms of Service (U.S.)</a></li>\r\n<li><a href=\&quot;/content/company/us/en/policies-and-practices/usage-rights-requests.html\&quot;>Usage Rights Requests (U.S.)</a></li>\r\n<li><a href=\&quot;/content/company/us/en/policies-and-practices/vulnerability-disclosure.html\&quot;>Vulnerability Disclosure Policy</a></li>\r\n</ul>\r\n&quot;}}" id="text-1480ee97d6" class="cmp-text" bis_skin_checked="1">
    <ul><li><a href="https://www.coca-cola.com/us/en/legal/privacy-policy">Privacy Policy (U.S.)</a></li><li><a href="https://www.coca-cola.com/us/en/legal/cookies-policy">Cookie Policy (U.S.)</a></li><li><a href="https://www.coca-cola.com/us/en/legal/terms-of-service">Terms of Service (U.S.)</a></li><li><a href="/policies-and-practices/usage-rights-requests">Usage Rights Requests (U.S.)</a></li><li><a href="/policies-and-practices/vulnerability-disclosure">Vulnerability Disclosure Policy</a></li></ul>

</div>

    

</div>

    
</div>

    </div>

    
</div>
</div>
    </div>
<div class="cmp-accordion__item" data-cmp-hook-accordion="item" data-cmp-data-layer="{&quot;accordion-4151fd9fe7-item-837d094e55&quot;:{&quot;@type&quot;:&quot;cep/components/accordion/item&quot;,&quot;repo:modifyDate&quot;:&quot;2023-03-30T14:38:51Z&quot;,&quot;dc:title&quot;:&quot;Research &amp; Studies&quot;}}" id="accordion-4151fd9fe7-item-837d094e55" data-cmp-expanded="" bis_skin_checked="1">
        <h3 class="cmp-accordion__header">
            <button id="accordion-4151fd9fe7-item-837d094e55-button" class="cmp-accordion__button cmp-accordion__button--expanded" type="button" aria-controls="accordion-4151fd9fe7-item-837d094e55-panel" data-cmp-hook-accordion="button" aria-expanded="true">
                <span class="cmp-accordion__title">Research &amp; Studies</span>
                <span class="cmp-accordion__icon"></span>
            </button>
        </h3>
        <div data-cmp-hook-accordion="panel" id="accordion-4151fd9fe7-item-837d094e55-panel" class="cmp-accordion__panel cmp-accordion__panel--expanded" role="region" aria-labelledby="accordion-4151fd9fe7-item-837d094e55-button" aria-hidden="false" bis_skin_checked="1"><div class="container responsivegrid" bis_skin_checked="1">

    
    
    
    
    <div id="container-837d094e55" class="cmp-container" bis_skin_checked="1">

        

        
        <div class="text" bis_skin_checked="1">
<div data-cmp-data-layer="{&quot;text-4e914879ae&quot;:{&quot;@type&quot;:&quot;cep/components/text&quot;,&quot;repo:modifyDate&quot;:&quot;2025-01-29T15:18:43Z&quot;,&quot;xdm:text&quot;:&quot;<ul>\r\n<li><a href=\&quot;/content/dam/company/us/en/policies/pdf/human-workplace-rights/addressing-global-issues/human-rights-in-the-coca-cola-sugar-supply-chain.pdf\&quot;>Overview of Country Sugar Study on Labor Practices</a></li>\r\n<li><a href=\&quot;/content/dam/company/us/en/reports/pdf/sugar-study-methodology-overview.pdf\&quot;>Sugar Study Methodology</a></li>\r\n<li><a href=\&quot;/content/company/us/en/policies-and-practices/country-sugar-studies.html\&quot;>Country Reports</a></li>\r\n<li><a href=\&quot;https://www.coca-colacompany.com/policies-and-practices/transparency\&quot;>Transparency in Partnerships</a></li>\r\n</ul>\r\n&quot;}}" id="text-4e914879ae" class="cmp-text" bis_skin_checked="1">
    <ul><li><a href="/content/dam/company/us/en/policies/pdf/human-workplace-rights/addressing-global-issues/human-rights-in-the-coca-cola-sugar-supply-chain.pdf">Overview of Country Sugar Study on Labor Practices</a></li><li><a href="/content/dam/company/us/en/reports/pdf/sugar-study-methodology-overview.pdf">Sugar Study Methodology</a></li><li><a href="/policies-and-practices/country-sugar-studies">Country Reports</a></li><li><a href="https://www.coca-colacompany.com/policies-and-practices/transparency">Transparency in Partnerships</a></li></ul>

</div>

    

</div>

        
    </div>

</div>
</div>
    </div>
<div class="cmp-accordion__item" data-cmp-hook-accordion="item" data-cmp-data-layer="{&quot;accordion-4151fd9fe7-item-db0a8c4be8&quot;:{&quot;@type&quot;:&quot;cep/components/accordion/item&quot;,&quot;repo:modifyDate&quot;:&quot;2023-04-20T08:23:00Z&quot;,&quot;dc:title&quot;:&quot;Employment&quot;}}" id="accordion-4151fd9fe7-item-db0a8c4be8" data-cmp-expanded="" bis_skin_checked="1">
        <h3 class="cmp-accordion__header">
            <button id="accordion-4151fd9fe7-item-db0a8c4be8-button" class="cmp-accordion__button cmp-accordion__button--expanded" type="button" aria-controls="accordion-4151fd9fe7-item-db0a8c4be8-panel" data-cmp-hook-accordion="button" aria-expanded="true">
                <span class="cmp-accordion__title">Employment</span>
                <span class="cmp-accordion__icon"></span>
            </button>
        </h3>
        <div data-cmp-hook-accordion="panel" id="accordion-4151fd9fe7-item-db0a8c4be8-panel" class="cmp-accordion__panel cmp-accordion__panel--expanded" role="region" aria-labelledby="accordion-4151fd9fe7-item-db0a8c4be8-button" aria-hidden="false" bis_skin_checked="1"><div class="container responsivegrid" bis_skin_checked="1">

    
    
    
    
    <div id="container-db0a8c4be8" class="cmp-container" bis_skin_checked="1">

        

        
        <div class="text" bis_skin_checked="1">
<div data-cmp-data-layer="{&quot;text-ddea1cb10c&quot;:{&quot;@type&quot;:&quot;cep/components/text&quot;,&quot;repo:modifyDate&quot;:&quot;2024-11-22T16:05:45Z&quot;,&quot;xdm:text&quot;:&quot;<ul>\r\n<li><a href=\&quot;/content/dam/company/us/en/reports/2023-data-updates/2023-workplace-representation-update.pdf\&quot;>2023 Workplace Representation Update</a></li>\r\n<li><a href=\&quot;/content/company/us/en/policies-and-practices/equal-employment-opportunity.html\&quot;>Equal Employment Opportunity</a></li>\r\n<li><a href=\&quot;/content/dam/company/us/en/policies/pdf/employment/coca-cola-applicant-privacy-notice-Oct2023.pdf\&quot;>Global&amp;nbsp;Applicant Privacy Notice&amp;nbsp;- English</a></li>\r\n<li><a href=\&quot;/content/company/us/en/policies-and-practices/global-applicant-privacy-notice-translated-by-country.html\&quot;>Global Applicant Privacy Notice - Translated by Country</a></li>\r\n<li><a href=\&quot;/content/company/us/en/policies-and-practices/equal-employment-opportunity-and-affirmative-action-2020-english.html\&quot;>Equal Employment Opportunity and Affirmative Action Policy</a></li>\r\n<li><a href=\&quot;/content/company/us/en/policies-and-practices/equal-employment-opportunity-and-affirmative-action-spanish.html\&quot;>Equal Employment Opportunity and Affirmative Action Policy - Spanish</a></li>\r\n<li><a href=\&quot;/content/dam/company/us/en/policies/pdf/employment/equal-employment-opportunity-law-poster-2009.pdf\&quot;>Equal Employment Opportunity is the Law (EEO)&amp;nbsp;</a></li>\r\n<li><a href=\&quot;/content/dam/company/us/en/policies/pdf/employment/equal-employment-opportunity-supplement-2009.pdf\&quot;>EEO is the Law Poster Supplement</a></li>\r\n<li><a href=\&quot;/content/dam/company/us/en/reports/pdf/uniformed-services-employment-and-reemployment-rights-act-2017.pdf\&quot;>USERRA Rights</a></li>\r\n<li><a href=\&quot;/content/dam/company/us/en/reports/pdf/employee-family-and-medical-leave-act-2016.pdf\&quot;>Family and Medical Leave Act (FMLA)</a></li>\r\n<li><a href=\&quot;/content/dam/company/us/en/policies/pdf/employment/employee-polygraph-protection-act-2016.pdf\&quot;>Employee Polygraph Protection Act (EPPA)</a></li>\r\n<li><a href=\&quot;/content/dam/company/us/en/policies/pdf/employment/e-verify-participation-poster-2017.pdf\&quot; target=\&quot;_blank\&quot; rel=\&quot;noopener noreferrer\&quot;>E-Verify (English and Spanish)</a></li>\r\n<li><a href=\&quot;/content/dam/company/us/en/reports/pdf/immigrant-and-employee-rights-right-to-work-poster-english-2019.pdf\&quot;>Right to Work (English)</a></li>\r\n<li><a href=\&quot;/content/dam/company/us/en/reports/pdf/pay-transparency-nondirscrimination-provision-english.pdf\&quot;>Pay Transparency Nondiscrimination Provision (English)</a></li>\r\n<li><a href=\&quot;/content/dam/company/us/en/policies/pdf/employment/immigrant-and-employee-rights-right-to-work-poster-spanish-2019.pdf\&quot;>Right to Work (Spanish)</a></li>\r\n<li><a href=\&quot;/content/dam/company/us/en/reports/pdf/pay-transparency-nondirscrimination-provision-spanish.pdf\&quot;>Pay Transparency Nondiscrimination Provision (Spanish)</a></li>\r\n<li><a href=\&quot;/content/company/us/en/policies-and-practices/recruitment-scams-fraudulent-activity.html\&quot;>Recruitment Scams &amp;amp; Fraudulent activity</a></li>\r\n<li><a href=\&quot;/content/dam/company/us/en/policies/pdf/employment/coca-cola-business-strategy-leadership-model-december-2020.pdf\&quot;>Business Strategy, Priorities &amp;amp; Leadership Model</a></li>\r\n<li><a href=\&quot;/content/company/us/en/policies-and-practices/equal-employment-opportunity-employer-reports.html\&quot;>Equal Employment Opportunity Employer Information Reports (EEO-1)</a></li>\r\n<li><a href=\&quot;https://health1.aetna.com/app/public/#/one/insurerCode=AETNACVS_I&amp;amp;brandCode=ALICSI/machine-readable-transparency-in-coverage?searchTerm=263764&amp;amp;lock=true\&quot;>Price Transparency Requirements for Healthcare Coverage</a></li>\r\n<li><a href=\&quot;https://mcs.com.pr/en/Pages/Transparency.aspx#\&quot;>Price Transparency Requirements for Healthcare Coverage (Puerto Rico)</a></li>\r\n<li><a href=\&quot;/content/company/us/en/policies-and-practices/accommodation-and-accessibility-request.html\&quot;>Accommodation and Accessibility Request</a></li>\r\n<li><a href=\&quot;/content/company/us/en/policies-and-practices/leadership-growth-insights-privacy-policy.html\&quot;>Leadership Growth Insights Privacy Policies</a></li>\r\n</ul>\r\n&quot;}}" id="text-ddea1cb10c" class="cmp-text" bis_skin_checked="1">
    <ul><li><a href="/content/dam/company/us/en/reports/2023-data-updates/2023-workplace-representation-update.pdf">2023 Workplace Representation Update</a></li><li><a href="/policies-and-practices/equal-employment-opportunity">Equal Employment Opportunity</a></li><li><a href="/content/dam/company/us/en/policies/pdf/employment/coca-cola-applicant-privacy-notice-Oct2023.pdf">Global&nbsp;Applicant Privacy Notice&nbsp;- English</a></li><li><a href="/policies-and-practices/global-applicant-privacy-notice-translated-by-country">Global Applicant Privacy Notice - Translated by Country</a></li><li><a href="/policies-and-practices/equal-employment-opportunity-and-affirmative-action-2020-english">Equal Employment Opportunity and Affirmative Action Policy</a></li><li><a href="/policies-and-practices/equal-employment-opportunity-and-affirmative-action-spanish">Equal Employment Opportunity and Affirmative Action Policy - Spanish</a></li><li><a href="/content/dam/company/us/en/policies/pdf/employment/equal-employment-opportunity-law-poster-2009.pdf">Equal Employment Opportunity is the Law (EEO)&nbsp;</a></li><li><a href="/content/dam/company/us/en/policies/pdf/employment/equal-employment-opportunity-supplement-2009.pdf">EEO is the Law Poster Supplement</a></li><li><a href="/content/dam/company/us/en/reports/pdf/uniformed-services-employment-and-reemployment-rights-act-2017.pdf">USERRA Rights</a></li><li><a href="/content/dam/company/us/en/reports/pdf/employee-family-and-medical-leave-act-2016.pdf">Family and Medical Leave Act (FMLA)</a></li><li><a href="/content/dam/company/us/en/policies/pdf/employment/employee-polygraph-protection-act-2016.pdf">Employee Polygraph Protection Act (EPPA)</a></li><li><a href="/content/dam/company/us/en/policies/pdf/employment/e-verify-participation-poster-2017.pdf" target="_blank" rel="noopener noreferrer">E-Verify (English and Spanish)</a></li><li><a href="/content/dam/company/us/en/reports/pdf/immigrant-and-employee-rights-right-to-work-poster-english-2019.pdf">Right to Work (English)</a></li><li><a href="/content/dam/company/us/en/reports/pdf/pay-transparency-nondirscrimination-provision-english.pdf">Pay Transparency Nondiscrimination Provision (English)</a></li><li><a href="/content/dam/company/us/en/policies/pdf/employment/immigrant-and-employee-rights-right-to-work-poster-spanish-2019.pdf">Right to Work (Spanish)</a></li><li><a href="/content/dam/company/us/en/reports/pdf/pay-transparency-nondirscrimination-provision-spanish.pdf">Pay Transparency Nondiscrimination Provision (Spanish)</a></li><li><a href="/policies-and-practices/recruitment-scams-fraudulent-activity">Recruitment Scams &amp; Fraudulent activity</a></li><li><a href="/content/dam/company/us/en/policies/pdf/employment/coca-cola-business-strategy-leadership-model-december-2020.pdf">Business Strategy, Priorities &amp; Leadership Model</a></li><li><a href="/policies-and-practices/equal-employment-opportunity-employer-reports">Equal Employment Opportunity Employer Information Reports (EEO-1)</a></li><li><a href="https://health1.aetna.com/app/public/#/one/insurerCode=AETNACVS_I&amp;brandCode=ALICSI/machine-readable-transparency-in-coverage?searchTerm=263764&amp;lock=true">Price Transparency Requirements for Healthcare Coverage</a></li><li><a href="https://mcs.com.pr/en/Pages/Transparency.aspx#">Price Transparency Requirements for Healthcare Coverage (Puerto Rico)</a></li><li><a href="/policies-and-practices/accommodation-and-accessibility-request">Accommodation and Accessibility Request</a></li><li><a href="/policies-and-practices/leadership-growth-insights-privacy-policy">Leadership Growth Insights Privacy Policies</a></li></ul>

</div>

    

</div>

        
    </div>

</div>
</div>
    </div>

    
</div>
</div>
<div class="accordion panelcontainer faq" bis_skin_checked="1">
<div id="accordion-574708b73f" class="cmp-accordion" data-cmp-data-layer="{&quot;accordion-574708b73f&quot;:{&quot;shownItems&quot;:[&quot;accordion-574708b73f-item-0576454e4a&quot;,&quot;accordion-574708b73f-item-dd25c9f5f6&quot;,&quot;accordion-574708b73f-item-189ea892db&quot;,&quot;accordion-574708b73f-item-bc70e195d5&quot;],&quot;@type&quot;:&quot;cep/components/accordion&quot;,&quot;repo:modifyDate&quot;:&quot;2023-04-24T14:50:08Z&quot;}}" data-placeholder-text="false" bis_skin_checked="1">
    <div class="cmp-accordion__item" data-cmp-hook-accordion="item" data-cmp-data-layer="{&quot;accordion-574708b73f-item-0576454e4a&quot;:{&quot;@type&quot;:&quot;cep/components/accordion/item&quot;,&quot;repo:modifyDate&quot;:&quot;2023-04-20T09:31:04Z&quot;,&quot;dc:title&quot;:&quot;Sustainability&quot;}}" id="accordion-574708b73f-item-0576454e4a" data-cmp-expanded="" bis_skin_checked="1">
        <h3 class="cmp-accordion__header">
            <button id="accordion-574708b73f-item-0576454e4a-button" class="cmp-accordion__button cmp-accordion__button--expanded" type="button" aria-controls="accordion-574708b73f-item-0576454e4a-panel" data-cmp-hook-accordion="button" aria-expanded="true">
                <span class="cmp-accordion__title">Sustainability</span>
                <span class="cmp-accordion__icon"></span>
            </button>
        </h3>
        <div data-cmp-hook-accordion="panel" id="accordion-574708b73f-item-0576454e4a-panel" class="cmp-accordion__panel cmp-accordion__panel--expanded" role="region" aria-labelledby="accordion-574708b73f-item-0576454e4a-button" aria-hidden="false" bis_skin_checked="1"><div class="container responsivegrid" bis_skin_checked="1">

    
    
    
    
    <div id="container-0576454e4a" class="cmp-container" bis_skin_checked="1">

        

        
        <div class="text" bis_skin_checked="1">
<div data-cmp-data-layer="{&quot;text-a06b92da0a&quot;:{&quot;@type&quot;:&quot;cep/components/text&quot;,&quot;repo:modifyDate&quot;:&quot;2025-01-29T15:30:44Z&quot;,&quot;xdm:text&quot;:&quot;<ul>\r\n<li><a href=\&quot;/content/dam/company/us/en/reports/2023-environmental-update/2023-environmental-update.pdf\&quot;>2023 Environmental Update</a></li>\r\n</ul>\r\n<div>&amp;nbsp;</div>\r\n<ul>\r\n<li><a href=\&quot;https://www.coca-colacompany.com/content/dam/company/us/en/policies/pdf/sustainability/2023-cdp-climate-change-response.pdf\&quot; target=\&quot;_blank\&quot; rel=\&quot;noopener noreferrer\&quot;>2023 CDP Climate Change Response</a></li>\r\n<li><a href=\&quot;/content/dam/company/us/en/policies/pdf/sustainability/2023-CDP-Forests-Response.pdf\&quot;>2023 CDP Forests Response</a></li>\r\n<li><u><a href=\&quot;/content/dam/company/us/en/policies/pdf/sustainability/2023-CDP-Water-Response.pdf\&quot;>2023 CDP Water Response</a></u></li>\r\n</ul>\r\n<p>&amp;nbsp;</p>\r\n<ul>\r\n<li><a href=\&quot;/content/dam/company/us/en/reports/coca-cola-business-sustainability-report-2022.pdf\&quot;>2022 Business &amp;amp; Sustainability Report</a><br>\r\n</li>\r\n<li><a href=\&quot;/content/dam/company/us/en/reports/2022-business-report/coca-cola-business-and-sustainability-report-2022-highlights.pdf\&quot;>2022 Business &amp;amp; Sustainability Report Highlights</a></li>\r\n<li><a href=\&quot;/content/company/us/en/reports/2022-business-report/2022-reporting-framework-indexes.pdf\&quot;>2022 Reporting Frameworks &amp;amp; SDGs</a></li>\r\n<li><a href=\&quot;https://www.coca-colacompany.com/content/dam/company/us/en/policies/pdf/sustainability/2022-cdp-climate-change-response.pdf\&quot;>2022 CDP Climate Change Response</a></li>\r\n<li><a href=\&quot;/content/dam/company/us/en/policies/pdf/sustainability/2022-cdp-forests-response.pdf\&quot;>2022 CDP Forests Response</a><br>\r\n</li>\r\n<li><a href=\&quot;/content/dam/company/us/en/policies/pdf/sustainability/2022-cdp-water-response.pdf\&quot;>2022 CDP Water Response</a></li>\r\n</ul>\r\n<p>&amp;nbsp;</p>\r\n<ul>\r\n<li><a href=\&quot;/content/dam/company/us/en/reports/coca-cola-business-environmental-social-governance-report-2021.pdf\&quot;>2021 Business &amp;amp; Environmental, Social and Governance Report</a></li>\r\n<li><a href=\&quot;/content/dam/company/us/en/reports/coca-cola-business-environmental-social-governance-report-2021-highlights.pdf\&quot;>2021 Business &amp;amp; Environmental, Social and Governance Report Highlights</a></li>\r\n<li><a href=\&quot;/content/dam/company/us/en/policies/pdf/sustainability/2021-reporting-framework-indexes.pdf\&quot;>2021 Reporting Frameworks &amp;amp; SDGs</a><br>\r\n</li>\r\n<li><a href=\&quot;/content/company/us/en/reports/world-without-waste-2021.html\&quot;>2021 World Without Waste Report</a></li>\r\n<li><a href=\&quot;/content/dam/company/us/en/policies/pdf/sustainability/2021-tccc-carbon-accounting-manual.pdf\&quot;>2021 Carbon Accounting Manual</a></li>\r\n<li><a href=\&quot;https://www.coca-colacompany.com/content/dam/company/us/en/policies/pdf/sustainability/2021-cdp-climate-change-response.pdf\&quot; target=\&quot;_blank\&quot; rel=\&quot;noopener noreferrer\&quot;>2021 CDP Climate Change Response</a></li>\r\n<li><a href=\&quot;/content/dam/company/us/en/policies/pdf/sustainability/2021-cdp-forests-response.pdf\&quot;>2021 CDP Forests Response</a></li>\r\n<li><a href=\&quot;/content/dam/company/us/en/policies/pdf/sustainability/2021-cdp-water-response.pdf\&quot;>2021 CDP Water Response</a></li>\r\n</ul>\r\n<p>&amp;nbsp;</p>\r\n<ul>\r\n<li><a href=\&quot;/content/company/us/en/reports/business-environmental-social-governance-report-2020.html\&quot;>2020 Business &amp;amp; Environmental, Social and Governance Report</a><br>\r\n</li>\r\n<li><a href=\&quot;/content/dam/company/us/en/reports/coca-cola-business-environmental-social-governance-report-2020-highlights.pdf\&quot;>2020 Business &amp;amp; Environmental, Social and Governance Report Highlights</a></li>\r\n<li><a href=\&quot;/content/dam/company/us/en/policies/pdf/sustainability/2020-reporting-framework-indexes.pdf\&quot;>2020 Reporting Frameworks &amp;amp; SDGs</a></li>\r\n<li><a href=\&quot;/content/company/us/en/reports/world-without-waste-2020.html\&quot;>2020 World Without Waste Report</a></li>\r\n<li><a href=\&quot;/content/dam/company/us/en/reports/pdf/coca-cola-5by20-report-march-2021.pdf\&quot;>2020 5by20 Report</a></li>\r\n<li><a href=\&quot;https://www.coca-colacompany.com/content/dam/company/us/en/policies/pdf/sustainability/2020-cdp-climate-change-response.pdf\&quot; target=\&quot;_blank\&quot; rel=\&quot;noopener noreferrer\&quot;>2020 CDP Climate Change Response</a></li>\r\n<li><a href=\&quot;/content/dam/company/us/en/policies/pdf/sustainability/2020-cdp-water-response.pdf\&quot;>2020 CDP Water Response</a></li>\r\n</ul>\r\n<p>&amp;nbsp;</p>\r\n<ul>\r\n<li><a href=\&quot;/content/dam/company/us/en/reports/coca-cola-business-and-sustainability-report-2019.pdf\&quot;>2019 Business &amp;amp; Sustainability Report</a></li>\r\n<li><a href=\&quot;/content/dam/company/us/en/reports/coca-cola-business-and-sustainability-report-highlights-2019.pdf\&quot;>2019 Business &amp;amp; Sustainability Report Highlights</a></li>\r\n<li><a href=\&quot;/content/dam/company/us/en/reports/pdf/2019-reporting-framework-indexes.pdf\&quot;>2019 Reporting Framework Indexes</a></li>\r\n<li><a href=\&quot;/content/dam/company/us/en/reports/pdf/coca-cola-world-without-waste-report-2019.pdf\&quot;>2019 World Without Waste Report</a></li>\r\n<li><a href=\&quot;/content/dam/company/us/en/reports/pdf/water-progress-update-2019.pdf\&quot;>2019 Water Progress Update</a></li>\r\n<li><a href=\&quot;/content/dam/company/us/en/reports/pdf/2019-Water-Replenishment-Projects.pdf\&quot;>2019 Water Replenishment Projects</a></li>\r\n<li><a href=\&quot;/content/dam/company/us/en/reports/pdf/sustainable-ingredients-policy.pdf\&quot;>2019 Sustainable Ingredients Policy</a></li>\r\n<li><a href=\&quot;https://www.coca-colacompany.com/content/dam/company/us/en/policies/pdf/sustainability/2019-cdp-climate-change-response.pdf\&quot;>2019 CDP Climate Change Response</a></li>\r\n<li><a href=\&quot;/content/dam/company/us/en/policies/pdf/sustainability/2019-cdp-water-response.pdf\&quot;>2019 CDP Water Response</a></li>\r\n</ul>\r\n<p>&amp;nbsp;</p>\r\n<ul>\r\n<li><a href=\&quot;/content/dam/company/us/en/policies/pdf/sustainability/coca-cola-business-and-sustainability-report-2018.pdf\&quot;>2018 Business &amp;amp; Sustainability Report</a></li>\r\n<li><a href=\&quot;/content/dam/company/us/en/reports/pdf/world-without-waste-report-2018.pdf\&quot;>2018 World Without Waste Progress Report</a></li>\r\n<li><a href=\&quot;/content/dam/company/us/en/policies/pdf/sustainability/coca-cola-business-and-sustainability-report-2018.pdf#page=26\&quot;>2018 Water Stewardship Progress Report</a></li>\r\n<li><a href=\&quot;/content/dam/company/us/en/policies/pdf/sustainability/2018-climate-report.pdf\&quot;>2018 Climate Report</a></li>\r\n<li><a href=\&quot;https://www.coca-colacompany.com/content/dam/company/us/en/policies/pdf/sustainability/2018-cdp-climate-change-response.pdf\&quot; target=\&quot;_blank\&quot; rel=\&quot;noopener noreferrer\&quot;>2018 CDP Climate Change Response</a></li>\r\n<li><a href=\&quot;/content/dam/company/us/en/policies/pdf/sustainability/2018-cdp-water-response.pdf\&quot;>2018 CDP Water Response</a></li>\r\n<li><a href=\&quot;/content/dam/company/us/en/policies/pdf/sustainability/gri-index-2018.pdf\&quot;>2018 GRI Index</a></li>\r\n</ul>\r\n<p>&amp;nbsp;</p>\r\n<ul>\r\n<li><a href=\&quot;/content/dam/company/us/en/policies/pdf/sustainability/2017-sustainability-report-the-coca-cola-company.pdf\&quot;>2017 Sustainability Report</a></li>\r\n</ul>\r\n<p>&amp;nbsp;</p>\r\n<ul>\r\n<li><a href=\&quot;/content/dam/company/us/en/policies/pdf/sustainability/2016-sustainability-report-the-coca-cola-company.pdf\&quot;>2016 Sustainability Report</a></li>\r\n</ul>\r\n<p>&amp;nbsp;</p>\r\n<ul>\r\n<li><a href=\&quot;/content/company/us/en/policies-and-practices/principles-for-sustainable-agriculture.html\&quot;>Principles for Sustainable Agriculture</a><br>\r\n</li>\r\n<li><a href=\&quot;/content/company/us/en/policies-and-practices/animal-health-and-welfare-guiding-principles.html\&quot;>Animal Health and Welfare Guiding Principles</a></li>\r\n<li><a href=\&quot;/content/company/us/en/policies-and-practices/occupational-health-and-safety-policy.html\&quot;>Occupational Health &amp;amp; Safety Policy</a></li>\r\n<li><a href=\&quot;/content/company/us/en/policies-and-practices/quality-and-food-safety-policy.html\&quot;>Quality &amp;amp; Food Safety Policy</a></li>\r\n<li><a href=\&quot;/content/company/us/en/policies-and-practices/environmental-policy.html\&quot;>Environmental Policy</a></li>\r\n<li><a href=\&quot;/content/company/us/en/policies-and-practices/coca-cola-commitment-to-the-un-global-compact.html\&quot;>Coca-Cola Commitment to the UN Global Compact</a></li>\r\n<li><a href=\&quot;/content/dam/company/us/en/policies/pdf/sustainability/2024-Sustainable-Commerical-Paper-Program-Indication-Report.pdf\&quot; target=\&quot;_blank\&quot; rel=\&quot;noopener noreferrer\&quot;>2024 Sustainable Commercial Paper Program Indication Report</a></li>\r\n</ul>\r\n&quot;}}" id="text-a06b92da0a" class="cmp-text" bis_skin_checked="1">
    <ul><li><a href="/content/dam/company/us/en/reports/2023-environmental-update/2023-environmental-update.pdf">2023 Environmental Update</a></li></ul>
<div bis_skin_checked="1">&nbsp;</div>
<ul><li><a href="https://www.coca-colacompany.com/content/dam/company/us/en/policies/pdf/sustainability/2023-cdp-climate-change-response.pdf" target="_blank" rel="noopener noreferrer">2023 CDP Climate Change Response</a></li><li><a href="/content/dam/company/us/en/policies/pdf/sustainability/2023-CDP-Forests-Response.pdf">2023 CDP Forests Response</a></li><li><u><a href="/content/dam/company/us/en/policies/pdf/sustainability/2023-CDP-Water-Response.pdf">2023 CDP Water Response</a></u></li></ul>
<p>&nbsp;</p>
<ul><li><a href="/content/dam/company/us/en/reports/coca-cola-business-sustainability-report-2022.pdf">2022 Business &amp; Sustainability Report</a><br>
</li><li><a href="/content/dam/company/us/en/reports/2022-business-report/coca-cola-business-and-sustainability-report-2022-highlights.pdf">2022 Business &amp; Sustainability Report Highlights</a></li><li><a href="/content/company/us/en/reports/2022-business-report/2022-reporting-framework-indexes.pdf">2022 Reporting Frameworks &amp; SDGs</a></li><li><a href="https://www.coca-colacompany.com/content/dam/company/us/en/policies/pdf/sustainability/2022-cdp-climate-change-response.pdf">2022 CDP Climate Change Response</a></li><li><a href="/content/dam/company/us/en/policies/pdf/sustainability/2022-cdp-forests-response.pdf">2022 CDP Forests Response</a><br>
</li><li><a href="/content/dam/company/us/en/policies/pdf/sustainability/2022-cdp-water-response.pdf">2022 CDP Water Response</a></li></ul>
<p>&nbsp;</p>
<ul><li><a href="/content/dam/company/us/en/reports/coca-cola-business-environmental-social-governance-report-2021.pdf">2021 Business &amp; Environmental, Social and Governance Report</a></li><li><a href="/content/dam/company/us/en/reports/coca-cola-business-environmental-social-governance-report-2021-highlights.pdf">2021 Business &amp; Environmental, Social and Governance Report Highlights</a></li><li><a href="/content/dam/company/us/en/policies/pdf/sustainability/2021-reporting-framework-indexes.pdf">2021 Reporting Frameworks &amp; SDGs</a><br>
</li><li><a href="/reports/world-without-waste-2021">2021 World Without Waste Report</a></li><li><a href="/content/dam/company/us/en/policies/pdf/sustainability/2021-tccc-carbon-accounting-manual.pdf">2021 Carbon Accounting Manual</a></li><li><a href="https://www.coca-colacompany.com/content/dam/company/us/en/policies/pdf/sustainability/2021-cdp-climate-change-response.pdf" target="_blank" rel="noopener noreferrer">2021 CDP Climate Change Response</a></li><li><a href="/content/dam/company/us/en/policies/pdf/sustainability/2021-cdp-forests-response.pdf">2021 CDP Forests Response</a></li><li><a href="/content/dam/company/us/en/policies/pdf/sustainability/2021-cdp-water-response.pdf">2021 CDP Water Response</a></li></ul>
<p>&nbsp;</p>
<ul><li><a href="/reports/business-environmental-social-governance-report-2020">2020 Business &amp; Environmental, Social and Governance Report</a><br>
</li><li><a href="/content/dam/company/us/en/reports/coca-cola-business-environmental-social-governance-report-2020-highlights.pdf">2020 Business &amp; Environmental, Social and Governance Report Highlights</a></li><li><a href="/content/dam/company/us/en/policies/pdf/sustainability/2020-reporting-framework-indexes.pdf">2020 Reporting Frameworks &amp; SDGs</a></li><li><a href="/reports/world-without-waste-2020">2020 World Without Waste Report</a></li><li><a href="/content/dam/company/us/en/reports/pdf/coca-cola-5by20-report-march-2021.pdf">2020 5by20 Report</a></li><li><a href="https://www.coca-colacompany.com/content/dam/company/us/en/policies/pdf/sustainability/2020-cdp-climate-change-response.pdf" target="_blank" rel="noopener noreferrer">2020 CDP Climate Change Response</a></li><li><a href="/content/dam/company/us/en/policies/pdf/sustainability/2020-cdp-water-response.pdf">2020 CDP Water Response</a></li></ul>
<p>&nbsp;</p>
<ul><li><a href="/content/dam/company/us/en/reports/coca-cola-business-and-sustainability-report-2019.pdf">2019 Business &amp; Sustainability Report</a></li><li><a href="/content/dam/company/us/en/reports/coca-cola-business-and-sustainability-report-highlights-2019.pdf">2019 Business &amp; Sustainability Report Highlights</a></li><li><a href="/content/dam/company/us/en/reports/pdf/2019-reporting-framework-indexes.pdf">2019 Reporting Framework Indexes</a></li><li><a href="/content/dam/company/us/en/reports/pdf/coca-cola-world-without-waste-report-2019.pdf">2019 World Without Waste Report</a></li><li><a href="/content/dam/company/us/en/reports/pdf/water-progress-update-2019.pdf">2019 Water Progress Update</a></li><li><a href="/content/dam/company/us/en/reports/pdf/2019-Water-Replenishment-Projects.pdf">2019 Water Replenishment Projects</a></li><li><a href="/content/dam/company/us/en/reports/pdf/sustainable-ingredients-policy.pdf">2019 Sustainable Ingredients Policy</a></li><li><a href="https://www.coca-colacompany.com/content/dam/company/us/en/policies/pdf/sustainability/2019-cdp-climate-change-response.pdf">2019 CDP Climate Change Response</a></li><li><a href="/content/dam/company/us/en/policies/pdf/sustainability/2019-cdp-water-response.pdf">2019 CDP Water Response</a></li></ul>
<p>&nbsp;</p>
<ul><li><a href="/content/dam/company/us/en/policies/pdf/sustainability/coca-cola-business-and-sustainability-report-2018.pdf">2018 Business &amp; Sustainability Report</a></li><li><a href="/content/dam/company/us/en/reports/pdf/world-without-waste-report-2018.pdf">2018 World Without Waste Progress Report</a></li><li><a href="/content/dam/company/us/en/policies/pdf/sustainability/coca-cola-business-and-sustainability-report-2018.pdf#page=26">2018 Water Stewardship Progress Report</a></li><li><a href="/content/dam/company/us/en/policies/pdf/sustainability/2018-climate-report.pdf">2018 Climate Report</a></li><li><a href="https://www.coca-colacompany.com/content/dam/company/us/en/policies/pdf/sustainability/2018-cdp-climate-change-response.pdf" target="_blank" rel="noopener noreferrer">2018 CDP Climate Change Response</a></li><li><a href="/content/dam/company/us/en/policies/pdf/sustainability/2018-cdp-water-response.pdf">2018 CDP Water Response</a></li><li><a href="/content/dam/company/us/en/policies/pdf/sustainability/gri-index-2018.pdf">2018 GRI Index</a></li></ul>
<p>&nbsp;</p>
<ul><li><a href="/content/dam/company/us/en/policies/pdf/sustainability/2017-sustainability-report-the-coca-cola-company.pdf">2017 Sustainability Report</a></li></ul>
<p>&nbsp;</p>
<ul><li><a href="/content/dam/company/us/en/policies/pdf/sustainability/2016-sustainability-report-the-coca-cola-company.pdf">2016 Sustainability Report</a></li></ul>
<p>&nbsp;</p>
<ul><li><a href="/policies-and-practices/principles-for-sustainable-agriculture">Principles for Sustainable Agriculture</a><br>
</li><li><a href="/policies-and-practices/animal-health-and-welfare-guiding-principles">Animal Health and Welfare Guiding Principles</a></li><li><a href="/policies-and-practices/occupational-health-and-safety-policy">Occupational Health &amp; Safety Policy</a></li><li><a href="/policies-and-practices/quality-and-food-safety-policy">Quality &amp; Food Safety Policy</a></li><li><a href="/policies-and-practices/environmental-policy">Environmental Policy</a></li><li><a href="/policies-and-practices/coca-cola-commitment-to-the-un-global-compact">Coca‑Cola Commitment to the UN Global Compact</a></li><li><a href="/content/dam/company/us/en/policies/pdf/sustainability/2024-Sustainable-Commerical-Paper-Program-Indication-Report.pdf" target="_blank" rel="noopener noreferrer">2024 Sustainable Commercial Paper Program Indication Report</a></li></ul>

</div>

    

</div>

        
    </div>

</div>
</div>
    </div>
<div class="cmp-accordion__item" data-cmp-hook-accordion="item" data-cmp-data-layer="{&quot;accordion-574708b73f-item-dd25c9f5f6&quot;:{&quot;@type&quot;:&quot;cep/components/accordion/item&quot;,&quot;repo:modifyDate&quot;:&quot;2023-04-20T09:31:04Z&quot;,&quot;dc:title&quot;:&quot;Legal &amp; Practices&quot;}}" id="accordion-574708b73f-item-dd25c9f5f6" data-cmp-expanded="" bis_skin_checked="1">
        <h3 class="cmp-accordion__header">
            <button id="accordion-574708b73f-item-dd25c9f5f6-button" class="cmp-accordion__button cmp-accordion__button--expanded" type="button" aria-controls="accordion-574708b73f-item-dd25c9f5f6-panel" data-cmp-hook-accordion="button" aria-expanded="true">
                <span class="cmp-accordion__title">Legal &amp; Practices</span>
                <span class="cmp-accordion__icon"></span>
            </button>
        </h3>
        <div data-cmp-hook-accordion="panel" id="accordion-574708b73f-item-dd25c9f5f6-panel" class="cmp-accordion__panel cmp-accordion__panel--expanded" role="region" aria-labelledby="accordion-574708b73f-item-dd25c9f5f6-button" aria-hidden="false" bis_skin_checked="1"><div class="container responsivegrid" bis_skin_checked="1">

    
    
    
    
    <div id="container-dd25c9f5f6" class="cmp-container" bis_skin_checked="1">

        

        
        <div class="text" bis_skin_checked="1">
<div data-cmp-data-layer="{&quot;text-a3c334d275&quot;:{&quot;@type&quot;:&quot;cep/components/text&quot;,&quot;repo:modifyDate&quot;:&quot;2023-04-20T11:48:11Z&quot;,&quot;xdm:text&quot;:&quot;<ul>\r\n<li><a href=\&quot;/content/company/us/en/policies-and-practices/code-of-business-conduct.html\&quot;>Code of Business Conduct</a></li>\r\n<li><a href=\&quot;/content/company/us/en/policies-and-practices/anti-bribery-policy.html\&quot;>Anti-Bribery Policy</a></li>\r\n<li><a href=\&quot;/content/company/us/en/policies-and-practices/reporting-ethics-concerns.html\&quot;>Reporting Ethics Concerns</a></li>\r\n<li><a href=\&quot;/content/company/us/en/policies-and-practices/responsible-marketing-policy.html\&quot;>Responsible Marketing Policy</a></li>\r\n<li><a href=\&quot;/content/company/us/en/policies-and-practices/responsible-digital-media-principles.html\&quot;>Digital Media Principles</a></li>\r\n<li><a href=\&quot;/content/company/us/en/policies-and-practices/marketing-responsibly-in-the-united-states.html\&quot;>Marketing Responsibly in the U.S.</a></li>\r\n<li><a href=\&quot;/content/company/us/en/policies-and-practices/global-school-beverage-policy.html\&quot;>Global School Beverage Policy</a></li>\r\n<li><a href=\&quot;/content/company/us/en/policies-and-practices/responsible-alcohol-marketing-policy.html\&quot;>Responsible Alcohol Marketing Policy</a></li>\r\n<li><a href=\&quot;/content/company/us/en/policies-and-practices/hateful-activity-policy.html\&quot;>Hateful Activity Policy</a></li>\r\n<li><a href=\&quot;/content/company/us/en/policies-and-practices/dmca-request.html\&quot;>DMCA Requests</a></li>\r\n<li><a href=\&quot;/content/company/us/en/policies-and-practices/prohibition-on-cartel-activity.html\&quot;>Prohibition on Cartel Activity</a></li>\r\n<li><a href=\&quot;/content/dam/company/us/en/reports/The-Coca-Cola-Company-Alcohol-Social-Media-Community-Guidelines.pdf\&quot;>Alcohol Social Media Community Guidelines</a></li>\r\n</ul>\r\n&quot;}}" id="text-a3c334d275" class="cmp-text" bis_skin_checked="1">
    <ul><li><a href="/policies-and-practices/code-of-business-conduct">Code of Business Conduct</a></li><li><a href="/policies-and-practices/anti-bribery-policy">Anti-Bribery Policy</a></li><li><a href="/policies-and-practices/reporting-ethics-concerns">Reporting Ethics Concerns</a></li><li><a href="/policies-and-practices/responsible-marketing-policy">Responsible Marketing Policy</a></li><li><a href="/policies-and-practices/responsible-digital-media-principles">Digital Media Principles</a></li><li><a href="/policies-and-practices/marketing-responsibly-in-the-united-states">Marketing Responsibly in the U.S.</a></li><li><a href="/policies-and-practices/global-school-beverage-policy">Global School Beverage Policy</a></li><li><a href="/policies-and-practices/responsible-alcohol-marketing-policy">Responsible Alcohol Marketing Policy</a></li><li><a href="/policies-and-practices/hateful-activity-policy">Hateful Activity Policy</a></li><li><a href="/policies-and-practices/dmca-request">DMCA Requests</a></li><li><a href="/policies-and-practices/prohibition-on-cartel-activity">Prohibition on Cartel Activity</a></li><li><a href="/content/dam/company/us/en/reports/The-Coca-Cola-Company-Alcohol-Social-Media-Community-Guidelines.pdf">Alcohol Social Media Community Guidelines</a></li></ul>

</div>

    

</div>

        
    </div>

</div>
</div>
    </div>
<div class="cmp-accordion__item" data-cmp-hook-accordion="item" data-cmp-data-layer="{&quot;accordion-574708b73f-item-189ea892db&quot;:{&quot;@type&quot;:&quot;cep/components/accordion/item&quot;,&quot;dc:title&quot;:&quot;Shareowner Services&quot;}}" id="accordion-574708b73f-item-189ea892db" data-cmp-expanded="" bis_skin_checked="1">
        <h3 class="cmp-accordion__header">
            <button id="accordion-574708b73f-item-189ea892db-button" class="cmp-accordion__button cmp-accordion__button--expanded" type="button" aria-controls="accordion-574708b73f-item-189ea892db-panel" data-cmp-hook-accordion="button" aria-expanded="true">
                <span class="cmp-accordion__title">Shareowner Services</span>
                <span class="cmp-accordion__icon"></span>
            </button>
        </h3>
        <div data-cmp-hook-accordion="panel" id="accordion-574708b73f-item-189ea892db-panel" class="cmp-accordion__panel cmp-accordion__panel--expanded" role="region" aria-labelledby="accordion-574708b73f-item-189ea892db-button" aria-hidden="false" bis_skin_checked="1"><div class="container responsivegrid" bis_skin_checked="1">

    
    <div id="container-189ea892db" class="cmp-container" bis_skin_checked="1">
        


<div class="aem-Grid aem-Grid--12 aem-Grid--default--12 " bis_skin_checked="1">
    
    <div class="text aem-GridColumn aem-GridColumn--default--12" bis_skin_checked="1">
<div data-cmp-data-layer="{&quot;text-45806e6d8f&quot;:{&quot;@type&quot;:&quot;cep/components/text&quot;,&quot;repo:modifyDate&quot;:&quot;2025-01-29T15:23:01Z&quot;,&quot;xdm:text&quot;:&quot;<ul>\r\n<li><a href=\&quot;https://investors.coca-colacompany.com/shareowners\&quot;>Shareowners Main Page</a></li>\r\n</ul>\r\n&quot;}}" id="text-45806e6d8f" class="cmp-text" bis_skin_checked="1">
    <ul><li><a href="https://investors.coca-colacompany.com/shareowners">Shareowners Main Page</a></li></ul>

</div>

    

</div>

    
</div>

    </div>

    
</div>
</div>
    </div>
<div class="cmp-accordion__item" data-cmp-hook-accordion="item" data-cmp-data-layer="{&quot;accordion-574708b73f-item-bc70e195d5&quot;:{&quot;@type&quot;:&quot;cep/components/accordion/item&quot;,&quot;dc:title&quot;:&quot;Advocacy &amp; Political Engagement&quot;}}" id="accordion-574708b73f-item-bc70e195d5" data-cmp-expanded="" bis_skin_checked="1">
        <h3 class="cmp-accordion__header">
            <button id="accordion-574708b73f-item-bc70e195d5-button" class="cmp-accordion__button cmp-accordion__button--expanded" type="button" aria-controls="accordion-574708b73f-item-bc70e195d5-panel" data-cmp-hook-accordion="button" aria-expanded="true">
                <span class="cmp-accordion__title">Advocacy &amp; Political Engagement</span>
                <span class="cmp-accordion__icon"></span>
            </button>
        </h3>
        <div data-cmp-hook-accordion="panel" id="accordion-574708b73f-item-bc70e195d5-panel" class="cmp-accordion__panel cmp-accordion__panel--expanded" role="region" aria-labelledby="accordion-574708b73f-item-bc70e195d5-button" aria-hidden="false" bis_skin_checked="1"><div class="container responsivegrid" bis_skin_checked="1">

    
    <div id="container-bc70e195d5" class="cmp-container" bis_skin_checked="1">
        


<div class="aem-Grid aem-Grid--12 aem-Grid--default--12 " bis_skin_checked="1">
    
    <div class="text aem-GridColumn aem-GridColumn--default--12" bis_skin_checked="1">
<div data-cmp-data-layer="{&quot;text-d955937f1c&quot;:{&quot;@type&quot;:&quot;cep/components/text&quot;,&quot;repo:modifyDate&quot;:&quot;2025-01-29T15:29:41Z&quot;,&quot;xdm:text&quot;:&quot;<ul>\r\n<li><a href=\&quot;/content/company/us/en/policies-and-practices/public-policy-and-political-engagement.html\&quot;>Public Policy &amp;amp; Political Engagement</a></li>\r\n<li><a href=\&quot;/content/company/us/en/policies-and-practices/political-contributions.html\&quot;>Coca-Cola PAC &amp;amp; Corporate Political Contributions</a></li>\r\n<li><a href=\&quot;/content/company/us/en/policies-and-practices/lobbying-disclosure-reports.html\&quot;>Lobbying Disclosure Reports (LD-2 &amp;amp; LD-203)</a></li>\r\n</ul>\r\n&quot;}}" id="text-d955937f1c" class="cmp-text" bis_skin_checked="1">
    <ul><li><a href="/policies-and-practices/public-policy-and-political-engagement">Public Policy &amp; Political Engagement</a></li><li><a href="/policies-and-practices/political-contributions">Coca‑Cola PAC &amp; Corporate Political Contributions</a></li><li><a href="/policies-and-practices/lobbying-disclosure-reports">Lobbying Disclosure Reports (LD-2 &amp; LD-203)</a></li></ul>

</div>

    

</div>

    
</div>

    </div>

    
</div>
</div>
    </div>

    
</div>
</div>
<div class="accordion panelcontainer faq" bis_skin_checked="1">
<div id="accordion-8a8af91dd2" class="cmp-accordion" data-cmp-data-layer="{&quot;accordion-8a8af91dd2&quot;:{&quot;shownItems&quot;:[&quot;accordion-8a8af91dd2-item-1ba6e0c065&quot;,&quot;accordion-8a8af91dd2-item-032612c674&quot;,&quot;accordion-8a8af91dd2-item-2f47059882&quot;,&quot;accordion-8a8af91dd2-item-2f69f95f1a&quot;],&quot;@type&quot;:&quot;cep/components/accordion&quot;,&quot;repo:modifyDate&quot;:&quot;2023-04-20T13:43:07Z&quot;}}" data-placeholder-text="false" bis_skin_checked="1">
    <div class="cmp-accordion__item" data-cmp-hook-accordion="item" data-cmp-data-layer="{&quot;accordion-8a8af91dd2-item-1ba6e0c065&quot;:{&quot;@type&quot;:&quot;cep/components/accordion/item&quot;,&quot;repo:modifyDate&quot;:&quot;2023-04-20T09:32:32Z&quot;,&quot;dc:title&quot;:&quot;Human &amp; Workplace Rights&quot;}}" id="accordion-8a8af91dd2-item-1ba6e0c065" data-cmp-expanded="" bis_skin_checked="1">
        <h3 class="cmp-accordion__header">
            <button id="accordion-8a8af91dd2-item-1ba6e0c065-button" class="cmp-accordion__button cmp-accordion__button--expanded" type="button" aria-controls="accordion-8a8af91dd2-item-1ba6e0c065-panel" data-cmp-hook-accordion="button" aria-expanded="true">
                <span class="cmp-accordion__title">Human &amp; Workplace Rights</span>
                <span class="cmp-accordion__icon"></span>
            </button>
        </h3>
        <div data-cmp-hook-accordion="panel" id="accordion-8a8af91dd2-item-1ba6e0c065-panel" class="cmp-accordion__panel cmp-accordion__panel--expanded" role="region" aria-labelledby="accordion-8a8af91dd2-item-1ba6e0c065-button" aria-hidden="false" bis_skin_checked="1"><div class="container responsivegrid" bis_skin_checked="1">

    
    
    
    
    <div id="container-1ba6e0c065" class="cmp-container" bis_skin_checked="1">

        

        
        <div class="text" bis_skin_checked="1">
<div data-cmp-data-layer="{&quot;text-93cc2b8642&quot;:{&quot;@type&quot;:&quot;cep/components/text&quot;,&quot;repo:modifyDate&quot;:&quot;2025-01-29T15:23:55Z&quot;,&quot;xdm:text&quot;:&quot;<ul>\r\n<li><a href=\&quot;/content/dam/company/us/en/reports/2023-data-updates/2023-human-rights-update.pdf\&quot;>2023 Human Rights Update</a></li>\r\n<li><a href=\&quot;/content/dam/company/us/en/reports/2023-data-updates/2023-workplace-and-safety-update.pdf\&quot;>2023 Workplace and Safety Update</a></li>\r\n<li><a href=\&quot;/content/dam/company/us/en/policies/pdf/social/human-rights-overview-2022.pdf\&quot;>2022 Human Rights Overview</a></li>\r\n<li><a href=\&quot;/content/dam/company/us/en/reports/pdf/CocaCola_Global%20Human%20Rights%20Policy_Document_20240419_v9.15.pdf\&quot;>Global Human Rights Policy (English)</a></li>\r\n<li><a href=\&quot;/content/company/us/en/policies-and-practices/human-rights-policy-languages.html\&quot;>Global Human Rights Policy (Translations)</a>&amp;nbsp;&amp;nbsp;</li>\r\n<li><a href=\&quot;/content/dam/company/us/en/reports/pdf/2024-04%20-%20Coca-Cola%20-%20HRP%20poster%20-%20English%20-%20ONLINE%20-%20v2.4.pdf\&quot;>Human Rights Policy Poster (English)</a></li>\r\n<li><a href=\&quot;/content/company/us/en/policies-and-practices/human-rights-policy-posters.html\&quot;>Human Rights Policy Poster (Translations)</a></li>\r\n<li><a href=\&quot;/content/company/us/en/policies-and-practices/supplier-guiding-principles.html\&quot;>Supplier Guiding Principles</a></li>\r\n<li><a href=\&quot;/content/company/us/en/policies-and-practices/supplier-guiding-principles-languages.html\&quot;>Supplier Guiding Principles - Languages</a></li>\r\n<li><a href=\&quot;/content/company/us/en/policies-and-practices/supplier-code-of-business-conduct.html\&quot;>Supplier Code of Business Conduct</a></li>\r\n<li><a href=\&quot;/content/company/us/en/policies-and-practices/supplier-code-of-business-conduct-languages.html\&quot;>Supplier Code of Business Conduct - Languages</a></li>\r\n<li><a href=\&quot;/content/dam/company/us/en/policies/pdf/human-workplace-rights/addressing-global-issues/the-coca-cola-companys-human-rights-report.pdf\&quot;>Human Rights Report</a></li>\r\n<li><a href=\&quot;/content/company/us/en/policies-and-practices/human-and-workplace-rights-materials-for-employees.html\&quot;>Human &amp;amp; Workplace Rights Materials for Employees</a></li>\r\n<li><a href=\&quot;/content/company/us/en/policies-and-practices/safety-and-health.html\&quot;>Safety &amp;amp; Health</a></li>\r\n<li><a href=\&quot;/content/company/us/en/policies-and-practices/addressing-global-issues.html\&quot;>Addressing Global Issues</a></li>\r\n<li><a href=\&quot;/content/company/us/en/policies-and-practices/human-rights-engaging-stakeholders.html\&quot;>Human Rights - Engaging Stakeholders</a></li>\r\n<li><a href=\&quot;/content/company/us/en/policies-and-practices/california-transparency-in-supply-chain-act.html\&quot;>California Transparency in Supply Chain Act</a></li>\r\n<li><a href=\&quot;/content/company/us/en/policies-and-practices/sgp-guidance-documents.html\&quot;>SGP Guidance Documents</a></li>\r\n<li><a href=\&quot;/content/company/us/en/policies-and-practices/sgp-implementation-guide-languages.html\&quot;>SGP Guidance Documents - Languages</a></li>\r\n<li><a href=\&quot;/content/company/us/en/policies-and-practices/human-rights-self-assessment-checklists.html\&quot;>Human Rights Self Assessment</a></li>\r\n<li><a href=\&quot;/content/dam/company/us/en/policies/pdf/human-workplace-rights/human-rights-restructuring-guidelines/human-rights-restructuring-guidelines-2020-framework.pdf\&quot;>Human Rights Restructuring Guidelines</a></li>\r\n</ul>\r\n&quot;}}" id="text-93cc2b8642" class="cmp-text" bis_skin_checked="1">
    <ul><li><a href="/content/dam/company/us/en/reports/2023-data-updates/2023-human-rights-update.pdf">2023 Human Rights Update</a></li><li><a href="/content/dam/company/us/en/reports/2023-data-updates/2023-workplace-and-safety-update.pdf">2023 Workplace and Safety Update</a></li><li><a href="/content/dam/company/us/en/policies/pdf/social/human-rights-overview-2022.pdf">2022 Human Rights Overview</a></li><li><a href="/content/dam/company/us/en/reports/pdf/CocaCola_Global%20Human%20Rights%20Policy_Document_20240419_v9.15.pdf">Global Human Rights Policy (English)</a></li><li><a href="/policies-and-practices/human-rights-policy-languages">Global Human Rights Policy (Translations)</a>&nbsp;&nbsp;</li><li><a href="/content/dam/company/us/en/reports/pdf/2024-04%20-%20Coca-Cola%20-%20HRP%20poster%20-%20English%20-%20ONLINE%20-%20v2.4.pdf">Human Rights Policy Poster (English)</a></li><li><a href="/policies-and-practices/human-rights-policy-posters">Human Rights Policy Poster (Translations)</a></li><li><a href="/policies-and-practices/supplier-guiding-principles">Supplier Guiding Principles</a></li><li><a href="/policies-and-practices/supplier-guiding-principles-languages">Supplier Guiding Principles - Languages</a></li><li><a href="/policies-and-practices/supplier-code-of-business-conduct">Supplier Code of Business Conduct</a></li><li><a href="/policies-and-practices/supplier-code-of-business-conduct-languages">Supplier Code of Business Conduct - Languages</a></li><li><a href="/content/dam/company/us/en/policies/pdf/human-workplace-rights/addressing-global-issues/the-coca-cola-companys-human-rights-report.pdf">Human Rights Report</a></li><li><a href="/policies-and-practices/human-and-workplace-rights-materials-for-employees">Human &amp; Workplace Rights Materials for Employees</a></li><li><a href="/policies-and-practices/safety-and-health">Safety &amp; Health</a></li><li><a href="/policies-and-practices/addressing-global-issues">Addressing Global Issues</a></li><li><a href="/policies-and-practices/human-rights-engaging-stakeholders">Human Rights - Engaging Stakeholders</a></li><li><a href="/policies-and-practices/california-transparency-in-supply-chain-act">California Transparency in Supply Chain Act</a></li><li><a href="/policies-and-practices/sgp-guidance-documents">SGP Guidance Documents</a></li><li><a href="/policies-and-practices/sgp-implementation-guide-languages">SGP Guidance Documents - Languages</a></li><li><a href="/policies-and-practices/human-rights-self-assessment-checklists">Human Rights Self Assessment</a></li><li><a href="/content/dam/company/us/en/policies/pdf/human-workplace-rights/human-rights-restructuring-guidelines/human-rights-restructuring-guidelines-2020-framework.pdf">Human Rights Restructuring Guidelines</a></li></ul>

</div>

    

</div>

        
    </div>

</div>
</div>
    </div>
<div class="cmp-accordion__item" data-cmp-hook-accordion="item" data-cmp-data-layer="{&quot;accordion-8a8af91dd2-item-032612c674&quot;:{&quot;@type&quot;:&quot;cep/components/accordion/item&quot;,&quot;repo:modifyDate&quot;:&quot;2023-03-30T14:40:33Z&quot;,&quot;dc:title&quot;:&quot;Corporate Governance&quot;}}" id="accordion-8a8af91dd2-item-032612c674" data-cmp-expanded="" bis_skin_checked="1">
        <h3 class="cmp-accordion__header">
            <button id="accordion-8a8af91dd2-item-032612c674-button" class="cmp-accordion__button cmp-accordion__button--expanded" type="button" aria-controls="accordion-8a8af91dd2-item-032612c674-panel" data-cmp-hook-accordion="button" aria-expanded="true">
                <span class="cmp-accordion__title">Corporate Governance</span>
                <span class="cmp-accordion__icon"></span>
            </button>
        </h3>
        <div data-cmp-hook-accordion="panel" id="accordion-8a8af91dd2-item-032612c674-panel" class="cmp-accordion__panel cmp-accordion__panel--expanded" role="region" aria-labelledby="accordion-8a8af91dd2-item-032612c674-button" aria-hidden="false" bis_skin_checked="1"><div class="container responsivegrid" bis_skin_checked="1">

    
    
    
    
    <div id="container-032612c674" class="cmp-container" bis_skin_checked="1">

        

        
        <div class="text" bis_skin_checked="1">
<div data-cmp-data-layer="{&quot;text-e461cd6830&quot;:{&quot;@type&quot;:&quot;cep/components/text&quot;,&quot;repo:modifyDate&quot;:&quot;2025-01-29T15:26:36Z&quot;,&quot;xdm:text&quot;:&quot;<ul>\r\n<li><a href=\&quot;https://d1io3yog0oux5.cloudfront.net/_fd6a3e721c8feb0db6fa2e45899401ee/cocacolacompany/db/719/7231/file/Corporate+Governance+Guidelines+as+of+October+19%2C+2023.pdf\&quot;>Corporate Governance Guidelines</a></li>\r\n<li><a href=\&quot;/content/dam/company/us/en/policies/pdf/corporate-governance/code-of-business-conduct/coca-cola-coc-external.pdf\&quot;>Code of Business Conduct (English PDF)</a></li>\r\n<li><a href=\&quot;/content/company/us/en/policies-and-practices/supplier-code-of-business-conduct.html\&quot;>Code of Business Conduct</a></li>\r\n<li><a href=\&quot;https://d1io3yog0oux5.cloudfront.net/_fd6a3e721c8feb0db6fa2e45899401ee/cocacolacompany/db/719/7229/file/Binder1.pdf\&quot;>Certificate of Incorporation</a></li>\r\n<li><a href=\&quot;https://d1io3yog0oux5.cloudfront.net/_fd6a3e721c8feb0db6fa2e45899401ee/cocacolacompany/db/719/7230/file/2023-10-19+Amended+and+Restated+Bylaws+as+of+October+19%2C+2023+%28FINAL%29.pdf\&quot;>Company Bylaws</a></li>\r\n<li><a href=\&quot;/content/dam/company/us/en/policies/pdf/corporate-governance/code-of-business-conduct/directors-code-2018.pdf\&quot;>Code of Business Conduct for Non Employee Directors (English)</a></li>\r\n<li><a href=\&quot;/content/company/us/en/policies-and-practices/supplier-code-of-business-conduct-languages.html\&quot;>Code of Business Conduct (Other Languages)</a></li>\r\n</ul>\r\n&quot;}}" id="text-e461cd6830" class="cmp-text" bis_skin_checked="1">
    <ul><li><a href="https://d1io3yog0oux5.cloudfront.net/_fd6a3e721c8feb0db6fa2e45899401ee/cocacolacompany/db/719/7231/file/Corporate+Governance+Guidelines+as+of+October+19%2C+2023.pdf">Corporate Governance Guidelines</a></li><li><a href="/content/dam/company/us/en/policies/pdf/corporate-governance/code-of-business-conduct/coca-cola-coc-external.pdf">Code of Business Conduct (English PDF)</a></li><li><a href="/policies-and-practices/supplier-code-of-business-conduct">Code of Business Conduct</a></li><li><a href="https://d1io3yog0oux5.cloudfront.net/_fd6a3e721c8feb0db6fa2e45899401ee/cocacolacompany/db/719/7229/file/Binder1.pdf">Certificate of Incorporation</a></li><li><a href="https://d1io3yog0oux5.cloudfront.net/_fd6a3e721c8feb0db6fa2e45899401ee/cocacolacompany/db/719/7230/file/2023-10-19+Amended+and+Restated+Bylaws+as+of+October+19%2C+2023+%28FINAL%29.pdf">Company Bylaws</a></li><li><a href="/content/dam/company/us/en/policies/pdf/corporate-governance/code-of-business-conduct/directors-code-2018.pdf">Code of Business Conduct for Non Employee Directors (English)</a></li><li><a href="/policies-and-practices/supplier-code-of-business-conduct-languages">Code of Business Conduct (Other Languages)</a></li></ul>

</div>

    

</div>

        
    </div>

</div>
</div>
    </div>
<div class="cmp-accordion__item" data-cmp-hook-accordion="item" data-cmp-data-layer="{&quot;accordion-8a8af91dd2-item-2f47059882&quot;:{&quot;@type&quot;:&quot;cep/components/accordion/item&quot;,&quot;dc:title&quot;:&quot;The Coca-Cola Foundation&quot;}}" id="accordion-8a8af91dd2-item-2f47059882" data-cmp-expanded="" bis_skin_checked="1">
        <h3 class="cmp-accordion__header">
            <button id="accordion-8a8af91dd2-item-2f47059882-button" class="cmp-accordion__button cmp-accordion__button--expanded" type="button" aria-controls="accordion-8a8af91dd2-item-2f47059882-panel" data-cmp-hook-accordion="button" aria-expanded="true">
                <span class="cmp-accordion__title">The Coca‑Cola Foundation</span>
                <span class="cmp-accordion__icon"></span>
            </button>
        </h3>
        <div data-cmp-hook-accordion="panel" id="accordion-8a8af91dd2-item-2f47059882-panel" class="cmp-accordion__panel cmp-accordion__panel--expanded" role="region" aria-labelledby="accordion-8a8af91dd2-item-2f47059882-button" aria-hidden="false" bis_skin_checked="1"><div class="container responsivegrid" bis_skin_checked="1">

    
    <div id="container-2f47059882" class="cmp-container" bis_skin_checked="1">
        


<div class="aem-Grid aem-Grid--12 aem-Grid--default--12 " bis_skin_checked="1">
    
    <div class="text aem-GridColumn aem-GridColumn--default--12" bis_skin_checked="1">
<div data-cmp-data-layer="{&quot;text-024ca464ad&quot;:{&quot;@type&quot;:&quot;cep/components/text&quot;,&quot;repo:modifyDate&quot;:&quot;2025-01-29T15:29:02Z&quot;,&quot;xdm:text&quot;:&quot;<ul>\r\n<li><a href=\&quot;/content/dam/company/us/en/reports/2023-data-updates/2023-giving-back-update.pdf\&quot;>2023 Giving Back Update</a></li>\r\n<li><a href=\&quot;content/dam/company/us/en/reports/pdf/2023-TCCF-Tax-Return-Form-990.pdf\&quot;>2023 The Coca-Cola Foundation Form 990-PF Return</a></li>\r\n<li><a href=\&quot;/content/dam/company/us/en/policies/pdf/the-coca-cola-foundation/the-coca-cola%20foundation-inc-%202021-tax-return-copy-for-public-inspection.pdf\&quot;>2021 The Coca-Cola Foundation Form 990-PF Return</a></li>\r\n<li><a href=\&quot;/content/dam/company/us/en/policies/pdf/the-coca-cola-foundation/2020-CCF-Form-990-PF.pdf\&quot;>2020 Coca-Cola Foundation Form 990 PF Return</a></li>\r\n<li><a href=\&quot;/content/dam/company/us/en/policies/pdf/the-coca-cola-foundation/The-Coca-Cola-Foundation-Charitable-Giving-List-2019.pdf\&quot;>2019 Charitable Contributions Report</a></li>\r\n<li><a href=\&quot;/content/dam/company/us/en/policies/pdf/the-coca-cola-foundation/2018-charitable-contributions-report-amended.pdf\&quot;>2018 Charitable Contributions Report</a></li>\r\n<li><a href=\&quot;https://coca-cola.smartsimple.com/s_Login.jsp\&quot;>Application Form for Grants</a></li>\r\n</ul>\r\n&quot;}}" id="text-024ca464ad" class="cmp-text" bis_skin_checked="1">
    <ul><li><a href="/content/dam/company/us/en/reports/2023-data-updates/2023-giving-back-update.pdf">2023 Giving Back Update</a></li><li><a href="content/dam/company/us/en/reports/pdf/2023-TCCF-Tax-Return-Form-990.pdf">2023 The Coca‑Cola Foundation Form 990-PF Return</a></li><li><a href="/content/dam/company/us/en/policies/pdf/the-coca-cola-foundation/the-coca-cola%20foundation-inc-%202021-tax-return-copy-for-public-inspection.pdf">2021 The Coca‑Cola Foundation Form 990-PF Return</a></li><li><a href="/content/dam/company/us/en/policies/pdf/the-coca-cola-foundation/2020-CCF-Form-990-PF.pdf">2020 Coca‑Cola Foundation Form 990 PF Return</a></li><li><a href="/content/dam/company/us/en/policies/pdf/the-coca-cola-foundation/The-Coca-Cola-Foundation-Charitable-Giving-List-2019.pdf">2019 Charitable Contributions Report</a></li><li><a href="/content/dam/company/us/en/policies/pdf/the-coca-cola-foundation/2018-charitable-contributions-report-amended.pdf">2018 Charitable Contributions Report</a></li><li><a href="https://coca-cola.smartsimple.com/s_Login.jsp">Application Form for Grants</a></li></ul>

</div>

    

</div>

    
</div>

    </div>

    
</div>
</div>
    </div>
<div class="cmp-accordion__item" data-cmp-hook-accordion="item" data-cmp-data-layer="{&quot;accordion-8a8af91dd2-item-2f69f95f1a&quot;:{&quot;@type&quot;:&quot;cep/components/accordion/item&quot;,&quot;dc:title&quot;:&quot;Supplier Requirements&quot;}}" id="accordion-8a8af91dd2-item-2f69f95f1a" data-cmp-expanded="" bis_skin_checked="1">
        <h3 class="cmp-accordion__header">
            <button id="accordion-8a8af91dd2-item-2f69f95f1a-button" class="cmp-accordion__button cmp-accordion__button--expanded" type="button" aria-controls="accordion-8a8af91dd2-item-2f69f95f1a-panel" data-cmp-hook-accordion="button" aria-expanded="true">
                <span class="cmp-accordion__title">Supplier Requirements</span>
                <span class="cmp-accordion__icon"></span>
            </button>
        </h3>
        <div data-cmp-hook-accordion="panel" id="accordion-8a8af91dd2-item-2f69f95f1a-panel" class="cmp-accordion__panel cmp-accordion__panel--expanded" role="region" aria-labelledby="accordion-8a8af91dd2-item-2f69f95f1a-button" aria-hidden="false" bis_skin_checked="1"><div class="container responsivegrid" bis_skin_checked="1">

    
    <div id="container-2f69f95f1a" class="cmp-container" bis_skin_checked="1">
        


<div class="aem-Grid aem-Grid--12 aem-Grid--default--12 " bis_skin_checked="1">
    
    <div class="text aem-GridColumn aem-GridColumn--default--12" bis_skin_checked="1">
<div data-cmp-data-layer="{&quot;text-63e9822116&quot;:{&quot;@type&quot;:&quot;cep/components/text&quot;,&quot;repo:modifyDate&quot;:&quot;2025-01-29T17:42:45Z&quot;,&quot;xdm:text&quot;:&quot;<ul>\r\n<li><a href=\&quot;https://tccc.starssmp.com/\&quot;>Become a Supplier</a></li>\r\n<li><a href=\&quot;/content/company/us/en/policies-and-practices/supplier-requirements.html\&quot;>Supplier Requirements</a></li>\r\n<li><a href=\&quot;/content/dam/company/us/en/policies/pdf/supplier-requirements/principles-for-sustainable-agriculture-supplier-guide.pdf\&quot;>Principles for Sustainable Agriculture Supplier Guide</a></li>\r\n<li><a href=\&quot;/content/company/us/en/policies-and-practices/patent-license-for-suppliers.html\&quot;>Patent License Terms for Suppliers</a></li>\r\n<li><a href=\&quot;/content/dam/company/us/en/policies/pdf/legal-and-practices/artwork-labeling-and-intellectual-property.pdf\&quot;>Artwork, Labeling &amp;amp; Intellectual Property</a></li>\r\n<li><a href=\&quot;/content/dam/company/us/en/policies/pdf/legal-and-practices/KORE-General-Supplier-Requirements-General.pdf\&quot;>General Supplier Requirements [KORE]</a></li>\r\n<li><a href=\&quot;/content/dam/company/us/en/policies/pdf/legal-and-practices/kore-ingredient-supplier-requirements.pdf\&quot;>Ingredient Supplier Requirements [KORE]</a></li>\r\n<li><a href=\&quot;/content/dam/company/us/en/policies/pdf/legal-and-practices/KORE-Ingredient-Supplier-Requirements-Pre-Pack.pdf\&quot;>Ingredient – Pre-Pack – Supplier Requirements [KORE]</a></li>\r\n<li><a href=\&quot;/content/dam/company/us/en/policies/pdf/legal-and-practices/KORE-Ingredient-Supplier-Requirements-Food-Allergen-and-Sensitivity-Control.pdf\&quot;>Ingredient – Food Allergen Sensitivity - Supplier Requirements [KORE]</a></li>\r\n<li><a href=\&quot;/content/company/us/en/policies-and-practices/global-purchase-order-terms-and-conditions.html\&quot;>Global Purchase Order Terms and Conditions</a></li>\r\n<li><a href=\&quot;/content/dam/company/us/en/policies/pdf/legal-and-practices/global-food-allergen-and-sensitivity-template.pdf\&quot;>Global Food Allergen and Sensitivity Template</a></li>\r\n<li><a href=\&quot;/content/dam/company/us/en/policies/pdf/supplier-requirements/The%20Coca-Cola%20Company%20Supplier%20Invoicing%20Guide_version%20Nov.%202024.pdf\&quot;>Supplier Invoicing Guide</a></li>\r\n</ul>\r\n&quot;}}" id="text-63e9822116" class="cmp-text" bis_skin_checked="1">
    <ul><li><a href="https://tccc.starssmp.com/">Become a Supplier</a></li><li><a href="/policies-and-practices/supplier-requirements">Supplier Requirements</a></li><li><a href="/content/dam/company/us/en/policies/pdf/supplier-requirements/principles-for-sustainable-agriculture-supplier-guide.pdf">Principles for Sustainable Agriculture Supplier Guide</a></li><li><a href="/policies-and-practices/patent-license-for-suppliers">Patent License Terms for Suppliers</a></li><li><a href="/content/dam/company/us/en/policies/pdf/legal-and-practices/artwork-labeling-and-intellectual-property.pdf">Artwork, Labeling &amp; Intellectual Property</a></li><li><a href="/content/dam/company/us/en/policies/pdf/legal-and-practices/KORE-General-Supplier-Requirements-General.pdf">General Supplier Requirements [KORE]</a></li><li><a href="/content/dam/company/us/en/policies/pdf/legal-and-practices/kore-ingredient-supplier-requirements.pdf">Ingredient Supplier Requirements [KORE]</a></li><li><a href="/content/dam/company/us/en/policies/pdf/legal-and-practices/KORE-Ingredient-Supplier-Requirements-Pre-Pack.pdf">Ingredient – Pre-Pack – Supplier Requirements [KORE]</a></li><li><a href="/content/dam/company/us/en/policies/pdf/legal-and-practices/KORE-Ingredient-Supplier-Requirements-Food-Allergen-and-Sensitivity-Control.pdf">Ingredient – Food Allergen Sensitivity - Supplier Requirements [KORE]</a></li><li><a href="/policies-and-practices/global-purchase-order-terms-and-conditions">Global Purchase Order Terms and Conditions</a></li><li><a href="/content/dam/company/us/en/policies/pdf/legal-and-practices/global-food-allergen-and-sensitivity-template.pdf">Global Food Allergen and Sensitivity Template</a></li><li><a href="/content/dam/company/us/en/policies/pdf/supplier-requirements/The%20Coca-Cola%20Company%20Supplier%20Invoicing%20Guide_version%20Nov.%202024.pdf">Supplier Invoicing Guide</a></li></ul>

</div>

    

</div>

    
</div>

    </div>

    
</div>
</div>
    </div>

    
</div>
</div>

        
    </div>'''
# print(a)
