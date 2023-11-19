import datetime
import sys

import polis
from polis._scrapers import _get_soup_urllib
from utils import *

name = 'Ministry of Housing and Urban Development'
url = 'https://consult.hud.govt.nz'
colour = '#003141'

async def scrape_hud_consultations(get_html_func=_get_soup_urllib) -> list[dict]:
	url = sys.modules[__name__].url
	name = sys.modules[__name__].name

	html_soup = get_html_func(url)

	current = html_soup.find(string='Open activities')
	print(current.parent.parent.next_sibling)

	#No consultations available
	if not current:
		return []

	entries = []

	html_entries = current.parent.parent.parent.find_all('div', {'class': 'col-md-6 col-lg-4'})

	for html_entry in html_entries:
		title = clean_str(html_entry.div.h3.a.string)
		url = clean_str(html_entry.div.h3.a.get('href'))
		blurb = None
		date_unf = clean_str(html_entry.find(string='Closes').parent.parent.text).replace('Closes ', '')


		if date_unf.lower() == 'today':
			date_obj = datetime.datetime.combine(datetime.date.today(), datetime.datetime.min.time())
		else:
			date_obj = datetime.datetime.strptime(date_unf, "%d %B %Y")

		entries.append(dict(org=polis.SCRAPER_ENUM.hud, title=title, url=url, blurb=blurb, date=date_obj))

	return entries


	for descendant in current.parent.parent.parent.ul.descendants:
		if descendant.name != 'li':
			continue
		html_entries.append(descendant)

		for html_entry in html_entries:
			title =  clean_str(str(html_entry.div.h3.a.string))
			url = clean_str(str(html_entry.div.h3.a.get('href')))
			blurb = clean_str(str(html_entry.div.p.string))
			date_unf = clean_str(str(html_entry.find('p', {'class': 'cs-date-delta'}).text).replace('Closes',''))

			if date_unf.lower() == 'today':
				date_obj = datetime.datetime.combine(datetime.date.today(), datetime.datetime.min.time())
			else:
				date_obj = datetime.datetime.strptime(date_unf, "%d %B %Y")

			entries.append(dict(org=polis.SCRAPER_ENUM.hud, title=title, url=url, blurb=blurb, date=date_obj))

	return entries
