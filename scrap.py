import scrapy
import json

class PgSpider(scrapy.Spider):
    name = 'proc_geral_4'
    start_urls = [
        'https://www.pg.unicamp.br/normas?tipoaux=&tipo=todos&numero=&anoaux=2024&todos=1&ementa=&palavras=&tblCad_length=25&tblCep_length=25&tblConsu_length=25&tblPortaria_length=25&tblResolucao_length=25&tblPosGraduacao_length=25'
    ]

    def __init__(self, *args, **kwargs):
        super(PgSpider, self).__init__(*args, **kwargs)
        self.items = []

    def parse(self, response):
        for item in response.css('div.text-dark'):
            title = item.css('a::text').get()
            # Usando .xpath() para obter todos os textos do nó atual
            parts = item.xpath('.//text()').getall()  # Isso inclui o texto do link e os textos antes e depois
            link = item.css('a::attr(href)').get(default='')
            # Juntando todos os pedaços de texto para formar o texto completo
            text = ''.join(parts).replace('- ', '').strip()

            item_data = {
                'title': title.strip() if title else '',
                'text': text,
                'link': link
            }
            
            if 'javascript:mostra_norma_popup(' in link:
                # Extrai o ID do popup e usa como URL para o callback
                link_parts = link.split('(')[1].split(',')
                link_id_0 = link_parts[0]
                link_id_1 = link_parts[1].strip(');')  # Remove the closing ')' from the second part
                url = f'https://www.pg.unicamp.br/norma/{link_id_0}/{link_id_1}'
                request = scrapy.Request(url, callback=self.parse_info)
                request.cb_kwargs['item_data'] = item_data  # Passa os dados já coletados para o próximo método
                yield request
            else:
                self.items.append(item_data)

    def parse_info(self, response, item_data):
        # Extrai todo o texto da página
        info = response.xpath('//body//text()').getall()
        info = ' '.join(info).strip()
        item_data['info'] = info
        self.items.append(item_data)

    def closed(self, reason):
        with open('output_prof2_v2.json', 'w') as file:
            json.dump(self.items, file, ensure_ascii=False, indent=4)
