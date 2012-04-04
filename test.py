import mechanize
from urlparse import urljoin

url = "http://news.ycodededembinator.com/"

br = mechanize.Browser()
br.set_handle_robots(False)
br.set_handle_referer(False)
try:
   response = br.open(url)
except:
   raise mechanize.URLError(url)

for link in br.links():
	furl = urljoin(url, link.url) #TODO: fix
	print furl
	
# print response.read()