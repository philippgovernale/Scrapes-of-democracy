import datetime
import sys
import json

import polis
from polis._scrapers import _get_soup_urllib

name = 'Ministry for Primary Industries'
url = 'https://www.mpi.govt.nz/consultations/'
colour = '#95c11f'

async def scrape_mpi_consultations(get_html_func=_get_soup_urllib) -> list[dict]:
	url = sys.modules[__name__].url
	name = sys.modules[__name__].name

	html_soup = get_html_func(url)

	consultation_list = html_soup.find_all('div', {'class': 'snippet mediarelease-override snippet-consultationarticle'})

	entries = []
	for entry in consultation_list:
		title = entry.div.a.get('title')
		url = entry.div.a.get('href')

		date_str = entry.div.div.div.time.text
		date = datetime.datetime.strptime(date_str, "%d %b %Y")

		entries.append(dict(org=polis.SCRAPER_ENUM.mpi, title=title, url=url, blurb=None, date=date))

	return entries
