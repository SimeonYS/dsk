import re

import scrapy

from scrapy.loader import ItemLoader
from ..items import DskItem
from itemloaders.processors import TakeFirst
pattern = r'(\xa0)?'

class DskSpider(scrapy.Spider):
	name = 'dsk'
	start_urls = ['https://dskbank.bg/%D0%BD%D0%BE%D0%B2%D0%B8%D0%BD%D0%B8-%D0%B8-%D0%BF%D1%80%D0%BE%D0%BC%D0%BE%D1%86%D0%B8%D0%B8/1']
	i = 1
	def parse(self, response):
		post_links = response.xpath('//h2[@class="news__title"]/a/@href').getall()
		yield from response.follow_all(post_links, self.parse_post)

		next_page = response.xpath(f'//li[@class="pagination__item"][{self.i}+1]/a[@class="pagination__link"]/@href').get()
		if next_page:
			self.i +=1
			yield response.follow(next_page, self.parse)
		else:
			nexxt = response.xpath('//li/a[@class="pagination__link pagination__link--next"]/@href').get()
			yield response.follow(nexxt, self.parse)
			self.i +=1

	def parse_post(self, response):

		date = response.xpath('//article[@class="general"]//time/text()').get()
		title = response.xpath('//h1/text()').get()
		content = response.xpath('//article[@class="general"]//text()[not (ancestor::time) and not (ancestor::h1)]').getall()
		content = [p.strip() for p in content if p.strip()]
		content = re.sub(pattern, "",' '.join(content))


		item = ItemLoader(item=DskItem(), response=response)
		item.default_output_processor = TakeFirst()

		item.add_value('title', title)
		item.add_value('link', response.url)
		item.add_value('content', content)
		item.add_value('date', date)

		return item.load_item()
