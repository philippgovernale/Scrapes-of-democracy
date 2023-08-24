import tkinter as tk
import tkinter.messagebox

from gui.toolbar import ToolBar
from gui.main_area import MainArea
from gui.statusbar import StatusBar

class View():
	def __init__(self, controller):
		self.windows_blur_fix()
		root = tk.Tk()
		root.title("Scrap(e)s of Democracy")
		root.state('zoomed')

		self.toolbar = ToolBar(root,controller)
		self.toolbar.pack(anchor=tk.W, fill=tk.X)

		self.main_area = MainArea(root, controller)
		self.main_area.pack(fill=tk.BOTH, expand=True)

		self.statusbar = StatusBar(root, controller)
		self.statusbar.pack(fill=tk.BOTH)

		self.root = root

	@staticmethod
	def windows_blur_fix():
		try:
			from ctypes import windll
		except Exception:
			pass
		else:
			windll.shcore.SetProcessDpiAwareness(1)

	def display(self):
		self.root.mainloop()

	def show_error(self, message):
		tkinter.messagebox.showerror(message=message)
