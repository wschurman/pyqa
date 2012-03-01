
class Parser(object):
	
	def __init__(self, data):
		self.data = data
		self.parsed = False
		
	def get_results(self):
		return self.data
		
	def is_parsed(self):
		return self.parsed