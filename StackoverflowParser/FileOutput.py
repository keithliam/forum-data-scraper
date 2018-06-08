def outputJSONFile(data):
	fp = open('output.json', 'w')
	fp.write(data)
	fp.close()