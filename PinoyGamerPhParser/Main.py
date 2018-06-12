from PinoyGamerPhParser import PinoyGamerPhParser
from FileOutput import outputJSONFile

url = ''
while url == '':
	url = input('Enter pinoygamerph page URL: ').strip()

parser = PinoyGamerPhParser(url)
outputJSONFile(parser.parse())
