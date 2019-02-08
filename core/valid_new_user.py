import pika
from django.conf import settings

def mq_newuser(routing,data):
    credentials = pika.PlainCredentials(settings.MQ_USER, settings.MQ_PASSWORD)
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=settings.MQ_CONNECTION, credentials=credentials))
    channel = connection.channel()
    channel.exchange_declare(exchange='account', exchange_type='topic', durable=True)

    channel.basic_publish(exchange='account',
                        routing_key=routing,
                        body=data,
                        properties=pika.BasicProperties(delivery_mode = 2,)
                        )
    connection.close()
