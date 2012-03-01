from scraper import ScrapeData
from parser import KeywordExtracter, SourceCiter

#@task
def parse(scrapedata, p):
	
	if p == "keyword":
		parser_module = KeywordExtracter(scrapedata)
	elif p == "citer":
		parser_module = SourceCiter(scrapedata)
	else:
		raise Exception("Parser unknown")
	
	parser_module.parse()
	return parser_module.get_results()


print parse(ScrapeData("http://google.com", 4), "keyword")