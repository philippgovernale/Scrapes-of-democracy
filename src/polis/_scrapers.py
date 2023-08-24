import urllib.request
from bs4 import BeautifulSoup

def _get_soup_urllib(url: str) -> BeautifulSoup:
	html = urllib.request.urlopen(url)
	return BeautifulSoup(html, 'lxml')
