#! /usr/bin/env python3

import json
import uuid

import pika
import redis

EXCHANGE = 'x_sqapi'


def populate_redis(uuid_ref):
    r = redis.Redis(host='localhost', port=6379, db=0)

    r.set(uuid_ref, {})


def populate_rabbit(message):
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost', 5672))
    channel = connection.channel()
    print('Established connection')

    # Create a queue
    declared_queue = channel.exchange_declare(exchange=EXCHANGE, exchange_type='fanout')
    print('Exchange created')

    channel.basic_publish(exchange=EXCHANGE,
                          routing_key='',
                          body=message)
    print('Published message')

    connection.close()
    print('Connection closed')


if __name__ == '__main__':
    rnd_uuid = str(uuid.uuid4())
    msg = json.dumps({
        'data_type': 'image/jpeg',
        'data_location': '/test/test_picture01.jpg',
        'meta_location': rnd_uuid,
        'uuid_ref': rnd_uuid
    })

    populate_redis(rnd_uuid)
    populate_rabbit(msg)
