from datetime import datetime, date

import urlparse
import re

from scrapy.selector import Selector
from scrapy. http import Request
from scrapy.spider import Spider

from ..items import Dog


class DogSpider(Spider):
    name = 'fetch'

    START_URL = 'http://www.animalcenter.org/adoptions/animals.aspx?type=dogs'
    BASE_URL = 'http://www.animalcenter.org/adoptions/'

    def __init__(self, breeds=None, *args, **kwargs):
        super(DogSpider, self).__init__(*args, **kwargs)
        self.breeds = breeds

    def start_requests(self):
        request = Request(url=self.START_URL, callback=self.parse_main, dont_filter=True)
        yield request

    @staticmethod
    def strip_html(selector):
        return re.sub('<[^<]+?>', '', selector)

    def parse_main(self, response):

        sel = Selector(response)
        dogs = sel.css('#maincontent_lblAnimals div table tr td')

        for dog in dogs:
            new_dog = Dog()
            if dog.css('h3'):
                new_dog['name'] = self.strip_html(dog.css('h3').extract()[0])

                # Really hacky way to grab all this. @todo Refactor maybe.
                info = re.sub('<[^<]+?>', '--', dog.css('p')[1].extract()).replace(' ', '').split('--')
                sex_index = ['Sex' in el for el in info].index(True)
                dob_index = ['DOB' in el for el in info].index(True)
                weight_index = ['Weight' in el for el in info].index(True)
                color_index = ['Color' in el for el in info].index(True)

                breed = self.strip_html(dog.css('p')[0].extract()).replace('- ', ' ')
                new_dog['breed'] = breed
                new_dog['sex'] = info[sex_index].split(':')[-1]

                days_age = (date.today() - datetime.strptime(info[dob_index].split(':')[-1], '%m/%d/%Y').date()).days
                years, year_remainder = divmod(days_age, 365)
                months, month_remainder = divmod(year_remainder, 30)
                if month_remainder > 15:
                    months += 0.5

                if years == 0:
                    new_dog['age'] = str(months) + ' months'
                elif years != 0 and months == 0:
                    new_dog['age'] = ' '.join([str(years), 'years'])
                else:
                    new_dog['age'] = ' '.join([str(years), 'years',
                                               str(months), 'months'])
                new_dog['weight'] = info[weight_index].split(':')[-1].replace('lbs', ' lbs')
                new_dog['color'] = info[color_index].split(':')[-1].replace('and', ', ')

                url = dog.css('a::attr(href)')[0].extract()
                indiv_url = urlparse.urljoin(self.BASE_URL, url)
                if self.breeds is None or (any([b.lower() in breed.lower() for b in self.breeds.split(',')])):
                    yield Request(url=indiv_url, meta={'item': new_dog},
                              callback=DogSpider.parse_individual, dont_filter=True)
    @staticmethod
    def parse_individual(response):

        new_dog = response.meta['item']
        sel = Selector(response)
        new_dog['bio'] = DogSpider.strip_html(sel.css('h3')[1].extract()).replace('`', '')

        yield new_dog
