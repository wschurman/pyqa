from celery.task import task
from scraper import Scraper

@task
def add(x, y):
    return x + y

@task
def crawl(url, maxdepth):
	if maxdepth == 0: return
	print "hello"