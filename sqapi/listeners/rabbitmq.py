#! /usr/bin/env python
import time

import pika


class RabbitMQ:

    def __init__(self, config: dict = None):
        config = config if config else dict()
        print('Loading RabbitMQ with config: {}'.format(config))

        self.retry_interval = float(config.get('retry_interval', 3))

        self.routing_key = config.get('routing_key', 'q_sqapi')
        self.exchange_name = config.get('exchange_name', 'x_sqapi')
        self.exchange_type = config.get('exchange_type', 'fanout')

        self.host = config.get('host', 'localhost')
        self.port = config.get('port', 5672)

        self.test_connection()

    def test_connection(self):
        while True:
            try:
                print('Testing connection to RabbitMQ on {}:{}'.format(self.host, self.port))
                connection = pika.BlockingConnection(pika.ConnectionParameters(self.host))

                if connection.is_open:
                    print('Connection tested: OK')
                    connection.close()
                    break
                else:
                    raise ConnectionError('Could not connect to RabbitMQ')
            except Exception as error:
                print('Connection tested: {}'.format(str(error)))
                time.sleep(self.retry_interval)

    def listen_queue(self, callback, routing_key=None):
        self.routing_key = routing_key if routing_key else self.routing_key
        print('Starting Queue listener with routing key: {}'.format(self.routing_key))

        connection = pika.BlockingConnection(pika.ConnectionParameters(self.host))
        channel = connection.channel()

        # Create a queue
        channel.queue_declare(queue=self.routing_key)
        channel.basic_consume(queue=self.routing_key, auto_ack=True, on_message_callback=callback)

        print('Starting to consume from queue: {}'.format(self.routing_key))
        channel.start_consuming()
        print('Finished consuming from queue: {}'.format(self.routing_key))

    def listen_exchange(self, callback):
        print('Starting Exchange listener "{}" as type "{}"'.format(self.exchange_name, self.exchange_type))
        connection = pika.BlockingConnection(pika.ConnectionParameters(self.host))
        channel = connection.channel()

        channel.exchange_declare(exchange=self.exchange_name, exchange_type=self.exchange_type)

        # Create a queue
        res = channel.queue_declare('', exclusive=True)
        queue_name = res.method.queue
        channel.queue_bind(exchange=self.exchange_name, queue=queue_name)
        channel.basic_consume(queue=queue_name, auto_ack=True, on_message_callback=callback)

        print('Starting to consume from exchange: {}'.format(self.exchange_name))
        channel.start_consuming()
        print('Finished consuming from exchange: {}'.format(self.exchange_name))
