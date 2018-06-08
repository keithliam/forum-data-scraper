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

	def parse(self):
		# soup = self.getHTMLFile(self.url)