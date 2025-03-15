import scrapy
# from MOL_UAE.items import Product
from lxml import html

class Mol_uaeSpider(scrapy.Spider):
    name = "MOL_UAE"
    start_urls = ["https://example.com"]

    def parse(self, response):
        parser = html.fromstring(response.text)
        print("Visited:", response.url)
