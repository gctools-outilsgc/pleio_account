import pika
import sys
import json


credentials = pika.PlainCredentials('gcaccount', 'pleio')
connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost', credentials=credentials))
channel = connection.channel()

channel.exchange_declare(exchange='account', exchange_type='topic', durable=True)

message = {
    "gcID":"61396asdfsded",
    "name": "Bryan Robitaille",
    "email": "bryan.robitaille@tbs-sct.gc.ca"
}

message = json.dumps(message)

routing = sys.argv[1:]
if not routing:
    sys.stderr.write("Usage: %s [routing_key]...\n" % sys.argv[0])
    sys.exit(1)

channel.basic_publish(exchange='account',
                      routing_key= routing[0],
                      body=message,
                      properties=pika.BasicProperties(delivery_mode = 2,)
                      )
print(" [x] Sent %r to RabbitMQ" % message)
connection.close()
