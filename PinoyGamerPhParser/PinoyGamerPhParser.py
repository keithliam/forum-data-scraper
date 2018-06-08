from bs4 import BeautifulSoup
from bs4.element import Tag
import urllib.request
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
				if not (item.has_attr('class') and item['class'][0] == 'quoteExpand'):
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
		extraInfo = message.find(class_='extraUserInfo').find_all(class_='pairsJustified')
		userData['no_of_topics'] = int(extraInfo[0].a.string)
		if len(extraInfo) == 2:
			if extraInfo[1].dt.string == 'Gender:':
				userData['gender'] = extraInfo[1].dd.string
			else:
				userData['team'] = extraInfo[1].dd.string
		elif len(extraInfo) == 3:
			userData['gender'] = extraInfo[1].dd.string
			userData['team'] = extraInfo[2].dd.string
		return userData

	def extractForumTitle(self, soup):
		return soup.find(class_='titleBar').h1.string.strip()

	def extractForumCategory(self, soup):
		return soup.find(id='pageDescription').a.string.strip()

	def extractMessageBody(self, message):
		return self.extractString(message.find(class_='messageText'))

	def extractPostDate(self, message):
		if message.find(class_='DateTime').name == 'span':
			return message.find(class_='DateTime')['title']
		else:
			return message.find(class_='DateTime')['data-datestring'] + ' at ' + message.find(class_='DateTime')['data-timestring']

	def extractPosts(self, messages):
		data = []
		for message in messages:
			messageData = {}
			messageData['user_id'] = self.extractUser(message)
			messageData['message'] = self.extractMessageBody(message)
			messageData['others'] = {}
			messageData['others']['date_posted'] = self.extractPostDate(message)
			messageData['others']['user_info'] = self.extractUserInfo(message)
			data.append(dict(messageData))
		return data

	def parse(self):
		soup = self.getHTMLFile(self.url)
		
		messages = self.getMessages(soup)

		data = {}
		data['others'] = {}
		data['user_id'] = self.extractUser(messages[0])
		data['message'] = self.extractMessageBody(messages[0])
		data['date_posted'] = self.extractPostDate(messages[0])
		data['others']['user_info'] = self.extractUserInfo(messages[0])
		data['others']['title'] = self.extractForumTitle(soup)
		data['others']['category'] = self.extractForumCategory(soup)
		data['quotes'] = self.extractPosts(messages[1:])
		print(data['quotes'])

		return self.convertToJSON(data) 