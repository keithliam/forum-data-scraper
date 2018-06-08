from bs4 import BeautifulSoup
from bs4.element import Tag
import urllib.request
import copy
import json

class PinoyGamerPhParser:
	def __init__(self, url):
		self.url = url

	# fetch html file from url
	def getHTMLFile(self, url):
		html = urllib.request.urlopen(url)
		index = html.read().decode('utf-8')
		return BeautifulSoup(index, "html.parser")

	# extract strings within a tag
	def extractString(self, contents):
		string = ''
		for item in contents.contents:
			if type(item) == Tag:
				if item.name == 'p':
					string += '\n'
				string += self.extractString(item) 			
			else:
				string += item
		return string

	def convertToJSON(self, data):
		return json.dumps(data)

	def getMessages(self, soup):
		messages = soup.find_all(class_='message')
		del(messages[1])
		return messages

	def extractUser(self, message):
		return message.find(class_='username').string

	def extractUserInfo(self, message):
		userData = {}
		userData['user_title'] = message.find(class_='userTitle').string
		return userData

	def parse(self):
		soup = self.getHTMLFile(self.url)
		
		messages = self.getMessages(soup)

		data = {}
		data['others'] = {}
		data['user_id'] = self.extractUser(messages[0])
		data['others']['user_info'] = self.extractUserInfo(messages[0])

		return self.convertToJSON(data)