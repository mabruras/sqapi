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


if __name__ == '__main__':
    rnd_uuid = str(uuid.uuid4())
    msg = json.dumps({
        'data_type': 'image/jpeg',
        'data_path': '/test/test_picture01.jpg',
        'meta_path': rnd_uuid,
        'uuid': rnd_uuid,
        'metadata': '{}',
    })

    send_zmq_msg(msg)
