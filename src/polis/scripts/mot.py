import datetime
import sys

import polis
from polis._scrapers import _get_soup_urllib
from utils import *

name = 'Ministry of Transport'
url = 'https://consult.transport.govt.nz/'
colour = '#0eafd2'

async def scrape_ccc_consultations(get_html_func=_get_soup_urllib) -> list[dict]:
	url = sys.modules[__name__].url
	name = sys.modules[__name__].name

	html_soup = get_html_func(url)

	current = html_soup.find(string='Open consultations')

	#No consultations available
	if not current:
		return []

	entries = []

	html_entries = current.parent.parent.parent.find('div', {'class': 'row'}).find_all('div', recursive=False)

	for html_entry in html_entries:
		title =  clean_str(str(html_entry.div.h3.a.string))
		url = clean_str(str(html_entry.div.h3.a.get('href')))
		date_unf = clean_str(str(html_entry.div.find_all('div')[1].text).replace('Closes',''))

		if date_unf.lower() == 'today':
			date_obj = datetime.datetime.combine(datetime.date.today(), datetime.datetime.min.time())
		else:
			date_obj = datetime.datetime.strptime(date_unf, "%d %B %Y")

		entries.append(dict(org=polis.SCRAPER_ENUM.mot, title=title, url=url, blurb=None, date=date_obj))

	return entries
