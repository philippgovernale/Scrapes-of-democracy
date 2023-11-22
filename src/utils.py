import re

def get_dmy_str(date_obj) -> str:
	return date_obj.strftime("%d/%m/%Y")

def clean_str(string: str) -> str:
	temp1 = re.sub(' +', ' ', string.replace('\t','').replace('\r','').strip())
	return re.sub('(?<=\n) +','', temp1) #remove leading whitespaces from paragraphs with positive lookbehind
