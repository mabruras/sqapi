#! /usr/bin/env python3

import json
import os
import uuid
from shutil import copyfile

import pika
import redis

EXCHANGE = 'x_sqapi'


def populate_redis(uuid_ref):
    r = redis.Redis(host='localhost', port=6379, db=0)

    r.hmset(uuid_ref,
            {
                'field1': 'value1',
                'field2': 'value2',
                'field3': 'value3',
                'field4': 'value4',
                'field5': 'value5',
                'field6': 'value6',
                'field7': 'value7',
                'field8': 'value8',
                'field9': 'value9'
            })


def populate_data(uuid_ref):
    script_dir = os.path.dirname(__file__)
    print('Script dir: {}'.format(script_dir))

    file_location = '/tmp/my_file_{}'.format(uuid_ref)

    test_file = os.path.join(script_dir, 'resources/test_picture01.jpg')
    print('Test file: {}'.format(test_file))
    copyfile(test_file, file_location)

    return file_location


def populate_rabbit(file_location, uuid_ref):
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost', 5672))
    channel = connection.channel()
    print('Established connection')

    # Create a queue
    declared_queue = channel.exchange_declare(exchange=EXCHANGE, exchange_type='fanout')
    print('Exchange created')

    channel.basic_publish(exchange=EXCHANGE,
                          routing_key='',
                          body=json.dumps({
                              'data_type': 'image/jpeg',
                              'data_location': file_location,
                              'meta_location': 'redis-ref',
                              'uuid_ref': uuid_ref,
                          })
                          )
    print('Published message')

    connection.close()
    print('Connection closed')


rnd_uuid = str(uuid.uuid4())

populate_redis(rnd_uuid)
data_location = populate_data(rnd_uuid)
populate_rabbit(data_location, rnd_uuid)
