from parser import Parser
from bs4 import BeautifulSoup

class KeywordExtracter(Parser):
	"""
	Extracts the keywords from the html
	"""
	def parse(self):
		if not self.data:
			print "Must init data in parser"
		
		b = BeautifulSoup(self.data["html"])
		print "Data Title: ", b.title
		
		keywords = []
		
		#keywords.extend(b.find('meta', { "name" : "keywords"}))
		if b.title:
			keywords.append(b.title.get_text())
		
		self.set_parsed_data(keywords)
		
	
