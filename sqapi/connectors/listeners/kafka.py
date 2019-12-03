#! /usr/bin/env python
import json
import logging
import threading
import time

import kafka as kafka
import zmq as zmq

from sqapi.core.message import Message
from sqapi.util import message_util

log = logging.getLogger(__name__)


class Listener:

    def __init__(self, config: dict, process_message):
        self.config = config if config else dict()
        self.pm_callback = process_message
        log.info('Loading Kafka')

        self.context = zmq.Context()

        self.retry_interval = float(config.get('retry_interval', 3))
        self.delay = config.get('process_delay', 0)

        self.host = config.get('host', 'localhost')
        self.port = config.get('port', 9092)

        self.consume_type = config.get('consume_type', 'topic')
        self.topic_name = config.get('topic_name', 'sqapi')
        self.sub_pattern = config.get('subscription_pattern', '^.*$')
        self.consumer_group = config.get('consumer_group', 'sqapi')
        self.api_version = tuple(config.get('api_version', [0, 10, 0]))

        self.msg_fields = config.get('message_fields') or message_util.MSG_FIELDS

    def start_listeners(self):
        threading.Thread(
            name='Kafka Listener',
            target=self._listen_for_messages
        ).start()

    def _listen_for_messages(self):
        while True:
            log.info(f'Listening for messages from Kafka')

            if self.consume_type.lower() == 'topic':
                consumer = kafka.KafkaConsumer(self.topic_name, self.consumer_group, api_version=self.api_version)
            elif self.consume_type.lower() == 'subscribe':
                consumer = kafka.KafkaConsumer(api_version=self.api_version)
                consumer.subscribe(self.sub_pattern)
            else:
                raise AttributeError(f'Consume type "{self.consume_type}" is not a supported type')

            consumer.poll()
            for msg in consumer:
                log.info(f'Received message')
                self.parse_message(msg)

    def parse_message(self, body):
        log.info('Received message. Processing starts after delay ({} seconds)'.format(self.delay))
        time.sleep(self.delay)

        try:
            log.debug('Received message: {}'.format(body))

            message = json.loads(body.value.decode('utf-8'))
            body = message_util.validate_message(message, self.msg_fields)

            self.pm_callback(Message(body, self.config))

        except Exception as e:
            err = 'Could not process received message: {}'.format(str(e))
            log.warning(err)
