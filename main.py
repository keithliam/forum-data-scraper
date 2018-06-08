from bs4 import BeautifulSoup
from bs4.element import Tag
import urllib.request
import copy

class StackoverflowParser:
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

	# extract the question header
	def extractQuestionHeader(self, html):
		return html.find(id="question-header").h1.string

	# extract answers from page
	def extractAnswers(self, html):
		allAnswers = []
		answers = html.select('.answer')
		for answer in answers:
			answerData = {}
			answerData['answer'] = self.extractPostBody(answer)
			answerData['upvotes'] = self.extractUpvotes(answer)
			answerData['author'] = self.extractAuthor(answer, isAnswer=True)
			answerData['editor'] = self.extractEditor(answer)
			answerData['comments'] = self.extractComments(answer)
			allAnswers.append(copy.deepcopy(answerData))
		return allAnswers

	# get user-details class from question-class
	def getAuthorUserDetailsClass(self, questionClass, isAnswer):
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

	def getNameFromUserDetails(self, userDetailsClass):
		if len(userDetailsClass.contents) == 1:
			return userDetailsClass.contents[0].strip()
		elif userDetailsClass.contents[1].name == 'a':
			return userDetailsClass.contents[1].string.strip()
		elif len(userDetailsClass.contents) > 2:
			return userDetailsClass.contents[2].string.strip()
		else:
			return userDetailsClass.contents[0].strip()

	# extract upvotes from question/answer main tag
	def extractUpvotes(self, mainTag):
		return int(mainTag.find(attrs={'class':'vote-count-post'}).string)

	# extract number of favorites from question/answer main tag
	def extractFavorites(self, mainTag):
		return int(mainTag.find(attrs={'class':'favoritecount'}).string)

	# extract author from user-details class
	def extractAuthor(self, questionClass, isAnswer=False):
		userDetailsClass = self.getAuthorUserDetailsClass(questionClass, isAnswer)
		return self.getNameFromUserDetails(userDetailsClass)

	def getEditorUserDetailsClass(self, questionClass):
		if questionClass.select(".post-signature .user-details")[0].a != None:
			return questionClass.select(".post-signature .user-details")[0]
		else:
			return None

	def extractEditor(self, questionClass):
		userDetailsClass = self.getEditorUserDetailsClass(questionClass)
		if userDetailsClass != None:
			return self.getNameFromUserDetails(userDetailsClass)
		else:
			return None

	def extractPostBody(self, postTag):
		return self.extractString(postTag.select('.post-text')[0]).strip()

	def getCommentsList(self, mainTag):
		return mainTag.find_all(attrs={'class':'comment'})

	def extractComment(self, commentTag):
		return self.extractString(commentTag.find(attrs={'class':'comment-copy'}))

	def extractCommentUpvotes(self, commentTag):
		if commentTag.span['class'][0] == 'warm' or commentTag.span['class'][0] == 'hot' or commentTag.span['class'][0] == 'cool':
			return int(commentTag.span.string)
		else:
			return 0

	def extractCommentAuthor(self, commentTag):
		return self.extractString(commentTag.find(attrs={'class':'comment-user'}))

	def extractCommentDate(self, commentTag):
		return self.extractString(commentTag.find(attrs={'class':'comment-date'}))

	def extractComments(self, mainTag):
		comments = self.getCommentsList(mainTag)

		commentList = []
		commentData = {}
		for comment in comments:
			commentData['comment'] = self.extractComment(comment)
			commentData['upvotes'] = self.extractCommentUpvotes(comment)
			commentData['author'] = self.extractCommentAuthor(comment)
			commentData['date'] = self.extractCommentDate(comment)
			commentList.append(copy.deepcopy(commentData))

		return commentList

	def parse(self):
		soup = self.getHTMLFile(self.url)

		# extract question
		data = {}
		data['question'] = {}
		data['question']['header'] = self.extractQuestionHeader(soup)
		data['question']['desc'] = self.extractPostBody(soup.select('#question')[0])
		data['question']['upvotes'] = self.extractUpvotes(soup.select('#question')[0])
		data['question']['favorites'] = self.extractFavorites(soup.select('#question')[0])
		data['question']['author'] = self.extractAuthor(soup.select('#question')[0])
		data['question']['editor'] = self.extractEditor(soup.select('#question')[0])
		data['question']['comments'] = self.extractComments(soup.select('#question')[0])

		# extract answers
		data['answer'] = self.extractAnswers(soup)

		# extract more answers if pagination is found
		nextPage = soup.find(attrs={'class':'page-numbers next'})
		while nextPage:
			soup = self.getHTMLFile('https://stackoverflow.com' + nextPage.parent['href'])
			data['answer'] += self.extractAnswers(soup)

			nextPage = soup.find(attrs={'class':'page-numbers next'})
		return data

url = 'https://stackoverflow.com/questions/927358/how-to-undo-the-most-recent-commits-in-git'
# url = 'https://stackoverflow.com/questions/959215/how-do-i-remove-leading-whitespace-in-python?noredirect=1&lq=1'
# url = 'https://stackoverflow.com/questions/761804/how-do-i-trim-whitespace-from-a-python-string'
parser = StackoverflowParser(url)
print(parser.parse())
