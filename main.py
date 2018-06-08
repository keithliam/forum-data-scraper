from bs4 import BeautifulSoup
from bs4.element import Tag
import urllib.request
import copy

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

# extract the question header
def extractQuestionHeader(html):
	return soup.find(id="question-header").h1.string

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

# extract upvotes from question/answer main tag
def extractUpvotes(mainTag):
	return int(mainTag.find(attrs={'class':'vote-count-post'}).string)

# extract number of favorites from question/answer main tag
def extractFavorites(mainTag):
	return int(mainTag.find(attrs={'class':'favoritecount'}).string)

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

def extractPostBody(postTag):
	return extractString(postTag.select('.post-text')[0]).strip()

def getCommentsList(mainTag):
	return mainTag.find_all(attrs={'class':'comment'})

def extractComment(commentTag):
	return extractString(commentTag.find(attrs={'class':'comment-copy'}))

def extractCommentUpvotes(commentTag):
	if commentTag.span['class'][0] == 'warm' or commentTag.span['class'][0] == 'hot' or commentTag.span['class'][0] == 'cool':
		return int(commentTag.span.string)
	else:
		return 0

def extractCommentAuthor(commentTag):
	return extractString(commentTag.find(attrs={'class':'comment-user'}))

def extractCommentDate(commentTag):
	return extractString(commentTag.find(attrs={'class':'comment-date'}))

def extractComments(mainTag):
	comments = getCommentsList(mainTag)

	commentList = []
	commentData = {}
	for comment in comments:
		commentData['comment'] = extractComment(comment)
		commentData['upvotes'] = extractCommentUpvotes(comment)
		commentData['author'] = extractCommentAuthor(comment)
		commentData['date'] = extractCommentDate(comment)
		commentList.append(copy.deepcopy(commentData))

	return commentList

url = 'https://stackoverflow.com/questions/927358/how-to-undo-the-most-recent-commits-in-git'
# url = 'https://stackoverflow.com/questions/959215/how-do-i-remove-leading-whitespace-in-python?noredirect=1&lq=1'
# url = 'https://stackoverflow.com/questions/761804/how-do-i-trim-whitespace-from-a-python-string'

html = urllib.request.urlopen(url)
index = html.read().decode('utf-8')
soup = BeautifulSoup(index, "html.parser")

# extract question
data = {}
data['question'] = {}
data['answer'] = []
data['question']['header'] = extractQuestionHeader(soup)
data['question']['desc'] = extractPostBody(soup.select('#question')[0])
data['question']['upvotes'] = extractUpvotes(soup.select('#question')[0])
data['question']['favorites'] = extractFavorites(soup.select('#question')[0])
data['question']['author'] = extractAuthor(soup.select('#question')[0])
data['question']['editor'] = extractEditor(soup.select('#question')[0])
data['question']['comments'] = extractComments(soup.select('#question')[0])

# extract answers
answers = soup.select('.answer')
for answer in answers:
	answerData = {}
	answerData['answer'] = extractPostBody(answer)
	answerData['upvotes'] = extractUpvotes(answer)
	answerData['author'] = extractAuthor(answer, isAnswer=True)
	answerData['editor'] = extractEditor(answer)
	answerData['comments'] = extractComments(answer)
	data['answer'].append(copy.deepcopy(answerData))

# extract more answers if pagination is found
nextPage = soup.find(attrs={'class':'page-numbers next'})
while nextPage:
	print(len(data['answer']))
	nextPageURL = 'https://stackoverflow.com' + nextPage.parent['href']

	html = urllib.request.urlopen(nextPageURL)
	index = html.read().decode('utf-8')
	soup = BeautifulSoup(index, "html.parser")

	answers = soup.select('.answer')
	for answer in answers:
		answerData = {}
		answerData['answer'] = extractPostBody(answer)
		answerData['upvotes'] = extractUpvotes(answer)
		answerData['author'] = extractAuthor(answer, isAnswer=True)
		answerData['editor'] = extractEditor(answer)
		answerData['comments'] = extractComments(answer)
		data['answer'].append(copy.deepcopy(answerData))	

	nextPage = soup.find(attrs={'class':'page-numbers next'})