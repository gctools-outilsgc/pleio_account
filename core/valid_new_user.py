import pika
import sys
import json

def validate_newuser(data):
    # credentials = pika.PlainCredentials('gcaccount', 'pleio')
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()

    channel.exchange_declare(exchange='new_valid_user', exchange_type='topic', durable=True)

    #Transform data
    def jdefault(data):
        return data.__dict__

    message = json.dumps(data, default=jdefault)

    routing = data
    if not routing:
        sys.stderr.write("Usage: %s [routing_key]...\n" % sys.argv[0])
        sys.exit(1)

    channel.basic_publish(exchange='new_valid_user',
                        routing_key=routing[0],
                        body=message,
                        properties=pika.BasicProperties(delivery_mode = 2,)
                        )
    print(" [x] Sent %r to RabbitMQ" % data)
    connection.close()
