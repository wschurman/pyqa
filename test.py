from celery.task import task
from celery.task.sets import subtask

@task
def add(x, y, callback=None):
	result = x + y
	if callback is not None:
		return subtask(callback).delay(result)
	return result
	
	
@task
def f2():
	print "Hello"
	print "Returning from f2"