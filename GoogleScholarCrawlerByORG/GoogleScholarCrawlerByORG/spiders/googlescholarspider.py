# -*- coding: utf-8 -*-
import scrapy
from GoogleScholarCrawlerByORG.items import profileItem
from GoogleScholarCrawlerByORG.items import publicationItem
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from scrapy.http import HtmlResponse
import time

class GooglescholarspiderSpider(scrapy.Spider):
	name = 'googlescholarspider'
	allowed_domains = ['scholar.google.com']
	start_urls = ['https://scholar.google.com/citations?view_op=view_org&hl=en&org=3903766639137847059']
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

		profile_urls = []
		next_page_button = '//*[@id="gsc_authors_bottom_pag"]/div/button[2]'
		p = 0;
		while True:
			urls = response.xpath('//a[@class="gs_ai_pho"]/@href').extract()
			profile_urls += urls

			#next page
			if response.xpath(next_page_button + '/@onclick').extract() != []:
				p = p+1
				print("-------------------p--------------------", p)
				time.sleep(1)
				self.driver.find_element_by_xpath(next_page_button).click()
				body = self.driver.page_source
				response = HtmlResponse(self.driver.current_url, body=body.encode('utf-8'), encoding='utf-8')
			else:
				break
		for url in profile_urls:
			url = self.base_url + url
			yield scrapy.Request(url=url, callback=self.parse_profile)

	def parse_profile(self, response):
		self.driver.get(response.url)
		body = self.driver.page_source
		response = HtmlResponse(self.driver.current_url, body=body.encode('utf-8'), encoding='utf-8')

		# extract profile info
		profile_item = profileItem()
		profile_item['name'] = response.xpath('//div[@id="gsc_prf_in"]/text()').extract()
		profile_item['org'] = response.xpath('//div[@id="gsc_prf_i"]/div[2]/a/text()').extract()
		profile_item['title'] = response.xpath('//div[@id="gsc_prf_i"]/div[2]/text()').extract()
		profile_item['interests'] = response.xpath('//div[@id="gsc_prf_int"]/a/text()').extract()
		for k,v in profile_item.items():
			if v == []:
				profile_item[k] = ['']

		time.sleep(1)
		yield profile_item

		# repeatedly click "SHOW MORE" til all publications of the auther are displayed
		pub_count = '0'
		show_more_button = '//button[@id="gsc_bpf_more"]'
		while(pub_count != response.xpath('//span[@id="gsc_a_nn"]/text()').re(r'([0-9]+)$')[0]):
			pub_count = response.xpath('//span[@id="gsc_a_nn"]/text()').re(r'([0-9]+)$')[0]
			print("********************************", pub_count)
			self.driver.find_element_by_xpath(show_more_button).click()
			body = self.driver.page_source
			response = HtmlResponse(self.driver.current_url, body=body.encode('utf-8'), encoding='utf-8')

		# extract all publication urls from table
		pub_urls = response.xpath('//td[@class="gsc_a_t"]/a/@data-href').extract()
		for pub_url in pub_urls:
			pub_url = self.base_url + pub_url
			yield scrapy.Request(url=pub_url, callback=self.parse_publication)


	def parse_publication(self, response):
		pub_item = publicationItem()
		pub_item['title'] = response.xpath('//div[@id="gsc_vcd_title"]/a/text()').extract()
		pub_item['authors'] = response.xpath('//div[@class="gsc_vcd_field" and contains(text(),"Authors")]/../div[2]/text()').extract()
		pub_item['date'] = response.xpath('//div[@class="gsc_vcd_field" and contains(text(),"Publication date")]/../div[2]/text()').extract()
		pub_item['publisher'] = response.xpath('//div[@class="gsc_vcd_field" and contains(text(),"Publisher")]/../div[2]/text()').extract()
		pub_item['description'] = response.xpath('//div[@class="gsc_vcd_field" and contains(text(),"Description")]/../div[2]/text()').extract()
		pub_item['citations'] = response.xpath('//div[@class="gsc_vcd_field" and contains(text(),"Total citations")]/../div[2]/div[1]/a/text()').re(r'[0-9]+$')

		for k,v in pub_item.items():
			if v == []:
				pub_item[k] = ['']

		yield pub_item