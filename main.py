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
def getAuthorUserDetailsClass(questionClass, isAnswer):
	if isAnswer:
		count = len(questionClass.select('.user-info .user-details'))
		if count == 2:
			return questionClass.select('.user-info .user-details')[1]
		if count == 3:
			return questionClass.select('.user-info .user-details')[2].contents[1]
		else: 
			return questionClass.select('.user-info .user-details')[0]
	if questionClass.find(attrs={'class':'owner'}) == None:
		return questionClass.select('.user-info .user-details a:nth-of-type(2)')[0]
	else:
		return questionClass.select('.owner .user-info .user-details')[0]

def getNameFromUserDetails(userDetailsClass):
	if len(userDetailsClass.contents) == 1:
		return userDetailsClass.contents[0].strip()
	elif userDetailsClass.contents[1].name == 'a':
		return userDetailsClass.contents[1].string.strip()
	elif len(userDetailsClass.contents) > 2:
		return userDetailsClass.contents[2].string.strip()
	else:
		return userDetailsClass.contents[0].strip()

# extract author from user-details class
def extractAuthor(questionClass, isAnswer=False):
	userDetailsClass = getAuthorUserDetailsClass(questionClass, isAnswer)
	return getNameFromUserDetails(userDetailsClass)

def getEditorUserDetailsClass(questionClass):
	if questionClass.select(".post-signature .user-details")[0].a != None:
		return questionClass.select(".post-signature .user-details")[0]
	else:
		return None

def extractEditor(questionClass):
	userDetailsClass = getEditorUserDetailsClass(questionClass)
	if userDetailsClass != None:
		return getNameFromUserDetails(userDetailsClass)
	else:
		return None

# url = 'https://stackoverflow.com/questions/927358/how-to-undo-the-most-recent-commits-in-git'
url = 'https://stackoverflow.com/questions/959215/how-do-i-remove-leading-whitespace-in-python?noredirect=1&lq=1'
# url = 'https://stackoverflow.com/questions/761804/how-do-i-trim-whitespace-from-a-python-string'

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
data['question']['upvotes'] = int(upvotes)

# extract question author
author = extractAuthor(soup.select('#question')[0])
data['question']['author'] = author

# extract question editor
editor = extractEditor(soup.select('#question')[0])
if editor != None:
	data['question']['editor'] = editor

# extract answers
answers = soup.select('.answer')
for answer in answers:
	# answer message
	contents = answer.select('.post-text')[0]
	string = extractString(contents).strip()

	# answer upvotes
	upvotes = answer.select('.vote-count-post')[0].string

	# answer author
	author = extractAuthor(answer, isAnswer=True)

	# answer editor
	editor = extractEditor(answer)

	if editor is None:
		data['answer'].append({
			'string':	string,
			'upvotes':	int(upvotes),
			'author':	author
		})
	else:
		data['answer'].append({
			'string':	string,
			'upvotes':	int(upvotes),
			'author':	author,
			'editor': 	editor
		})