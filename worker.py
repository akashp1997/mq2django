import requests
import pika
import json

LOGS_EXCHANGE_NAME = "logs"
GRAPH_EXCHANGE_NAME = "graph"
rabbitmq_hostname="localhost"
rabbitmq_port=5672
django_hostname = "localhost"

def log_callback(ch, method, properties, body):
    body = body.decode().replace("\n", "")
    data = json.loads(body)
    data["message"] = json.loads(data["message"].replace("'", '"'))
    requests.post("http://%s:8000/api/logs/set/" % django_hostname, json=data).content

def graph_callback(ch, method, properties, body):
    body = body.decode().replace("\n", "")
    data = json.loads(body)
    requests.post("http://%s:8000/api/graph/set/" % django_hostname, json=data).content

try:
    channel = pika.BlockingConnection(pika.ConnectionParameters(rabbitmq_hostname, rabbitmq_port)).channel()
    channel.exchange_declare(exchange=LOGS_EXCHANGE_NAME, exchange_type="fanout")
    queue_name = channel.queue_declare().method.queue
    channel.queue_bind(exchange=LOGS_EXCHANGE_NAME, queue=queue_name)
    #channel.basic_consume(log_callback, queue=queue_name)
    channel.exchange_declare(exchange=GRAPH_EXCHANGE_NAME, exchange_type="fanout")
    queue_name = channel.queue_declare().method.queue
    channel.queue_bind(exchange=GRAPH_EXCHANGE_NAME, queue=queue_name)
    channel.basic_consume(graph_callback, queue=queue_name)
    channel.start_consuming()
except requests.exceptions.ConnectionError as error:
    print("Could not connect to Django.\n" + str(error))
