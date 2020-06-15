import pika
from constance import config

def service_mesh_message(routing,data):

    try:
        if config.SERVICE_MESH_ACTIVATION:
            credentials = pika.PlainCredentials(config.SERVICE_MESH_USER, config.SERVICE_MESH_PASSWORD)
            connection = pika.BlockingConnection(pika.ConnectionParameters(host=config.SERVICE_MESH_HOST, credentials=credentials))
            channel = connection.channel()
            channel.exchange_declare(exchange='account', exchange_type='topic', durable=True)

            channel.basic_publish(exchange='account',
                                routing_key=routing,
                                body=data,
                                properties=pika.BasicProperties(delivery_mode = 2,)
                                )
            connection.close()
    except Exception as e:
        print('Service Mesh Error: ' + str(e))
