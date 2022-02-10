import scrapy
from scrapy.http import HtmlResponse
from jobparser.items import JobparserItem


class HhruSpider(scrapy.Spider):
    name = 'hhru'
    allowed_domains = ['hh.ru']
    start_urls = ['https://hh.ru/search/vacancy?area=1&fromSearchLine=true&text=Python&from=suggest_post&items_on_page=20',
                  'https://hh.ru/search/vacancy?area=2&fromSearchLine=true&text=Python&from=suggest_post&items_on_page=20']

    def parse(self, response: HtmlResponse):
        next_page = response.xpath("//a[@data-qa='pager-next']/@href").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

        links = response.xpath("//a[@data-qa='vacancy-serp__vacancy-title']/@href").getall()
        for link in links:
            yield response.follow(link, callback=self.vacancy_parse)

    def vacancy_parse(self, response: HtmlResponse):
        name = response.xpath("//h1//text()").get()
        salary_min, salary_max, salary_cur = self.prepare_salary(response.xpath("//div[@data-qa='vacancy-salary']//text()").getall())
        url = response.url
        yield JobparserItem(name=name, url=url, salary_min=salary_min, salary_max=salary_max, salary_cur=salary_cur)

    @staticmethod
    def prepare_salary(salary):
        salary_min, salary_max, salary_cur = None, None, None
        if len(salary) > 1:
            salary_cur = salary[-2]
            if salary[0].startswith('от'):
                salary_min = salary[1]
                if salary[2].find('до'):
                    salary_max = salary[3]
            if salary[0].startswith('до'):
                salary_max = salary[1]

            try:
                salary_min = int(salary_min.replace('\xa0', ''))
            except:
                salary_min = None
            try:
                salary_max = int(salary_max.replace('\xa0', ''))
            except:
                salary_max = None

        return salary_min, salary_max, salary_cur
