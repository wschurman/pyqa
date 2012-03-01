from parser import Parser
from bs4 import BeautifulSoup

class KeywordExtracter(Parser):
	
	def parse(self):
		if not self.data:
			print "Must init data in parser"
		
		b = BeautifulSoup(self.data.get_content())
		
		keywords = []
		
		keywords.extend(b.find('meta', { "name" : "keywords"}))
		keywords.add(b.title.get_text())
		
		self.data.set_parsed_data(keywords)
		
	
