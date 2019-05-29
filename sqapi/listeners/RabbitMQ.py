#! /usr/bin/env python
from _thread import interrupt_main

import pika

EXCHANGE_TYPE = 'fanout'
EXCHANGE = 'x_sqapi'
ROUTING_KEY = 'q_sqapi'


class RabbitMQ:

    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        self.test_connection()

    def test_connection(self):

        try:
            print('Testing connection to RabbitMQ on {}:{}'.format(self.host, self.port))
            connection = pika.BlockingConnection(pika.ConnectionParameters(self.host))
            if connection.is_open:
                print('Connection tested: OK')
                connection.close()
            else:
                raise ConnectionError('Could not connect to RabbitMQ')
        except Exception as error:
            print('Connection tested: {}'.format(error))
            interrupt_main()

    def listen_queue(self, callback, routing_key=ROUTING_KEY):
        connection = pika.BlockingConnection(pika.ConnectionParameters(self.host))
        channel = connection.channel()

        # Create a queue
        channel.queue_declare(queue=routing_key)
        channel.basic_consume(queue=routing_key, auto_ack=True, on_message_callback=callback)

        channel.start_consuming()

    def listen_exchange(self, callback):
        connection = pika.BlockingConnection(pika.ConnectionParameters(self.host))
        channel = connection.channel()

        channel.exchange_declare(exchange=EXCHANGE, exchange_type=EXCHANGE_TYPE)

        # Create a queue
        res = channel.queue_declare('', exclusive=True)
        queue_name = res.method.queue
        channel.queue_bind(exchange=EXCHANGE, queue=queue_name)
        channel.basic_consume(queue=queue_name, auto_ack=True, on_message_callback=callback)

        channel.start_consuming()
