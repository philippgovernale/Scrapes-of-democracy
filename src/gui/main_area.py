import enum
import tkinter as tk
import tkinter.font
from tkinter import ttk
from collections import namedtuple

from gui.colours import GuiColours
from gui.fonts import get_font, set_font

EntryWdgs = namedtuple('EntryWdgs', ['entry_important_marker', 'entry_frame', 'entry_org', 'entry_title', 'entry_date', 'scrape_datetime'])

class EntrySortVar(enum.Enum):
	#Enum representing the different variables by which the entries can be sorted.
	#The values represent the objects paths within the Entry structure
	ORG = 'entry_data.org.name'
	TITLE = 'entry_data.title'
	DATE_EXP = 'entry_data._date'
	DATE_SCR = 'entry_user_data.scrape_date'

class MainArea(ttk.PanedWindow):
	def __init__(self, parent, controller):
		super().__init__(parent, orient=tk.HORIZONTAL)

		self.detail_area = DetailArea(self, controller)
		self.entry_list_area = EntryListArea(self, controller)
		self.add(self.entry_list_area, weight=5)
		self.add(self.detail_area, weight=1)

class SortEntryBar(tk.Frame):
	def __init__(self, parent, controller):
		super().__init__(parent, bg=GuiColours.MAINAREA_BG.value)

		self.organisation = tk.Label(self, text='Organisation', bg=GuiColours.MAINAREA_BG.value)
		self.title = tk.Label(self, text='Title', bg=GuiColours.MAINAREA_BG.value)
		self.date_exp = tk.Label(self, text='Closes', bg=GuiColours.MAINAREA_BG.value)
		self.date_scraped = tk.Label(self, text='Scraped', bg=GuiColours.MAINAREA_BG.value)

		self.organisation.pack(side=tk.LEFT, padx=7)
		self.title.pack(side=tk.LEFT, fill=tk.X, expand=True)
		self.date_exp.pack(side=tk.RIGHT, padx=7)
		self.date_scraped.pack(side=tk.RIGHT, padx=14)

		self.organisation.bind("<Button-1>", lambda e,sort_type=EntrySortVar.ORG: controller.change_entries_sort(e.widget, sort_type))
		self.title.bind("<Button-1>", lambda e,sort_type=EntrySortVar.TITLE: controller.change_entries_sort(e.widget, sort_type))
		self.date_exp.bind("<Button-1>", lambda e,sort_type=EntrySortVar.DATE_EXP: controller.change_entries_sort(e.widget, sort_type))
		self.date_scraped.bind("<Button-1>", lambda e,sort_type=EntrySortVar.DATE_SCR: controller.change_entries_sort(e.widget, sort_type))

		self.bold_font = get_font(self.title, 'bold')
		self.normal_font = get_font(self.title, 'normal')

		#init bold font
		set_font(self.title, self.bold_font)

	#for widget in self.sort_options_wdgs:
	def update_headings_weight(self, selected_widget) -> None:
		set_font(selected_widget, self.bold_font)

		for widget in self.winfo_children():
			if widget != selected_widget:
				set_font(widget, self.normal_font)

class EntryListArea(tk.Frame):
	def __init__(self, parent, controller):
		super().__init__(parent, borderwidth=0, bg=GuiColours.MAINAREA_BG.value)
		self.controller = controller

		self.scrollbar = tk.Scrollbar(self, jump=True)
		self.scrollbar.pack(side='right', fill=tk.Y)

		self.sort_entry_bar = SortEntryBar(self, controller)
		self.sort_entry_bar.pack(anchor=tk.E, fill=tk.X, ipadx=10)

		self.entry_list = tk.Canvas(self, yscrollcommand=self.scrollbar.set, highlightthickness=0, bd=0)
		self.entry_list.pack(fill=tk.BOTH, expand=True)

		self.scrollbar.config(command=self.entry_list.yview)
		self.bind('<Configure>', lambda e: self.resize_entries())

	def add_entry(self, entry, formatted_entry_details, colours):
		shortened_title, org_name, date_exp_str, date_scr_str = formatted_entry_details
		bg_colour, important_marker_colour, org_txt_colour = colours

		#use of fixed width aligns labels. Width is in terms of text units so should work well on other resolutions too
		entry_frame = tk.Frame(self, bg=bg_colour, borderwidth=0)
		entry_important_marker = tk.Frame(entry_frame, bg=important_marker_colour, width=4)
		entry_org = tk.Label(entry_frame, text=org_name, bg=bg_colour, fg=org_txt_colour, anchor=tk.W, width=24)
		entry_title = tk.Label(entry_frame, text=shortened_title, bg=bg_colour)
		entry_exp_date = tk.Label(entry_frame, text=date_exp_str, bg=bg_colour, width=8)
		entry_scr_date = tk.Label(entry_frame, text=date_scr_str, bg=bg_colour)

		entry_important_marker.pack(side=tk.LEFT, anchor=tk.W, fill=tk.Y)
		entry_org.pack(padx=7, anchor=tk.W, side=tk.LEFT)
		entry_title.pack(side=tk.LEFT, fill=tk.X, expand=True)
		entry_exp_date.pack(side=tk.RIGHT, padx=7)
		entry_scr_date.pack(side=tk.RIGHT)

		entry_wdgs = EntryWdgs(entry_important_marker, entry_frame, entry_org, entry_title, entry_exp_date, entry_scr_date)

		entry_frame.bind("<Button-1>", lambda e,entry=entry,entry_wdgs=entry_wdgs: self.controller.select_entry(entry, entry_wdgs))
		entry_org.bind("<Button-1>", lambda e,entry=entry,entry_wdgs=entry_wdgs: self.controller.select_entry(entry, entry_wdgs))
		entry_title.bind("<Button-1>", lambda e,entry=entry,entry_wdgs=entry_wdgs: self.controller.select_entry(entry, entry_wdgs))
		entry_exp_date.bind("<Button-1>", lambda e,entry=entry,entry_wdgs=entry_wdgs: self.controller.select_entry(entry, entry_wdgs))

		bold_font = get_font(entry_org, weight='bold')
		entry_org.config(font=bold_font)

		size: tuple[int,int,int,int] = self.entry_list.bbox('all')
		entry_y: int = size[3] if size else 0

		window = self.entry_list.create_window(0, entry_y, window=entry_frame, anchor=tk.NW, width=self.entry_list.winfo_width(), height=50)
		self.entry_list.config(scrollregion=self.entry_list.bbox('all'))

	def resize_entries(self) -> None:
		for entry in self.entry_list.find_withtag('all'):
			self.entry_list.itemconfigure(entry, width=self.winfo_width()-self.scrollbar.winfo_width())

		self.scrollbar.tkraise()

	def change_entry_bg(self, widget_list: list, bg: str) -> None:
		#skip mark important
		for widget in widget_list[1:]:
			widget.config(bg=bg)

		#only change important marker colour if it is not important
		if widget_list.entry_important_marker.cget('bg') != GuiColours.IMPORTANT_MARKER.value:
			widget_list.entry_important_marker.config(bg=bg)

	def change_text_fg(self, widget_list: list, fg: str):
		for widget in widget_list[3:]:
			widget.config(fg=fg)

	def depopulate(self) -> None:
		for widget in self.entry_list.find_withtag('all'):
			self.entry_list.delete(widget)

class WrappingLabel(tk.Label):
	def __init__(self, master=None, **kwargs):
		tk.Label.__init__(self, master, **kwargs)
		self.bind('<Configure>', lambda e: self.config(wraplength=self.winfo_width()))

class DetailArea(tk.Frame):
	def __init__(self, parent, controller):
		super().__init__(parent, borderwidth=0, bg=GuiColours.MAINAREA_BG.value)

		self.title_str = tk.StringVar(self)
		self.org_str = tk.StringVar(self)
		self.closing_date_str = tk.StringVar(self)
		self.blurb_str = tk.StringVar(self)
		self.url_str = tk.StringVar(self)

		title_font = tk.font.Font(size='15')
		org_font = tk.font.Font(size='12', weight='bold', underline=0)
		date_font = tk.font.Font(size='9', weight='bold', underline=0)
		blurb_font = tk.font.Font(size='10')

		title_text = WrappingLabel(self, width=40, wraplength=40, textvar=self.title_str, bg=GuiColours.MAINAREA_BG.value, font=title_font)

		overview_area = tk.Frame(self, borderwidth=25, bg=GuiColours.DETAILAREA_OVERVIEW_BG.value)
		self.org_text = tk.Label(overview_area, textvar=self.org_str, anchor=tk.W, font=org_font, bg=GuiColours.DETAILAREA_OVERVIEW_BG.value)
		closing_date_text = tk.Label(overview_area, textvar=self.closing_date_str, anchor=tk.W, font=date_font, fg='gray25', bg=GuiColours.DETAILAREA_OVERVIEW_BG.value)

		blurb_text = WrappingLabel(self, width=40, wraplength=40, textvar=self.blurb_str, anchor=tk.W, justify=tk.LEFT, bg=GuiColours.MAINAREA_BG.value, font=blurb_font)
		url_text = WrappingLabel(self, width=40, wraplength=40, textvar=self.url_str, anchor=tk.W, bg=GuiColours.MAINAREA_BG.value)

		detail_command_area = tk.Frame(self, bg=GuiColours.MAINAREA_BG.value)
		open_button = ttk.Button(detail_command_area, text='Open', command=controller.open_url_webbrowser)
		read_unread_button = ttk.Button(detail_command_area, text='Read/Unread', command=controller.toggle_entry_read)
		important_button = ttk.Button(detail_command_area, text ='(Un)/Important', command=controller.toggle_entry_important)

		sep1 = ttk.Separator(self, orient=tk.HORIZONTAL)
		sep2 = ttk.Separator(self, orient=tk.HORIZONTAL)

		title_text.pack(pady=[10, 30], padx=25, fill=tk.X)
		sep1.pack(fill=tk.X)

		self.org_text.pack(pady=0, anchor=tk.W)
		closing_date_text.pack(pady=[8,0], anchor=tk.W)
		overview_area.pack(fill=tk.X)

		sep2.pack(fill=tk.X, pady=0)
		blurb_text.pack(pady=30, padx=25, fill=tk.X)

		open_button.pack(side='left', anchor=tk.S, padx=10, pady=10, ipadx=5, ipady=3, fill=tk.X, expand=True)
		read_unread_button.pack(side='left', anchor=tk.S, padx=10, pady=10, ipadx=5, ipady=3, fill=tk.X, expand=True)
		important_button.pack(side='right', anchor=tk.S, padx=10, pady=10, ipadx=5, ipady=3, fill=tk.X, expand=True)

		detail_command_area.pack(anchor=tk.S, side='bottom', ipady=0, fill=tk.BOTH)
		url_text.pack(pady=5, padx=25, side='bottom', fill=tk.X)
