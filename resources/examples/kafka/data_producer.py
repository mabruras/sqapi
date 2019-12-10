#! /usr/bin/env python3

import json
import sys
import uuid

import kafka


def send_kafka_msg(message, topic):
    producer = kafka.KafkaProducer(bootstrap_servers='localhost:9092')
    key = 'sqapi_producer'

    print(f'Sending message:')
    print(f'\t[Tpc]\t{topic}')
    print(f'\t[Msg]\t{message.encode("utf-8")}')
    print(f'\t[Key]\t{key.encode("utf-8")}')

    producer.send(topic, message.encode('utf-8'), key.encode('utf-8'))
    producer.flush()
    print(f'Message sent')


if __name__ == '__main__':
    rnd_uuid = str(uuid.uuid4())
    msg = json.dumps({
        'data_type': 'image/jpeg',
        'data_path': '/test/test_picture01.jpg',
        'meta_path': rnd_uuid,
        'uuid': rnd_uuid,
        'metadata': '{}',
    })

    topic = 'sqapi'
    if len(sys.argv) > 1:
        topic = sys.argv[1]

    send_kafka_msg(msg, topic)
