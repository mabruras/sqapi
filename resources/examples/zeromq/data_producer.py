#! /usr/bin/env python3

import json
import uuid

import zmq


def send_zmq_msg(message):
    context = zmq.Context()

    bind_addr = f'tcp://127.0.0.1:5001'
    socket = context.socket(zmq.PUSH)
    socket.connect(bind_addr)

    print(f'Sending message: {message}')
    socket.send(message.encode('utf-8'))
    print(f'Message sent')
    socket.close()


def get_string_data(rnd_uuid):
    return f'{rnd_uuid}|/test/test_picture01.jpg|sqapi|messaging|0'


def get_json_data(rnd_uuid):
    return json.dumps({
        'uuid': rnd_uuid,
        'hash': '/test/test_picture01.jpg',
        'meta_path': rnd_uuid,
        'system': 'sqapi',
        'module': 'test',
        'state': 0,
    })


if __name__ == '__main__':
    rnd_uuid = str(uuid.uuid4())
    #msg = get_json_data(rnd_uuid)
    msg = get_string_data(rnd_uuid)

    send_zmq_msg(msg)
