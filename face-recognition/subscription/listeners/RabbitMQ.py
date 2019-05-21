#! /usr/bin/env python
from _thread import interrupt_main

import pika


class RabbitMQ:

    def __init__(self, host: str, routing_key: str = 'content'):
        self.host = host
        self.routing_key = routing_key
        self.test_connection()

    def test_connection(self):

        try:
            connection = pika.BlockingConnection(pika.ConnectionParameters(self.host))
            if connection.is_open:
                print('Connection tested: OK')
                connection.close()
            else:
                raise ConnectionError('Could not connect to RabbitMQ')
        except Exception as error:
            print('Connection tested: {}'.format(error))
            interrupt_main()

    def listen(self, transformer, callback):
        connection = pika.BlockingConnection(pika.ConnectionParameters(self.host))
        channel = connection.channel()

        # Create a queue
        channel.queue_declare(queue=self.routing_key)
        channel.basic_consume(queue=self.routing_key, auto_ack=True, on_message_callback=callback)

        channel.start_consuming()
