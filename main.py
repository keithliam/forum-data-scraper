from bs4 import BeautifulSoup
import urllib.request

url = 'https://stackoverflow.com/questions/927358/how-to-undo-the-most-recent-commits-in-git'

html = urllib.request.urlopen(url)
index = html.read().decode('utf-8')
soup = BeautifulSoup(index, "html.parser")