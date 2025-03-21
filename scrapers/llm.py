import os
from mistralai import Mistral


def llm(html):

    api_key = os.getenv('API_KEY')
    model = "mistral-large-latest"

    client = Mistral(api_key=api_key)

    chat_response = client.chat.complete(
        model= model,
        messages = [
            {
                "role": "system",
                "content": '''You are a extraction system that can provide event name, date, and the associated files from a raw html content into a json object. You will only respond with a JSON object with the event name, date, and files (this will be a list of files where applicalble).
                            here are some examples:

                            <div class="presentations-wrapper" bis_skin_checked="1"><div class="presentations-date-title" bis_skin_checked="1"><div class="presentations-title" bis_skin_checked="1">2024 Full-year results</div></div><div class="presentations-all-types-date" bis_skin_checked="1"><div class="presentations-all-types" bis_skin_checked="1"><a href="/sites/default/files/2025-02/full-year-results-investor-presentation-2024.pdf" target="_blank" class="media-file-info" data-once="ln_datalayer_outbound_link">Presentation <span class="media">3MB</span> <span class="ext"></span></a>  <a href="/sites/default/files/2025-02/full-year-results-2024-prepared-remarks.pdf" target="_blank" class="media-file-info" data-once="ln_datalayer_outbound_link">Transcript <span class="media">277KB</span> <span class="ext"></span></a>   <a href="/media/mediaeventscalendar/allevents/2024-full-year-results" target="_self" rel="noopener">Event page</a> </div><div class="presentations-date" bis_skin_checked="1"><time datetime="2025-02-13T07:00:00+01:00">Feb 13, 2025</time>
                            </div> </div></div>


                            from this, the extracted information is: 
                            {
                                event name: 2024 Full-year results
                                date: 2025/02/13
                                urls: [/sites/default/files/2025-02/full-year-results-2024-prepared-remarks.pdf, /media/mediaeventscalendar/allevents/2024-full-year-results]
                            }

                            Prompt:
                            <div class="presentations-wrapper" bis_skin_checked="1"><div class="presentations-date-title" bis_skin_checked="1"><div class="presentations-title" bis_skin_checked="1">Q&amp;A - Coffee &amp; PetCare - Capital Markets Day 2024</div></div><div class="presentations-all-types-date" bis_skin_checked="1"><div class="presentations-all-types" bis_skin_checked="1">   <a href="https://youtu.be/T_UY42DdE3I" target="_blank" class="media-file-info" data-once="ln_datalayer_outbound_link">Video <span class="ext"></span></a>  <a href="/media/mediaeventscalendar/allevents/2024-capital-markets-day" target="_self" rel="noopener">event</a> </div><div class="presentations-date" bis_skin_checked="1"><time datetime="2024-11-19T13:00:00+01:00">Nov 19, 2024</time>
                            </div> </div></div>

                            {
                                event name: Q&A - Coffee & PetCare - Capital Markets Day 2024
                                date: 2024/11/19
                                urls: [https://youtu.be/T_UY42DdE3I, /media/mediaeventscalendar/allevents/2024-capital-markets-day]
                            }


                            <div class="presentations-wrapper" bis_skin_checked="1"><div class="presentations-date-title" bis_skin_checked="1"><div class="presentations-title" bis_skin_checked="1">CEO, Laurent Freixe - Capital Markets Day 2024</div></div><div class="presentations-all-types-date" bis_skin_checked="1"><div class="presentations-all-types" bis_skin_checked="1"><a href="/sites/default/files/2024-11/capital-markets-day-2024-ceo.pdf" target="_blank" class="media-file-info" data-once="ln_datalayer_outbound_link">Presentation <span class="media">2MB</span> <span class="ext"></span></a>  <a href="/sites/default/files/2024-11/capital-markets-day-2024-transcript-ceo.pdf" target="_blank" class="media-file-info" data-once="ln_datalayer_outbound_link">Transcript <span class="media">262KB</span> <span class="ext"></span></a> <a href="https://youtu.be/cVWr1ysMOoo" target="_blank" class="media-file-info" data-once="ln_datalayer_outbound_link">Video <span class="ext"></span></a>  <a href="/media/mediaeventscalendar/allevents/2024-capital-markets-day" target="_self" rel="noopener">event page</a> </div><div class="presentations-date" bis_skin_checked="1"><time datetime="2024-11-19T08:15:00+01:00">Nov 19, 2024</time>
                            </div> </div></div>

                            {
                                event name: CEO, Laurent Freixe - Capital Markets Day 2024
                                date: 2024/11/19
                                urls: [/sites/default/files/2024-11/capital-markets-day-2024-ceo.pdf, /sites/default/files/2024-11/capital-markets-day-2024-transcript-ceo.pdf, https://youtu.be/cVWr1ysMOoo, /media/mediaeventscalendar/allevents/2024-capital-markets-day"] 
                            }

                            <a id="nv-teaser-bb36c49de7" class="cmp-teaser     " data-title-style="dynamic" href="#/webinar/4821105" target="_blank"><div class="nv-teaser--holder" bis_skin_checked="1"><div class="cmp-teaser__image" data-type="renditionUpload" data-altvaluefromdam="true" bis_skin_checked="1"><div data-cmp-lazy="" data-cmp-lazythreshold="300" data-cmp-src="/content/nvidiaGDC/zz/en_ZZ/testing/testdata/_jcr_content/root/responsivegrid/nv_container_170217500/nv_teaser.coreimg.100{.width}.png/1697602993046/nvidialogo.png" data-cmp-widths="190,410,630,850,1070,1290" class="cmp-image" data-cmp-type="renditionUpload" bis_skin_checked="1"><img class="cmp-image__image" data-cmp-hook-image="image" data-analytics="nv-image-bb36c49de7" src="https://orion.akamaized.net/event/48/21/10/5/rt/1/slide/slide/1_581D9DCCC9EFE8D87D9FE64C8BCD68CD.jpg" alt="Accelerate Your AI Development With NVIDIA NIM Microservices" title="Accelerate Your AI Development With NVIDIA NIM Microservices" style="max-height: 200px;"></div></div></div><div class="general-container-text h--smallest css-6sx646" bis_skin_checked="1"><div class="text-left lap-text-left tab-text-left mob-text-left" bis_skin_checked="1"><div class="cmp-teaser__description" bis_skin_checked="1"><p class="event-date">Feb 27, 2025 2:00 PM IST</p></div><h1 class="cmp-teaser__title event-heading css-1qcxeu7" data-titlerow="One" data-titlerowlaptop="One" data-titlerowtablet="One">Accelerate Your AI Development With NVIDIA NIM Microservices</h1><div class="cmp-teaser__description event-description css-1pptn7k" bis_skin_checked="1">Unleash the Power of Generative AI with NVIDIA NIM microservicesAs organizations transition from generative AI experiments to deploying and scaling generative AI applications in production, the focus on production model deployment for inference—where AI delivers results—is growing. In addition to strategies that ensure data security and compliance while enabling flexibility and agility for innovation, enterprises need a streamlined, cost-effective approach to managing AI inference at scale.Master NVIDIA NIM microservices for deploying foundation models securely and efficiently. This workshop covers comprehensive deployment strategies for Language Models, Vision Language Models, Speech Models, Embeddings, and Rerankers. Learn to implement production-grade runtimes with enterprise support across cloud and data center environments.Join us for an engaging webinar where we'll explore key considerations for deploying and scaling generative AI in production, including the critical role of AI inference. Through real-world case studies highlighting successful enterprise deployments, we'll uncover best practices supporting enterprise data security and compliance, enabling developer innovation and agility, and unlocking AI inference for production applications at scale.Don't miss out on this opportunity to accelerate your enterprise journey to generative AI.LearningsThe Current Landscape of Generative AI:Understand the latest trends and challenges in deploying generative AI models.NVIDIA NIM microservices:A Game-Changer: Discover how NVIDIA NIMs can significantly improve the performance and efficiency of your generative AI inferences. Learn how to implement production-ready AI applications using NVIDIA NIM microservices &amp; ensure security and compliance in model deployment.Real-World Case Studies:Hear from industry experts atxxxxas they share their experiences using NVIDIA NIMs to optimize their AI applications.(C) NVIDIA Corporation 2025. All rights reserved. No recording of this webinar should be made or reposted without the express written consent of NVIDIA Corporation.</div></div></div></a>


                            {
                                Event Name: Accelerate Your AI Development With NVIDIA NIM Microservices
                                Date: 2025/02/27
                                href: [#/webinar/4821105] 
                            }


                            Prompt:
                            <div class="teaser css-n9ns6f" bis_skin_checked="1"><a id="nv-teaser-bb36c49de7" class="cmp-teaser     " data-title-style="dynamic" href="#/webinar/4737096" target="_blank"><div class="nv-teaser--holder" bis_skin_checked="1"><div class="cmp-teaser__image" data-type="renditionUpload" data-altvaluefromdam="true" bis_skin_checked="1"><div data-cmp-lazy="" data-cmp-lazythreshold="300" data-cmp-src="/content/nvidiaGDC/zz/en_ZZ/testing/testdata/_jcr_content/root/responsivegrid/nv_container_170217500/nv_teaser.coreimg.100{.width}.png/1697602993046/nvidialogo.png" data-cmp-widths="190,410,630,850,1070,1290" class="cmp-image" data-cmp-type="renditionUpload" bis_skin_checked="1"><img class="cmp-image__image" data-cmp-hook-image="image" data-analytics="nv-image-bb36c49de7" src="https://orion.akamaized.net/media/cv/video_library/client/25/37/3/rt/11/63/74/5/rt/webinar_cut_myhqY.png" alt="Data Insights Unleashed" title="Data Insights Unleashed" style="max-height: 200px;"></div></div></div><div class="general-container-text h--smallest css-6sx646" bis_skin_checked="1"><div class="text-left lap-text-left tab-text-left mob-text-left" bis_skin_checked="1"><div class="cmp-teaser__description" bis_skin_checked="1"><p class="event-date">Oct 31, 2024 10:00 AM PDT</p></div><h1 class="cmp-teaser__title event-heading css-1qcxeu7" data-titlerow="One" data-titlerowlaptop="One" data-titlerowtablet="One">Data Insights Unleashed</h1><div class="cmp-teaser__description event-description css-1pptn7k" bis_skin_checked="1">The integration of AI into traditional workflows and enterprise applications is blurring the lines between serial and parallel processing, requiring a new accelerated compute platform with a hybrid architecture that can seamlessly blend the flexibility and energy efficiency of the ARM CPU with the performance of the GPU. Join this webinar to hear from HEAVY.AI and Vultr on how the NVIDIA Grace Hopper™ Superchip’s converged memory architecture is accelerating a wide array of enterprise workloads for their customers, from database and analytics to LLM-powered agents, all while unlocking energy savings in the data center. In this webinar, you’ll learn:The benefits of the converged memory architecture of the NVIDIA GH200 SuperchipHow HEAVY.AI is leveraging NVIDIA GH200 to accelerate database query times, unlock new analytical insights, and deliver cost savings for its customersHow Vultr built out its NVIDIA GH200 cloud instances and how its customers are leveraging it to build LLM-powered digital agents(C) NVIDIA Corporation 2024. All rights reserved. No recording of this webinar should be made or reposted without the express written consent of NVIDIA Corporation.</div></div></div></a></div>

                            {
                            Event Name: Data Insights Unleashed
                            Date: 2024/10/31
                            href: [#/webinar/4737096],
                            }'''
            },

            {
                "role": "user",
                "content": f'''{html}''',
            },
        ]
    )
    return chat_response.choices[0].message.content