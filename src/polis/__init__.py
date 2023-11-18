import pkgutil
import enum
import inspect
import asyncio
from collections import namedtuple

import polis.scripts

# Traverse the scripts folder to generate an enum for all the scrapers

Scraper = namedtuple('Scraper', ['name', 'mod', 'func', 'url', 'colour'])
scripts = polis.scripts
_scraper_dict = {}

for _importer, _modname, _ in pkgutil.iter_modules(scripts.__path__):
	_m = _importer.find_module(_modname).load_module(_modname)

	_is_function_in_module = lambda obj: inspect.isfunction(obj) and inspect.getmodule(obj) == _m
	_func = inspect.getmembers(_m, _is_function_in_module)[0][1]

	_scraper_dict[_modname] = Scraper(_m.name, _m, _func, _m.url, _m.colour)

SCRAPER_ENUM = enum.Enum('SCRAPER_ENUM', _scraper_dict)
SCRAPERS = [scraper for scraper in SCRAPER_ENUM]

class ScrapeGroupError(Exception):
	"""Raised when one of the scrapers in a group raised an exception"""
	def __init__(self, exceptions):
		self.scraper_exceptions = exceptions

async def _scrape(orgs_to_scrape: list[SCRAPER_ENUM], silent_fail):
	scraper_funcs = [scraper.value.func() for scraper in orgs_to_scrape]

	all_scrapers_results = await asyncio.gather(*scraper_funcs, return_exceptions=True)

	data, exceptions, group_exception = [], [], None
	for scraper_result in all_scrapers_results:
		if isinstance(scraper_result, Exception):
			exceptions.append(scraper_result)
			continue

		data.extend(scraper_result) #flatten

	if exceptions:
		group_exception = ScrapeGroupError(exceptions)
		if not silent_fail:
			raise group_exception

	if silent_fail:
		return (data, group_exception)
	else:
		return data

def scrape(orgs_to_scrape: list[SCRAPER_ENUM], silent_fail = True):
	"""
	Scrape the organisations provided in the input list

	Arg:
		List of polis.SCRAPER_ENUM objs

	Returns:
		List of dicts or exception objs for each organisation scraped
	"""
	return asyncio.run(_scrape(orgs_to_scrape, silent_fail = True))

def scrape_all():
	"""
	Scrape all the organisations that have a scraper in the scripts folder.

	Returns:
		List of dicts or exception objs for each organisation scraped
	"""
	return asyncio.run(_scrape(SCRAPERS, silent_fail))
