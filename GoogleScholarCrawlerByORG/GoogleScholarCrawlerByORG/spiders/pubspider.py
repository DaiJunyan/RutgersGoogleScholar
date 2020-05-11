# -*- coding: utf-8 -*-
import scrapy
from GoogleScholarCrawlerByORG.items import profileItem
from GoogleScholarCrawlerByORG.items import publicationItem
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from scrapy.http import HtmlResponse
import time
import random

class GooglescholarspiderSpider(scrapy.Spider):
	name = 'pubspider'
	allowed_domains = ['scholar.google.com']
	with open('./profile_urls.txt', 'r') as cache:
			start_urls = [line.rstrip("\n") for line in cache.readlines()]
	# start_urls = ['https://scholar.google.com/citations?user=cyEM2BoAAAAJ&hl=en']
	base_url = 'https://scholar.google.com'

	def __init__(self):
		# self.driver = webdriver.Firefox(executable_path='C:\Program Files (x86)\Firefox\geckodriver.exe')
		chrome_options = Options()
		# chrome_options.add_argument('--headless')
		chrome_options.add_argument('log-level=3')
		# chrome_options.add_argument('--disable-gpu')
		# chrome_options.add_argument('--no-sandbox')

		self.driver = webdriver.Chrome(chrome_options=chrome_options,
		                               executable_path='C:\Program Files (x86)\Google\Chrome\chromedriver\chromedriver.exe')
	def parse(self, response):
		self.driver.get(response.url)
		body = self.driver.page_source
		response = HtmlResponse(self.driver.current_url, body=body.encode('utf-8'), encoding='utf-8')
		
		# repeatedly click "SHOW MORE" til all publications of the auther are displayed
		pub_count = '0'
		show_more_button = '//button[@id="gsc_bpf_more"]'
		while(pub_count != response.xpath('//span[@id="gsc_a_nn"]/text()').re(r'([0-9]+)$')[0]):
			pub_count = response.xpath('//span[@id="gsc_a_nn"]/text()').re(r'([0-9]+)$')[0]
			print("**********************************************************pub_count ", pub_count)
			self.driver.find_element_by_xpath(show_more_button).click()
			time.sleep(random.uniform(1.0,2.5))
			body = self.driver.page_source
			# response = response.replace(body=body)
			response = HtmlResponse(self.driver.current_url, body=body.encode('utf-8'), encoding='utf-8')
			print("***********************************************************response ", response.xpath('//span[@id="gsc_a_nn"]/text()').re(r'([0-9]+)$')[0])

		# extract all publication urls from table
		pub_urls = response.xpath('//td[@class="gsc_a_t"]/a/@data-href').extract()

		print("*****************************************************************len ", len(pub_urls))
		# return None
		for pub_url in pub_urls:
			pub_url = self.base_url + pub_url
			time.sleep(random.uniform(5.0,10.0))
			yield scrapy.Request(url=pub_url, callback=self.parse_publication, meta={'url': pub_url})


	def parse_publication(self, response):
		pub_item = publicationItem()
		pub_item['title'] = response.xpath('//div[@id="gsc_vcd_title"]/a/text()').extract()
		pub_item['authors'] = response.xpath('//div[@class="gsc_vcd_field" and contains(text(),"Authors")]/../div[2]/text()').extract()
		pub_item['date'] = response.xpath('//div[@class="gsc_vcd_field" and contains(text(),"Publication date")]/../div[2]/text()').extract()
		pub_item['publisher'] = response.xpath('//div[@class="gsc_vcd_field" and contains(text(),"Publisher")]/../div[2]/text()').extract()
		# pub_item['description'] = response.xpath('//div[@class="gsc_vcd_field" and contains(text(),"Description")]/../div[2]/div[@class="gsh_small"]/div[@class="gsh_csp"]/text()').extract()
		pub_item['description'] = response.xpath('//div[@id="gsc_vcd_descr"]//text()').extract()
		pub_item['citations'] = response.xpath('//div[@class="gsc_vcd_field" and contains(text(),"Total citations")]/../div[2]/div[1]/a/text()').re(r'[0-9]+$')
		pub_item['url'] = response.meta['url']

		for k,v in pub_item.items():
			if v == [] and k != 'citations':
				pub_item[k] = ['']
			elif v ==[] and k == 'citations':
				pub_item[k] = ['0']

		yield pub_item