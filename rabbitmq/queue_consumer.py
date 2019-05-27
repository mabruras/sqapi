#! /usr/bin/env python3

import pika


def callback(ch, method, properties, body):
    print(" [x] Received %r" % body)


connection = pika.BlockingConnection(pika.ConnectionParameters('localhost', 5672))
channel = connection.channel()
print('Established connection')

# Create a queue
channel.queue_declare(queue='content')
print('Queue created')

channel.basic_consume(queue='content',
                      auto_ack=True,
                      on_message_callback=callback)

channel.start_consuming()
