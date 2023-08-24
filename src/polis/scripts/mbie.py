import datetime
import sys

import polis
from polis._scrapers import _get_soup_urllib
from utils import *

name = 'MBIE'
url = 'https://www.mbie.govt.nz/have-your-say/'
colour = '#006272'

async def scrape_mbie_consultations(get_html_func=_get_soup_urllib) -> list[dict]:
	url = sys.modules[__name__].url
	name = sys.modules[__name__].name

	html_soup = get_html_func(url)

	html_entries = html_soup.find_all('div', {'class':'listing-item item-open'})

	entries = []
	for html_entry in html_entries:
		div = html_entry.find('div', {'class':'submission-details'})

		title = clean_str(str(div.a.string))
		url = clean_str(str(div.a.get('href')))
		blurb = clean_str(str(div.p.string))

		date_unf = clean_str(str(div.span.string))
		date_unf = date_unf.replace('Submissions due: ','').strip().split(',')[0]
		date = datetime.datetime.strptime(date_unf, "%d %B %Y")

		entries.append(dict(polis.SCRAPER_ENUM.mbie, title=title, url=url, blurb=blurb, date=date))

	return entries
