from celery.task import task

from parser import KeywordExtracter, SourceCiter, StripTags

# crawldata is in form {"url": url, "links": final_links, "html":str(html)}

@task
def parse(crawldata, p):
	"""
	Parse celery task. Calls parse on specified parser and returns the results.
	"""
	return_data = crawldata
	
	if p == "keyword":
		parser_module = KeywordExtracter(crawldata)
	elif p == "citer":
		parser_module = SourceCiter(crawldata)
	elif p == "strip":
	   parser_module = StripTags(crawldata)
	else:
		raise Exception("Parser unknown")
	
	parser_module.parse()
	return_data["parse_results"] = parser_module.get_parsed_data()
	del return_data['html']
	return return_data