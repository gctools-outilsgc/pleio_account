import pika
import config as cfg
import json

def send_to_services(data, key):
    credentials = pika.PlainCredentials('gcaccount', 'pleio')
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='mq.gccollab.ca', credentials=credentials))
    channel = connection.channel()

    channel.exchange_declare(exchange='account', exchange_type='topic', durable=True)

    message = json.dumps(data)
    channel.basic_publish(exchange='account',
                        routing_key= routing[0],
                        body=message,
                        properties=pika.BasicProperties(delivery_mode = 2,)
                        ))
    print(" [x] Sent %r to RabbitMQ with key %s" % (message, routing_key))
    connection.close()