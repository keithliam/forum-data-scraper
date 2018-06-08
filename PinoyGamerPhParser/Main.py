from PinoyGamerPhParser import PinoyGamerPhParser
from FileOutput import outputJSONFile

url = ''
while url == '':
	url = input('Enter stackoverflow page URL: ').strip()

parser = StackoverflowParser(url)
outputJSONFile(parser.parse())
