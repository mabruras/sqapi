#! /usr/bin/env python3

import pika


def callback(ch, method, properties, body):
    print(" [x] Received %r" % body)


connection = pika.BlockingConnection(pika.ConnectionParameters('localhost', 5672))
channel = connection.channel()
print('Established connection')

# Create an exchange
channel.exchange_declare(exchange='content', exchange_type='fanout')

# Create a queue
res = channel.queue_declare('', exclusive=True)
queue_name = res.method.queue
print('Queue created: {}'.format(queue_name))

channel.queue_bind(exchange='content', queue=queue_name)
channel.basic_consume(queue=queue_name,
                      auto_ack=True,
                      on_message_callback=callback)

channel.start_consuming()
