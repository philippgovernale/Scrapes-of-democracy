import tkinter as tk
from tkinter import ttk

class StatusBar(tk.Frame):
	def __init__(self, parent, controller):
		super().__init__(parent)

		self.message_txt = tk.StringVar(self)
		self.status_txt = tk.StringVar(self, "Ready.")
		self.status_label = tk.Label(self, textvar=self.status_txt)
		self.message_label = tk.Label(self, textvar=self.message_txt)

		self.columnconfigure(0, weight=1, uniform='row')
		self.columnconfigure(1, weight=1, uniform='row')
		self.columnconfigure(2, weight=1, uniform='row')

		self.message_label.grid(row=0, column=0, sticky=tk.W)
		self.status_label.grid(row=0, column=1)
