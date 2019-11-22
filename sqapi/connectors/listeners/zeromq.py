#! /usr/bin/env python
import json
import logging
import threading
import time

import zmq as zmq

from sqapi.core.message import Message

MSG_FIELDS = {
    'data_type': {'key': 'data_type', 'required': True},
    'data_location': {'key': 'data_location', 'required': True},
    'meta_location': {'key': 'meta_location', 'required': True},
    'uuid_ref': {'key': 'uuid_ref', 'required': True},
    'metadata': {'key': 'metadata', 'required': False},
}

log = logging.getLogger(__name__)


class Listener:

    def __init__(self, config: dict, process_message):
        self.config = config if config else dict()
        self.pm_callback = process_message
        log.info('Loading ZeroMQ')

        self.context = zmq.Context()

        self.retry_interval = float(config.get('retry_interval', 3))
        self.delay = config.get('process_delay', 0)

        self.host = config.get('host', '127.0.0.1')
        self.port = config.get('port', 5001)

        self.connection_type = config.get('connection_type', 'connect')
        self.socket_type = config.get('socket_type', zmq.PULL)
        self.protocol = config.get('protocol', 'tcp')

        self.msg_fields = config.get('message_fields') or MSG_FIELDS

    def start_listeners(self):
        connect_addr = f'{self.protocol}://{self.host}:{self.port}'
        print(f'Connecting to {self.socket_type}-socket on {connect_addr}')

        socket = self.context.socket(self.socket_type)
        if self.connection_type.lower() == 'connect':
            socket.connect(connect_addr)
        elif self.connection_type.lower() == 'bind':
            socket.bind(connect_addr)
        else:
            raise AttributeError(f'Connection type "{self.connection_type}" is not a supported type')

        threading.Thread(
            name='ZeroMQ Listener',
            target=self._listen_for_messages,
            args=[socket]
        ).start()

    def _listen_for_messages(self, socket):
        while True:
            log.info(f'Listening for messages on socket')
            body = socket.recv()
            log.info(f'Received message on socket')
            self.parse_message(body)

    def parse_message(self, body):
        log.info('Received message. Processing starts after delay ({} seconds)'.format(self.delay))
        time.sleep(self.delay)

        try:
            log.debug('Received message: {}'.format(body))

            body = self.validate_message(body)

            self.pm_callback(Message(body, self.config))
        except Exception as e:
            err = 'Could not process received message: {}'.format(str(e))
            log.warning(err)

    def validate_message(self, body):
        log.debug('Validating message')
        message = json.loads(body)
        self.validate_fields(message)
        log.debug('Message validated successfully')

        return message

    def validate_fields(self, message):
        log.debug('Validating required fields of set: {}'.format(self.msg_fields))
        required_fields = {
            self.msg_fields.get(f).get('key') for f in self.msg_fields
            if self.msg_fields.get(f).get('required')
        }
        log.debug('Required fields: {}'.format(required_fields))
        missing_fields = []

        for f in required_fields:
            if f not in dict(message.items()):
                log.debug('Field {} is missing'.format(f))
                missing_fields.append(f)

        if missing_fields:
            err = 'The field(/s) "{}" are missing in the message'.format('", "'.join(missing_fields))
            log.debug(err)
            raise AttributeError(err)
