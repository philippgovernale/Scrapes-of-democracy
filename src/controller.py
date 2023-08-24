import webbrowser
import enum
from concurrent.futures import ThreadPoolExecutor
from collections import namedtuple

import polis
from polis import ScrapeGroupError
from gui.gui import View
from gui.toolbar import EntryViewFilters
from gui.main_area import EntrySortVar
from gui.colours import GuiColours

class Status(enum.Enum):
	IDLE = ("Ready.", "SystemButtonFace", "black")
	SCRAPING = ("Scraping ", "#ffc333", "#a52a2a")
	DONE = ("Finished :)", "green", "white")
	FAILED = ("Couldn't do it :(", "red", "white")

	def __init__(self, text: str, bg_colour: str, fg_colour):
		self.text = text
		self.bg_colour = bg_colour
		self.fg_colour = fg_colour

class Controller():
	def __init__(self, model):
		self.entry_sort_var = EntrySortVar.TITLE
		self._status = Status.IDLE
		self.selected_entry_wdgs = None
		self.selected_entry = None
		self.displayed_orgs = {scraper: True for scraper in polis.SCRAPERS}
		self.entry_view_filter = EntryViewFilters.CURRENT

		self.model = model
		self.view = View(self)
		self.populate_entries()

		self.view.display()

		self.model.scraper_data.save_data()

	@property
	def status(self) -> Status:
		return self._status

	@status.setter
	def status(self, new_status: Status) -> None:
		if self._status == Status.SCRAPING:
			self.view.root.after_cancel(self.anim_job)

		self._status = new_status
		self.view.statusbar.status_txt.set(new_status.text)
		self.view.statusbar.config(bg=new_status.bg_colour)
		self.view.statusbar.status_label.config(bg=new_status.bg_colour)
		self.view.statusbar.status_label.config(fg=new_status.fg_colour)
		self.view.statusbar.message_label.config(bg=new_status.bg_colour)
		self.view.statusbar.message_label.config(fg=new_status.fg_colour)

		#make done a transient state that after a set time becomes IDLE
		if new_status == Status.DONE:
			def change_status(status):
				self.status = status

			self.view.root.after(4000, lambda status=Status.IDLE : change_status(status))

		elif new_status == Status.SCRAPING:
			self.view.toolbar.set_refresh_btn_state(is_enabled=False)
			self.anim_state = True #two states hence bool

			def scrape_animation():
				if self._status == Status.SCRAPING:
					self.anim_job = self.view.root.after(250, scrape_animation)

				anim_ch = '/' if self.anim_state else '\\'
				self.view.statusbar.status_txt.set(Status.SCRAPING.text + anim_ch)

				self.anim_state = not self.anim_state

			scrape_animation()

		if new_status in {Status.IDLE, Status.DONE}:
			self.view.toolbar.set_refresh_btn_state(is_enabled=True)

	def show_filter_org_window(self) -> None:
		self.view.toolbar.filter_org_window.deiconify()

	def select_entry_filter(self, filter) -> None:
		filter = filter.get()
		self.entry_view_filter = EntryViewFilters(filter)
		self.update_entry_view()

	def filter_entries_by_org(self) -> None:
		self.view.toolbar.filter_org_window.withdraw()

		for org, state in self.view.toolbar.filter_org_window.org_checkbuttons:
			self.displayed_orgs[org] = state.get()

		self.update_entry_view()

	def _get_scrape_orgs(self):
		return polis.SCRAPERS

	def refresh_all(self) -> None:
		self.status = Status.SCRAPING
		self.view.toolbar.set_refresh_btn_state(is_enabled=False)

		#run scraping in a different thread with coroutines
		thread = ThreadPoolExecutor(max_workers=1)
		scrape_future = thread.submit(self.model.scrape, polis.SCRAPERS)
		scrape_future.add_done_callback(self._refresh_complete)

	def refresh_selected(self) -> None:
		self.view.toolbar.refresh_selected_window.withdraw()
		self.status = Status.SCRAPING

		enabled_orgs: list[polis.SCRAPER_ENUM] = []
		for org, state in self.view.toolbar.refresh_selected_window.org_checkbuttons:
			is_enabled = state.get()

			if is_enabled:
				enabled_orgs.append(org)

		thread = ThreadPoolExecutor(max_workers=1)
		scrape_future = thread.submit(self.model.scrape, enabled_orgs)
		scrape_future.add_done_callback(self._refresh_complete)

	def _refresh_complete(self, scrape_future) -> None:
		scraper_exceptions = scrape_future.exception()
		if scraper_exceptions:
			print(scraper_exceptions)
			error_msg = self.model.get_scraping_exceptions_msg(scraper_exceptions.scraper_exceptions)
			self.status = Status.FAILED
			self.view.show_error(error_msg)
			self.status = Status.IDLE
			return

		self.status = Status.DONE
		self.view.toolbar.set_refresh_btn_state(is_enabled=True)

		#Select Date scraped sorting so that new entries always show on top
		self.entry_sort_var = EntrySortVar.DATE_SCR
		self.view.main_area.entry_list_area.sort_entry_bar.update_headings_weight(self.view.main_area.entry_list_area.sort_entry_bar.date_scraped)
		self.update_entry_view()

		n_new_entries = len(self.model.scraper_data.get_new_entries())
		new_entries_txt = "{} new entries".format(n_new_entries)
		self.view.statusbar.message_txt.set(new_entries_txt)
		self.view.statusbar.after(4000, lambda : self.view.statusbar.message_txt.set(""))

	def select_entry(self, entry, entry_wdgs: list) -> None:
		#if selected_entry_wdgs is not None then we need to revert the old widgets back to the unselected colour
		if self.selected_entry_wdgs and entry_wdgs != self.selected_entry_wdgs:
			if self.selected_entry.entry_user_data.seen:
				widget_colour = GuiColours.ENTRY_READ.value
			else:
				widget_colour = GuiColours.ENTRY_UNREAD.value

			self.view.main_area.entry_list_area.change_entry_bg(self.selected_entry_wdgs, widget_colour)
			self.view.main_area.entry_list_area.change_text_fg(self.selected_entry_wdgs, GuiColours.ENTRY_NOT_SELECTED_FG.value)

		self.selected_entry = entry
		entry.entry_user_data.seen = True

		self.update_detail_view(entry)
		self.view.main_area.entry_list_area.change_entry_bg(entry_wdgs, GuiColours.ENTRY_SELECTED_BG.value)
		self.view.main_area.entry_list_area.change_text_fg(entry_wdgs, GuiColours.ENTRY_SELECTED_FG.value)
		self.selected_entry_wdgs = entry_wdgs

	def toggle_entry_important(self) -> None:
		if not self.selected_entry:
			return

		self.selected_entry.entry_user_data.important = not self.selected_entry.entry_user_data.important

		important_marker_colour = GuiColours.IMPORTANT_MARKER if self.selected_entry.entry_user_data.important else GuiColours.ENTRY_SELECTED_BG
		self.selected_entry_wdgs.entry_important_marker.config(bg=important_marker_colour.value)

	def toggle_entry_read(self) -> None:
		if not self.selected_entry:
			return

		self.selected_entry.entry_user_data.seen = not self.selected_entry.entry_user_data.seen

	def open_url_webbrowser(self) -> None:
		webbrowser.open(self.selected_entry.entry_data.url)

	def change_entries_sort(self, widget, sort_type: EntrySortVar) -> None:
		self.entry_sort_var = sort_type
		self.view.main_area.entry_list_area.sort_entry_bar.update_headings_weight(widget)
		self.update_entry_view()

	def update_entry_view(self) -> None:
		self.selected_entry_wdgs = None
		self.repopulate_entries()

	def update_detail_view(self, entry) -> None:
		def format_data_for_detail_view(entry) -> tuple[str, str, str, str, str]:
			entry_data = entry.entry_data

			title_str = entry_data.title
			org_str = entry_data.org.value.name
			date_str = "Due by:   {date}".format(date= entry_data.date)
			blurb_str = "No blurb available. Check website." if not entry_data.blurb else entry_data.blurb
			url_str = entry_data.url
			return (title_str, org_str, date_str, blurb_str, url_str)

		title_str, org_str, date_str, blurb_str, url_str = format_data_for_detail_view(entry)

		self.view.main_area.detail_area.title_str.set(title_str)
		self.view.main_area.detail_area.org_str.set(org_str)
		self.view.main_area.detail_area.closing_date_str.set(date_str)
		self.view.main_area.detail_area.blurb_str.set(blurb_str)
		self.view.main_area.detail_area.url_str.set(url_str)

		title_str_colour = entry.entry_data.org.value.colour
		self.view.main_area.detail_area.org_text.config(fg=title_str_colour)

	def populate_entries(self) -> None:

		def format_data_for_entry_list(entry) -> tuple[str, str, str, str]:
			#extracts data from Entry structure and applies formatting for view
			CHAR_LEN_TITLE = 13

			n_days = entry.entry_data.days_remaining
			match entry.entry_data.days_remaining:
				case "EXPIRED" | 'No date' | 'Today':
					date_exp_str = f"{n_days}"
				case 1:
					date_exp_str = f"{n_days} day"
				case _:
					date_exp_str = f"{n_days} days"

			date_scr_str = "{n_days} days ago".format(n_days= entry.entry_user_data.days_ago_scraped)

			#Shorten the title
			title_word_list = entry.entry_data.title.split(" ")
			truncated_title = " ".join(title_word_list[:CHAR_LEN_TITLE - 1])
			if len(title_word_list) > CHAR_LEN_TITLE:
				truncated_title = truncated_title + "..."

			org_name = entry.entry_data.org.value.name

			return (truncated_title, org_name, date_exp_str, date_scr_str)

		entries = self._get_entries_to_display()
		if not entries:
			return

		for entry in entries:
			bg_colour: str = GuiColours.ENTRY_READ.value if entry.entry_user_data.seen else GuiColours.ENTRY_UNREAD.value
			important_marker_colour: str = GuiColours.IMPORTANT_MARKER.value if entry.entry_user_data.important else bg_colour
			org_txt_colour: str = entry.entry_data.org.value.colour

			formatted_entry_details : tuple[str, str, str, str] = format_data_for_entry_list(entry)
			colours = (bg_colour, important_marker_colour, org_txt_colour)

			self.view.main_area.entry_list_area.add_entry(entry, formatted_entry_details, colours)

	def repopulate_entries(self) -> None:
		self.view.main_area.entry_list_area.depopulate()
		self.populate_entries()

	def _get_entries_to_display(self):

		def filter(self, entries_list: list) -> list:
			#Filter org
			entries_list = [entry for entry in entries_list if self.displayed_orgs[entry.entry_data.org]]

			match self.entry_view_filter:
				case EntryViewFilters.READ:
					entries_list = [entry for entry in entries_list if entry.entry_user_data.seen]
				case EntryViewFilters.UNREAD:
					entries_list = [entry for entry in entries_list if not entry.entry_user_data.seen]
				case EntryViewFilters.IMPORTANT:
					entries_list = [entry for entry in entries_list if entry.entry_user_data.important]
				case EntryViewFilters.CURRENT:
					entries_list = [entry for entry in entries_list if entry.entry_data.current]
				case EntryViewFilters.LAPSED:
					entries_list = [entry for entry in entries_list if not entry.entry_data.current]

			return entries_list

		entries_list = self.model.scraper_data.get_all_entries()

		entries_list = filter(self, entries_list)
		sorted_entry_list = self.model.sort_entries(entries_list, self.entry_sort_var)

		return sorted_entry_list
