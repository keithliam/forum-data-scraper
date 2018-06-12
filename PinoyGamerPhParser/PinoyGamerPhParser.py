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
		return soup.find_all(class_='message')

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
		return dict(userData)

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

	def extractQuotedPost(self, message):
		quote = message.find(class_='bbCodeBlock bbCodeQuote')
		if quote:
			quoteData = {}
			quoteData['user_id'] = self.extractString(quote.div)[:-9]
			quoteData['message'] = quote.blockquote.div.string
			return dict(quoteData)
		else:
			return None

	def extractPosts(self, messages):
		data = []
		for message in messages:
			messageData = {}
			messageData['user_id'] = self.extractUser(message)
			messageData['message'] = self.extractMessageBody(message)
			messageData['others'] = {}
			messageData['others']['date_posted'] = self.extractPostDate(message)
			messageData['others']['user_info'] = self.extractUserInfo(message)
			quotedPost = self.extractQuotedPost(message)
			if quotedPost:
				messageData['others']['quoted_post'] = quotedPost
			data.append(dict(messageData))
		return data

	def getNextURL(self, soup):
		navButtons = soup.find(class_='PageNav')
		if navButtons:
			navButtons = navButtons.nav.find_all('a')
			lastButton = navButtons[len(navButtons) - 1]
			if lastButton.string == 'Next >':
				return 'https://pinoygamer.ph/' + lastButton['href']
			else:
				return None
		else:
			return None

	def extractNextPosts(self, soup):
		return self.extractPosts(self.getMessages(soup))

	def parse(self):
		soup = self.getHTMLFile(self.url)
		
		messages = self.getMessages(soup)
		del(messages[1])

		data = {}
		data['others'] = {}
		data['user_id'] = self.extractUser(messages[0])
		data['message'] = self.extractMessageBody(messages[0])
		data['date_posted'] = self.extractPostDate(messages[0])
		data['others']['user_info'] = self.extractUserInfo(messages[0])
		data['others']['title'] = self.extractForumTitle(soup)
		data['others']['category'] = self.extractForumCategory(soup)
		data['quotes'] = self.extractPosts(messages[1:])

		nextURL = self.getNextURL(soup)
		while nextURL:
			soup = self.getHTMLFile(nextURL)
			data['quotes'] += self.extractNextPosts(soup)
			nextURL = self.getNextURL(soup)

		return self.convertToJSON(data) 