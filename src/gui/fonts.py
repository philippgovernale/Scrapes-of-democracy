import tkinter as tk

def set_font(widget, font):
	widget.configure(font=font)

def get_font(widget, weight='normal',size=None):
	font = widget.cget('font')
	font = tk.font.nametofont(font)
	newfont = font.copy()
	if not size:
		size = font.cget('size')
	newfont.configure(weight=weight, size=size)
	return newfont
