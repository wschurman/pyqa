from parser import Parser
from bs4 import BeautifulSoup

class StripTags(Parser):
	"""
	Cites the page as a source.
	"""
	def parse(self):
		if not self.data:
			print "Must init data in parser"
		
		b = BeautifulSoup(self.data["html"])
		
		print "Got %s" % b.body.get_text(" ", strip=True)
		
		self.set_parsed_data(str(''.join([x for x in b.body.get_text(" ", strip=True) if ord(x) < 128])))