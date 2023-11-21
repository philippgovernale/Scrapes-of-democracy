import enum
import tkinter as tk
from tkinter import ttk

class EntryViewFilters(enum.Enum):
	ALL = 'All'
	READ = 'Read'
	UNREAD = 'Unread'
	IMPORTANT = 'Important'
	OPEN = 'Open'
	CLOSED = 'Closed'

class ToolBar(tk.Frame):
	def __init__(self, parent, controller):
		super().__init__(parent, borderwidth=10)

		sel_entry_state = tk.StringVar(self)
		menu_entry_states = tuple(filter.value for filter in EntryViewFilters)

		self.filter_org_window = FilterWindow(controller, controller.filter_entries_by_org)
		self.refresh_selected_window = FilterWindow(controller, controller.refresh_selected)
		self.filter_org_window.withdraw()
		self.refresh_selected_window.withdraw()

		self.refresh_btn = ttk.Button(self, text='Refresh All', command=controller.refresh_all)
		self.refresh_some_btn = ttk.Button(self, text='Refresh', command=self.refresh_selected_window.deiconify)
		filter_org_btn = ttk.Button(self, text='Filter', command=self.filter_org_window.deiconify)
		entry_state_menu = ttk.OptionMenu(self, sel_entry_state, controller.entry_view_filter.value, *menu_entry_states)

		self.refresh_btn.pack(anchor=tk.W, side='left', ipady=3)
		self.refresh_some_btn.pack(anchor=tk.W, side='left', padx=[15,0], ipady=3)
		filter_org_btn.pack(anchor=tk.E, side='right', padx=15, ipady=3)
		entry_state_menu.pack(anchor=tk.E, side='right', ipady=3)

		self.filter_org_window.protocol('WM_DELETE_WINDOW', self.filter_org_window.withdraw)
		self.refresh_selected_window.protocol('WM_DELETE_WINDOW', self.refresh_selected_window.withdraw)
		sel_entry_state.trace('w', lambda var,index,mode,selected_filter=sel_entry_state: controller.select_entry_filter(selected_filter))

	def set_refresh_btn_state(self, is_enabled: bool) -> None:
		tk_btn_state = 'normal' if is_enabled else 'disabled'

		self.refresh_btn.config(state=tk_btn_state)
		self.refresh_some_btn.config(state=tk_btn_state)

class FilterWindow(tk.Toplevel):
	def __init__(self, controller, ok_btn_func):
		super().__init__(borderwidth=10)

		heading = tk.Label(self, text="Organisations")
		heading.pack()

		self.toggle_checkbtns_var = tk.BooleanVar(self, True)
		self.toggle_checkbtns_var.trace('w', lambda var,index,mode: self.toggle_checkbuttons())

		toggle_all_checkbtns_checkbutton = ttk.Checkbutton(self, variable=self.toggle_checkbtns_var)
		toggle_all_checkbtns_checkbutton.pack(anchor=tk.W)

		sep = ttk.Separator(self)
		sep.pack(fill=tk.X, pady=[0, 10])

		scrape_orgs = controller._get_scrape_orgs()

		self.org_checkbuttons = []
		for scrape_org in scrape_orgs:
			org_is_selected = tk.BooleanVar(self, True)

			org_checkbutton = ttk.Checkbutton(self, text=scrape_org.value.name, variable=org_is_selected)
			org_checkbutton.pack(anchor=tk.W)

			self.org_checkbuttons.append((scrape_org, org_is_selected))

		ok_btn = ttk.Button(self, text='Ok', command= ok_btn_func)
		ok_btn.pack(pady=10)

	def toggle_checkbuttons(self):
		for _ , checkbutton in self.org_checkbuttons:
			checkbutton.set(self.toggle_checkbtns_var.get())
