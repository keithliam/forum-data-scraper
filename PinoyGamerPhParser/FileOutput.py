import os.path

def outputJSONFile(data):
	fileNum = 1
	while os.path.isfile('spai_pinoygamerph_' + str(fileNum) + '.json'):
		fileNum += 1
	fp = open('spai_pinoygamerph_' + str(fileNum) + '.json', 'w')
	fp.write(data)
	fp.close()