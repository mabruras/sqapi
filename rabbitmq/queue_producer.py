#! /usr/bin/env python3

import json
import uuid

import pika

connection = pika.BlockingConnection(pika.ConnectionParameters('localhost', 5672))
channel = connection.channel()
print('Established connection')

# Create a queue
channel.queue_declare(queue='content')
print('Queue created')

channel.basic_publish(exchange='',
                      routing_key='content',
                      body=json.dumps({
                          'type': 'face/encoding',
                          's3': 'mybucket/28c98ee8b211be21d4a9f4ef1687c4d36f',
                          'redis': 'redis-ref',
                          'uuid': str(uuid.uuid4()),
                      })
                      )
print('Published message')

connection.close()
print('Connection closed')
