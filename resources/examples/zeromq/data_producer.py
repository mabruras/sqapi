#! /usr/bin/env python3
import datetime
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
    # return f'{rnd_uuid}|/test/test_picture01.jpg|sqapi|messaging|0'
    # return f'{rnd_uuid}|/test/test_json01.json|sqapi|messaging|application/json'

    json_meta = json.dumps({
        'wrapper-a': {
            'field-a-1': 'abc',
            'field-a-2': 456,
            'field-a-3': 3.14,
        },
        'wrapper-b': {
            'field-b-1': True,
            'field-b-2': None,
            'field-b-3': '',
        },
        'date-stamps': [
            datetime.datetime.now().isoformat(),
            (datetime.datetime.now() + datetime.timedelta(1)).isoformat(),
        ],
        'wrapped-stamp': {
            'timestamp': datetime.datetime.now().isoformat(),
        },
        'uuid': rnd_uuid,
    })
    return f'{rnd_uuid}|/test/test_json01.json|{json_meta}'


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
    # msg = get_json_data(rnd_uuid)
    msg = get_string_data(rnd_uuid)

    send_zmq_msg(msg)
