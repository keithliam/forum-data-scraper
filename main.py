from StackoverflowParser import StackoverflowParser

url = ''
while url == '':
	url = input('Enter stackoverflow page URL: ').strip()

parser = StackoverflowParser(url)
print(parser.parse())
