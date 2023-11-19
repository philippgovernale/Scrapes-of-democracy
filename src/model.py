import traceback
import pickle
import datetime
import enum
from collections import namedtuple
from operator import attrgetter
from urllib.error import *
from dataclasses import dataclass

import polis
from gui.main_area import EntrySortVar

@dataclass(frozen=True)
class Consultation():
	org: polis.SCRAPER_ENUM
	title: str
	url: str
	blurb: str
	_date: datetime.datetime

	@classmethod
	def from_dict(cls, data_dict):
		org = data_dict['org']

		title = data_dict['title']
		url = data_dict['url']
		blurb = data_dict['blurb']
		_date = data_dict['date']
		return cls(org, title, url, blurb, _date)

	@property
	def date(self) -> str:
		if not self._date:
			return ''
		return self._date.strftime("%d/%m/%Y")

	@property
	def days_remaining(self):
		if not self._date:
			return 'No date'
		elif not self.open:
			return 'CLOSED'
		elif self.is_today:
			return 'Today'

		delta = datetime.datetime.date(self._date) - datetime.date.today()
		return delta.days

	@property
	def open(self) -> bool:
		if not self._date:
			return True
		return datetime.datetime.date(self._date) >= datetime.date.today()

	@property
	def is_today(self) -> bool:
		return datetime.datetime.date(self._date) == datetime.date.today()

	def __str__(self):
		return "{}\n".format(self.title)
	def __eq__(self, other):
		return self.title == other.title and self.url == other.url
	def __hash__(self):
		return hash((self.url))

class EntryUserData():
	def __init__(self):
		self.seen = False
		self.important = False

		#date the entry was *first* scraped
		self.scrape_date = datetime.datetime.now()

	@property
	def days_ago_scraped(self):
		delta = datetime.datetime.now() - self.scrape_date
		return delta.days

class Entry(namedtuple('Entry', 'entry_data entry_user_data')):
	def __eq__(self, other):
		return self.entry_data == other.entry_data
	def __hash__(self):
		return hash(self.entry_data)

class ScraperGroupDataHandler():
	def __init__(self, data_path: str):
		self.data_path: str= data_path
		self.scraper_data: list[Entry] = self.load_data()
		self.old_scraper_data: list[Entry] = []

	def save_data(self) -> None:
		with open(self.data_path, 'wb') as f:
			pickle.dump(self.get_all_entries(), f)

	def load_data(self) -> list[Entry]:
		try:
			with open(self.data_path, 'rb') as f:
				data = pickle.load(f)
		except IOError:
			data = []

		return data

	def update_data(self, new_data: list[Entry]) -> None:
		self.old_scraper_data = self.get_all_entries()
		self.scraper_data = new_data

	def get_new_entries(self) -> list[Entry]:
		#compare newly scraped data with old data

		return [entry for entry in self.scraper_data if entry not in self.old_scraper_data]

	def get_all_entries(self) -> list[Entry]:
		new = self.scraper_data
		old = self.old_scraper_data

		return list(set(old) | set(new))

class Model():
	def __init__(self, data_path: str) -> None:
		self.scraper_data = ScraperGroupDataHandler(data_path)

	def scrape(self, orgs_to_scrape: list) -> None:
		res_dict, exception = polis.scrape(orgs_to_scrape)

		res_cons = [Consultation.from_dict(cons) for cons in res_dict]
		res_entry = [Entry(entry, EntryUserData()) for entry in res_cons]

		self.scraper_data.update_data(res_entry)

		if exception:
			raise exception

	@staticmethod
	def sort_entries(entries: list[Entry], sort_type: EntrySortVar) -> list[Entry]:
		#Since some entries don't have any entry date we need to do some special handling to ensure the sort works
		if sort_type == EntrySortVar.DATE_EXP:
			entries_cpy = entries
			entries = [entry for entry in entries if entry.entry_data._date]
			no_date_entries = [entry for entry in entries_cpy if not entry.entry_data._date]

		#to the scraping date sorting we need to reverse the sort as we want the later
		#(i.e. newest) to show before the earlier dates
		reversed = True if sort_type == EntrySortVar.DATE_SCR else False

		sorted_entries = sorted(entries, key=attrgetter(sort_type.value), reverse=reversed)

		if sort_type == EntrySortVar.DATE_EXP:
			sorted_entries = sorted_entries + no_date_entries

		return sorted_entries

	@staticmethod
	def get_scraping_exceptions_msg(exceptions) -> str:
		msg = ""

		scraper_msgs: list[str] = []
		intro = "{n} scrapers failed.\n\n".format(n=len(exceptions))

		for exception in exceptions:
			scraper_msg = ""

			if isinstance(exception, (HTTPError, URLError)):
				reason = exception.reason
			exception_type = type(exception)

			#get info for the first element in the traceback
			fp, line, func_name, text = traceback.extract_tb(exception.__traceback__)[0]

			print(traceback.extract_tb(exception.__traceback__)[0])

			match exception:
				case HTTPError():
					scraper_msg = (
						f'The scraper script {fp} raised an HTTPError with reason {reason} on line {line}. '
						f'This likely occured because they detected and blocked our scraping attempt. '
						f'Please visit the website to check for updates \n\n.'
					)
				case URLError():
					scraper_msg = (
						f'The scraper script {fp} raised a URLError with reason {reason} on line {line}'
						f'Check whether the link in the scraper file is still live.\n\n'
					)
				case _:
					scraper_msg = (
						f'The scraper script {fp} raised an {exception_type} on line {line}\n\n'
					)

			scraper_msgs.append(scraper_msg)

		combined_scraper_msgs = "".join(scraper_msgs)
		msg = intro + combined_scraper_msgs

		return msg
