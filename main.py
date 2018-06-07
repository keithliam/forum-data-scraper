from bs4 import BeautifulSoup
from bs4.element import Tag
import urllib.request

# extract strings within a tag
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

# get user-details class from question-class
def getUserDetailsClass(questionClass):
	if questionClass.find(attrs={'class':'owner'}) == None:
		return questionClass.select('.user-info .user-details a:nth-of-type(2)')[0]
	else:
		return questionClass.select('.owner .user-info .user-details')[0]

# extract author from user-details class
def extractAuthor(questionClass):
	userDetailsClass = getUserDetailsClass(questionClass)
	if len(userDetailsClass.contents) == 1:
		return userDetailsClass.contents[0].strip()
	elif userDetailsClass.contents[1].name == 'a':
		return userDetailsClass.contents[1].string.strip()
	else:
		return userDetailsClass.contents[0].strip()


# url = 'https://stackoverflow.com/questions/927358/how-to-undo-the-most-recent-commits-in-git'
# url = 'https://stackoverflow.com/questions/959215/how-do-i-remove-leading-whitespace-in-python?noredirect=1&lq=1'
url = 'https://stackoverflow.com/questions/761804/how-do-i-trim-whitespace-from-a-python-string'

html = urllib.request.urlopen(url)
index = html.read().decode('utf-8')
soup = BeautifulSoup(index, "html.parser")

data = {}
data['question'] = {}
data['answer'] = []

# extract question header
data['question']['header'] = soup.find(id="question-header").h1.string

# extract question description
contents = soup.select('#question .post-text')[0]
data['question']['desc'] = extractString(contents).strip()

# extract question upvotes
upvotes = soup.select('#question .vote-count-post')[0].string
data['question']['upvotes'] = upvotes

# extract question author
author = extractAuthor(soup.select('#question')[0])
data['question']['author'] = author

# extract answers
answers = soup.select('.answer')
for answer in answers:
	contents = answer.select('.post-text')[0]
	string = extractString(contents).strip()
	data['answer'].append(string)