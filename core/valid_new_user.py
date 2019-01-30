import pika
import sys
import json
from django.conf import settings

def mq_newuser(data):
    credentials = pika.PlainCredentials(settings.LANGUAGE_CODE, settings.LANGUAGE_CODE)
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=settings.LANGUAGE_CODE))
    channel = connection.channel()

    channel.exchange_declare(exchange='account', exchange_type='topic', durable=True)

    #Transform data
    def jdefault(data):
        return data.__dict__

    message = json.dumps(data, default=jdefault)

    routing = data
    if not routing:
        sys.stderr.write("Usage: %s [routing_key]...\n" % sys.argv[0])
        sys.exit(1)

    channel.basic_publish(exchange='account',
                        routing_key=routing[0],
                        body=message,
                        properties=pika.BasicProperties(delivery_mode = 2,)
                        )
    print(" [x] Sent %r to RabbitMQ" % data)
    connection.close()
