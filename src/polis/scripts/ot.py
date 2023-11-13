import datetime
import sys

import polis
from polis._scrapers import _get_soup_urllib
from utils import *

name = 'Oranga Tamariki'
url = 'https://www.orangatamariki.govt.nz/consultations/'
colour = 'black'

async def scrape_ot_consultations(get_html_func=_get_soup_urllib) -> list[dict]:
	url = sys.modules[__name__].url
	name = sys.modules[__name__].name

	html_soup = get_html_func(url)

	html_entries = html_soup.find('ul', {'id': 'a3807_ajax-results-items'}).find_all('li')

	#No consultations available
	if not html_entries:
		print("no entries")
		return []

	entries = []
	for html_entry in html_entries:
		title = clean_str(html_entry.a.span.text)
		url = clean_str(html_entry.a.get('href'))
		blurb = clean_str(html_entry.a.p.string)
		date_unf = clean_str(html_entry.find('p', {'class': 'b-publication-date-and-read-time'}).time.text)

		if date_unf.lower() == 'today':
			date_obj = datetime.datetime.combine(datetime.date.today(), datetime.datetime.min.time())
		else:
			date_obj = datetime.datetime.strptime(date_unf, "%d %B %Y")

		entries.append(dict(org=polis.SCRAPER_ENUM.ot, title=title, url=url, blurb=blurb, date=date_obj))

	return entries
