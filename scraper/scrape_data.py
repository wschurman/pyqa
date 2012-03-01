class ScrapeData:
	
	def __init__(self, url, depth):
		self.url = url
		self.scraped = False
		self.depth = depth
	
	def __hash__(self):
		return self.url
	
	def scraped(self):
		return self.scraped
	
	def get_url(self):
		return self.url
	
	def set_content(self, c):
		self.content = c
		self.scraped = True
		
	def get_content(self):
		return self.content
	
	def get_depth(self):
		return self.depth
		
	def set_parsed_data(self, d):
		self.data = d
		
	def get_parsed_data(self):
		return self.data