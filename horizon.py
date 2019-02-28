import asvmq
import requests
import asvprotobuf.sensor_pb2
import random
from google.protobuf.json_format import MessageToDict

LOGS_EXCHANGE_NAME = "logs"
GRAPH_EXCHANGE_NAME = "graph"
rabbitmq_hostname="localhost"
rabbitmq_port=5672
django_hostname = "localhost"

def callback(data, args):
    return requests.post("http://%s:8000/api/horizon/set/" % django_hostname, json={"roll": data.orientation.roll, "pitch": data.orientation.pitch, "accel": data.acceleration.x/100}).content

def laser_callback(data, args):
    data = MessageToDict(data)
    return requests.post("http://%s:8000/api/scan/set/" % django_hostname, json=data).content

#asvmq.Subscriber(topic_name='imu_data', object_type=asvprotobuf.sensor_pb2.Imu, callback=callback, hostname=rabbitmq_hostname, port=rabbitmq_port)
asvmq.Subscriber(topic_name='scan', object_type=asvprotobuf.sensor_pb2.LaserScan, callback=laser_callback, hostname=rabbitmq_hostname, port=rabbitmq_port)
