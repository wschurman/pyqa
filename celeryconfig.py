BROKER_URL = "amqp://celery:9PxyWcTUNDr6UZB6qcU@ec2-184-73-79-244.compute-1.amazonaws.com:5672/celeryv"

CELERY_RESULT_BACKEND = "mongodb"
CELERY_MONGODB_BACKEND_SETTINGS = {
    "host": "ec2-184-73-79-244.compute-1.amazonaws.com",
    "port": 27017,
    "database": "celery",
	"user": "celery",
	"password": "9PxyWcTUNDr6UZB6qcU",
    "taskmeta_collection": "my_taskmeta_collection",
}

CELERY_IMPORTS = ("crawl", "parse", "test")