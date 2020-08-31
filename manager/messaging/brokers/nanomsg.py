#! /usr/bin/env python
import logging
import time

import nanomsg as nano

from messaging.brokers import BrokerConfig

log = logging.getLogger(__name__)


class NanomsgConfig(BrokerConfig):
    def __init__(self):
        super().__init__(5001, 'localhost')

        self.retry_interval = 0
        self.process_delay = 0
        self.connection_type = 'bind'
        self.socket_type = 7
        self.protocol = 'tcp'


class NanomsgBroker:

    def __init__(self, config: dict, process_message):
        self.config = config if config else dict()
        self.pm_callback = process_message
        log.info('Loading Nanomsg')

        self.context = nano.Context()

        self.retry_interval = float(config.get('retry_interval', 3))
        self.delay = config.get('process_delay', 0)

        self.host = config.get('host', '127.0.0.1')
        self.port = config.get('port', 5001)

        self.connection_type = config.get('connection_type', 'connect')
        self.socket_type = config.get('socket_type', nano.PULL)
        self.protocol = config.get('protocol', 'tcp')

    def start_listener(self):
        connect_addr = f'{self.protocol}://{self.host}:{self.port}'
        print(f'Connecting to {self.socket_type}-socket on {connect_addr}')

        socket = self.context.socket(self.socket_type)
        if self.connection_type.lower() == 'connect':
            socket.connect(connect_addr)

        elif self.connection_type.lower() == 'bind':
            socket.bind(connect_addr)

        else:
            raise AttributeError(f'Connection type "{self.connection_type}" is not a supported type')

        self._listen_for_messages(socket)

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

            self.pm_callback(body)

        except Exception as e:
            err = 'Could not process received message: {}'.format(str(e))
            log.warning(err)
