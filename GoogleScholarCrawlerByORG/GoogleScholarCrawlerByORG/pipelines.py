# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import pymysql
from GoogleScholarCrawlerByORG.items import profileItem
from GoogleScholarCrawlerByORG.items import publicationItem

class GooglescholarcrawlerbyorgPipeline(object):
	def __init__(self):
		self.connect = pymysql.connect(
			host = 'localhost',
			db = 'GoogleScholars',
			user = 'root',
			passwd = '')
		self.cursor = self.connect.cursor()
		self.create_table()

	def create_table(self):
		self.cursor.execute('''CREATE TABLE IF NOT EXISTS Organizations(
								id int AUTO_INCREMENT PRIMARY KEY,
								name varchar(128))''')

		self.cursor.execute('''CREATE TABLE IF NOT EXISTS Authors(
								id int AUTO_INCREMENT PRIMARY KEY,
								name varchar(128),
								title varchar(128),
								Oid int,
								FOREIGN KEY (Oid) REFERENCES Organizations(id))''')

		self.cursor.execute('''CREATE TABLE IF NOT EXISTS Publications(
								id int AUTO_INCREMENT PRIMARY KEY,
								title varchar(256),
								authors varchar(256),
								description text,
								pubdate varchar(32),
								publisher varchar(128),
								citationNum int,
								url varchar(1024))''')

		self.cursor.execute('''CREATE TABLE IF NOT EXISTS Interests(
								id int AUTO_INCREMENT PRIMARY KEY,
								name varchar(128))''')

		self.cursor.execute('''CREATE TABLE IF NOT EXISTS Authors_to_Publications(
								Aid int,
								Pid int,
								PRIMARY KEY(Aid, Pid))''') # foreign key?

		self.cursor.execute('''CREATE TABLE IF NOT EXISTS Authors_to_Interests(
								Aid int,
								Iid int,
								PRIMARY KEY(Aid, Iid))''') # foreign key?

	def process_item(self, item, spider):
		if isinstance(item, profileItem):
			# insert value to table Organizations
			self.cursor.execute('''INSERT IGNORE INTO Organizations(name)
									SELECT %s WHERE NOT EXISTS(SELECT * FROM Organizations 
									WHERE name = %s)''', (item['org'][0], item['org'][0]))
			# insert value to table Authors
			self.cursor.execute('''INSERT IGNORE INTO Authors(name, title, Oid)
			 						SELECT %s, %s, o.id FROM Organizations o 
			 						WHERE o.name = %s''', (item['name'][0], item['title'][0], item['org'][0]))
			# insert interests
			for interest in item['interests']:
				self.cursor.execute('''INSERT IGNORE INTO Interests(name)
									SELECT %s 
									WHERE NOT EXISTS(SELECT * FROM Interests 
									WHERE name = %s)''', (interest, interest))
				self.cursor.execute('''INSERT IGNORE INTO Authors_to_Interests(Aid, Iid)
									SELECT a.id, i.id FROM Authors a, Interests i 
									WHERE a.name = %s AND i.name = %s''', (item['name'][0], interest))

		if isinstance(item, publicationItem):
			self.cursor.execute('''SELECT citationNum FROM Publications WHERE title = %s''', (item['title'][0]))
			citationNum = self.cursor.fetchone()
			if citationNum is None:
				self.cursor.execute('''INSERT IGNORE INTO Publications(title, authors, description, pubdate, publisher, citationNum, url)
									VALUES(%s, %s, %s, %s, %s, %s, %s)''', (item['title'][0], item['authors'][0], item['description'][0], item['date'], item['publisher'][0], int(item['citations'][0]), item['url'][0]))
			elif int(citationNum[0]) > int(item['citations'][0]):
				self.cursor.execute('''UPDATE Publications
										SET authors = %s, 
											description = %s,
											pubdate = %s,
											publisher = %s,
											citationNum = %s,
											url = %s
										WHERE title = %s''', (item['authors'][0], item['description'][0], item['pubdate'][0], item['publisher'][0], int(item['citations'][0]), item['url'][0], item['title'][0]))

		self.connect.commit()
		return item


	def close_spider(self, spider):
		self.connect.close()