
class Parser(object):
	
	def __init__(self, data):
		self.data = data
		self.parsed = False
		
	def get_results(self):
		return self.data
		
	def is_parsed(self):
		return self.parsed
		
	def set_parsed_data(self, d):
		self.parsed_data = d
		
	def get_parsed_data(self):
		return self.parsed_data