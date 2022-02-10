import scrapy
from scrapy.http import HtmlResponse
from jobparser.items import JobparserItem

class SjruSpider(scrapy.Spider):
    name = 'sjru'
    allowed_domains = ['superjob.ru']
    start_urls = ['https://www.superjob.ru/vacancy/search/?keywords=Python&geo%5Bt%5D%5B0%5D=4',
                  'https://spb.superjob.ru/vacancy/search/?keywords=Python']

    def parse(self, response):
        next_page = response.xpath("//a[@rel='next']/@href").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

        links = response.xpath("//div[@class='f-test-search-result-item']//a[contains(@href, 'vakansii')]/@href").getall()
        for link in links:
            yield response.follow(link, callback=self.vacancy_parse)

    def vacancy_parse(self, response: HtmlResponse):
        name = response.xpath("//h1//text()").get()
        salary_min, salary_max, salary_cur = self.prepare_salary(response.xpath("//h1/following-sibling::span/span/text()").getall())
        url = response.url
        yield JobparserItem(name=name, url=url, salary_min=salary_min, salary_max=salary_max, salary_cur=salary_cur)

    @staticmethod
    def prepare_salary(salary):
        salary_min, salary_max, salary_cur = None, None, None
        if len(salary) > 1:
            try:
                if salary[0].startswith('от'):
                    tmp = salary[2].split('\xa0')
                    salary_min = int(''.join(tmp[:-1]))
                    salary_cur = tmp[-1]
                elif salary[0].startswith('до'):
                    tmp = salary[2].split('\xa0')
                    salary_max = int(''.join(tmp[:-1]))
                    salary_cur = tmp[-1]
                else:
                    salary_min = int(salary[0].replace('\xa0', ''))
                    salary_max = int(salary[1].replace('\xa0', ''))
                    salary_cur = salary[3]
            except:
                pass

        print()

        return salary_min, salary_max, salary_cur
