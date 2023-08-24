import re
import datetime
import sys
import json

import polis
from polis._scrapers import _get_soup_urllib

name = 'Ministry for the Environment'
url = 'https://environment.govt.nz/what-you-can-do/have-your-say/'
colour = 'green'

async def scrape_mfe_consultations(get_html_func=_get_soup_urllib) -> list[dict]:
	url = sys.modules[__name__].url
	name = sys.modules[__name__].name

	html_soup = get_html_func(url)

	tmp = html_soup.find('results-container').get(':initial-state')
	data = json.loads(tmp)['nodes']

	entries = []
	for consultation_dict in data:
		title = consultation_dict['title']
		url = consultation_dict['href']
		blurb = consultation_dict['intro']

		date=None
		date_match = re.search('Closes (\d{1,2} [a-zA-Z]{3,9} \d\d\d\d)', blurb)
		if date_match:
			date_unf = date_match.group(1)
			date = datetime.datetime.strptime(date_unf, "%d %B %Y")

		entries.append(dict(org=polis.SCRAPER_ENUM.mfe, title=title, url=url, blurb=blurb, date=date))

	return entries
