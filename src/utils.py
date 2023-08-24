def get_dmy_str(date_obj) -> str:
	return date_obj.strftime("%d/%m/%Y")

def clean_str(string: str) -> str:
	return string.replace('\n','').replace('\t','').replace('\r','').strip()
