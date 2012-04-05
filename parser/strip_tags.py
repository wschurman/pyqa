from parser import Parser

class StripTags(Parser):
	"""
	Cites the page as a source.
	"""
	def parse(self):
		if not self.data:
			print "Must init data in parser"