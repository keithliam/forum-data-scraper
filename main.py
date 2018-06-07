from bs4 import BeautifulSoup
from bs4.element import Tag
import urllib.request

def extractString(contents):
	string = ''
	for item in contents.contents:
		if type(item) == Tag:
			if item.name == 'p':
				string += '\n'
			string += extractString(item) 			
		else:
			string += item
	return string

url = 'https://stackoverflow.com/questions/927358/how-to-undo-the-most-recent-commits-in-git'

html = urllib.request.urlopen(url)
index = html.read().decode('utf-8')
soup = BeautifulSoup(index, "html.parser")

data = {}
data['question'] = {}
data['answer'] = []

data['question']['header'] = soup.find(id="question-header").h1.string

contents = soup.select('#question .post-text')[0]
data['question']['desc'] = extractString(contents).strip()