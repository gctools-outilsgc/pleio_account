from django.apps import AppConfig
import pika
from constance import config


class CoreConfig(AppConfig):
    name = 'core'

    def ready(self):
        # Makes sure all signal handlers are connected
        from core import handler


        if config.SERVICE_MESH_ACTIVATION:
            credentials = pika.PlainCredentials(config.SERVICE_MESH_USER, config.SERVICE_MESH_PASSWORD)
            connection = pika.BlockingConnection(pika.ConnectionParameters(host=config.SERVICE_MESH_HOST, credentials=credentials))
            channel = connection.channel()
            channel.exchange_declare(exchange='account', exchange_type='topic', durable=True)

            connection.close()
