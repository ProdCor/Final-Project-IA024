# Abordagem número 2

import scrapy
import json


class PgSpider(scrapy.Spider):
    name = 'proc_geral_10'
    start_urls = [
        'https://www.pg.unicamp.br/normas?tipoaux=&tipo=todos&numero=&anoaux=2024&todos=1&ementa=&palavras=&tblCad_length=25&tblCep_length=25&tblConsu_length=25&tblPortaria_length=25&tblResolucao_length=25&tblPosGraduacao_length=25'
    ]
    revogados = []
    alterados = []

    def __init__(self, *args, **kwargs):
        super(PgSpider, self).__init__(*args, **kwargs)
        self.items = []

    def handle_error(self, failure):
        if failure.check(HttpError):
            response = failure.value.response
            self.logger.error('HttpError on %s', response.url)
        
    def parse(self, response):
        for item in response.css('div.text-dark'):
            title = item.css('a::text').getall()
            parts = item.xpath('.//text()').getall()  # Inclui texto do link e textos antes e depois
            link = item.css('a::attr(href)').get(default='')
            description = ''.join(parts).replace('- ', '').strip()


            item_data = {
                'title_main': title[0].strip() if title else '',
                'description': description,
            }

            if 'javascript:mostra_norma_popup(' in link:
                link_parts = link.split('(')[1].split(',')
                link_id_0 = link_parts[0].strip("'")
                link_id_1 = link_parts[1].strip(');')

                url_original = f'https://www.pg.unicamp.br/norma/{link_id_0}/{link_id_1}'
                item_data['url_ori'] = url_original
                #url_conso = f'https://www.pg.unicamp.br/norma/{link_id_0}/{1}'
                #item_data['url_conso'] = url_conso

                request_original = scrapy.Request(url_original, callback=self.parse_info_original, errback=self.handle_error)
                request_original.cb_kwargs['item_data'] = item_data  # Pass data already collected to the next method
                yield request_original
 
                
    def parse_info_original(self, response, item_data):
        # Process the response from the first request
        info_original = response.xpath('//body//text()').getall()
        info_original = ' '.join(info_original).strip()

        red_elements = response.css('div.text-danger').getall()

        #red_elements = response.xpath('//div[contains(@style, "color: #DC3545")]')
        #red_elements = response.xpath('//div.text-danger.fw-bold.style[contains(@style, "color: #DC3545")]')
        contains_revoga_in_red = any("revoga" in text.lower() for text in red_elements)

        # Here you can implement your condition to decide whether to make the second request
        if not contains_revoga_in_red:
            link_id_0 = response.url.split('/')[-2]
            url_conso = f'https://www.pg.unicamp.br/norma/{link_id_0}/{1}'
            request_conso = scrapy.Request(url_conso, callback=self.parse_info_conso, errback=self.handle_error)
            request_conso.cb_kwargs['item_data'] = item_data
            yield request_conso  # Emit the second request only if the condition is met

        if len(red_elements) == 0:
            item_data['info_original'] = info_original
            self.items.append(item_data)

    def parse_info_conso(self, response, item_data):
        info_conso = response.xpath('//body//text()').getall()
        info_conso = ' '.join(info_conso).strip()
        item_data['info_conso'] = info_conso
        self.items.append(item_data)


    def closed(self, reason):
        with open('output_prof3_v10_4.json', 'w') as file:
            json.dump(self.items, file, ensure_ascii=False, indent=4)
