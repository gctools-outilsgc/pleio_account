import pika
import time
import json
import sys

# credentials = pika.PlainCredentials('profile', 'GCdirectory')
connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

channel.exchange_declare(exchange='new_valid_user', exchange_type='topic', durable=True)
channel.queue_declare(queue='valid_user', durable=True)
binding_keys = sys.argv[1:]

if not binding_keys:
    sys.stderr.write("Usage: %s [binding_key]...\n" % sys.argv[0])
    sys.exit(1)

for binding_key in binding_keys:
    channel.queue_bind(exchange='new_valid_user',
                       queue='valid_user',
                       routing_key=binding_key)

print(' [*] Waiting for messages. To exit press CTRL+C')

def callback(ch, method, properties, body):
    jsonResponse = json.loads(body.decode('utf-8'))
    print(" [x] Received %r" % jsonResponse['email'])
    time.sleep(body.count(b'.'))
    print(" [x] Done")
    ch.basic_ack(delivery_tag = method.delivery_tag)

channel.basic_qos(prefetch_count=1)
channel.basic_consume(callback, queue='valid_user')

channel.start_consuming()