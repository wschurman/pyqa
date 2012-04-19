from celery.task import task

import parser

# crawldata is in form {"url": url, "links": final_links, "html":str(html)}

@task
def parse(crawldata, p):
	"""
	Parse celery task. Calls parse on specified parser and returns the results.
	"""
	return_data = crawldata
	
	try:
 		class_ = getattr(parser, p)
		parser_module = class_(crawldata)
	except Exception:
		raise Exception("Parser unknown")
	
	parser_module.parse()
	return_data["parse_results"] = parser_module.get_parsed_data()
	del return_data['html']
	return return_data