import pika
import sys
import json
from django.conf import settings

def mq_newuser(data):
    credentials = pika.PlainCredentials(settings.CRED_USERNAME, settings.CRED_PASSWORD)
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=settings.PIKA_CONNECTION))
    channel = connection.channel()

    channel.exchange_declare(exchange='account', exchange_type='topic', durable=True)

    channel.basic_publish(exchange='account',
                        routing_key='',
                        body=data,
                        properties=pika.BasicProperties(delivery_mode = 2,)
                        )
    print(" [x] Sent %r to RabbitMQ" % data)
    connection.close()
