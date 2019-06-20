#! /usr/bin/env python
import json
import logging
import time

import pika
from pika.exceptions import StreamLostError

MIME_TYPES = ['image/jpeg', 'image/png', 'image/gif']
MSG_FIELDS = ['data_type', 'data_location', 'meta_location', 'uuid_ref']

log = logging.getLogger(__name__)


class Listener:

    def __init__(self, config: dict, process_message):
        config = config if config else dict()
        self.processor = process_message
        log.info('Loading RabbitMQ')

        self.retry_interval = float(config.get('retry_interval', 3))
        self.delay = config.get('process_delay', 0)

        self.routing_key = config.get('routing_key', 'q_sqapi')
        self.exchange_name = config.get('exchange_name', 'x_sqapi')
        self.exchange_type = config.get('exchange_type', 'fanout')

        self.host = config.get('host', 'localhost')
        self.port = config.get('port', 5672)

        self.msg_fields = config.get('message_fields', MSG_FIELDS)
        self.mime_types = config.get('supported_mime', MIME_TYPES)

        self.test_connection()

    def test_connection(self):
        log.debug('Testing connection to RabbitMQ on {}:{}'.format(self.host, self.port))
        while True:
            try:
                log.debug('Establishing connection through Pika module')
                connection = pika.BlockingConnection(pika.ConnectionParameters(self.host))

                if connection.is_open:
                    log.info('Connection tested: OK')
                    connection.close()
                    break
                else:
                    err = 'Could not connect to RabbitMQ'
                    log.debug(err)
                    raise ConnectionError('Could not connect to RabbitMQ')
            except Exception as e:
                log.debug('Connection tested: {}'.format(str(e)))
                time.sleep(self.retry_interval)

    def listen_queue(self, routing_key=None):
        self.routing_key = routing_key if routing_key else self.routing_key
        log.info('Starting Queue listener with routing key: {}'.format(self.routing_key))

        connection = pika.BlockingConnection(pika.ConnectionParameters(self.host))
        channel = connection.channel()

        # Create a queue
        channel.queue_declare(queue=self.routing_key)
        channel.basic_consume(queue=self.routing_key, auto_ack=True, on_message_callback=self.parse_message)

        while True:
            try:
                log.info('Starting to consume from queue: {}'.format(self.routing_key))
                channel.start_consuming()
            except StreamLostError as e:
                log.warning('Lost connection to broker: {}'.format(str(e)))
                time.sleep(1)
            except (InterruptedError, KeyboardInterrupt) as e:
                log.error('Interrupted, exiting consumer: {}'.format(str(e)))
                break
        log.info('Finished consuming from queue: {}'.format(self.routing_key))

    def listen_exchange(self):
        log.info('Starting Exchange listener {} as type {}'.format(self.exchange_name, self.exchange_type))
        connection = pika.BlockingConnection(pika.ConnectionParameters(self.host))
        channel = connection.channel()

        channel.exchange_declare(exchange=self.exchange_name, exchange_type=self.exchange_type)

        # Create a queue
        res = channel.queue_declare('', exclusive=True)
        queue_name = res.method.queue
        channel.queue_bind(exchange=self.exchange_name, queue=queue_name)
        channel.basic_consume(queue=queue_name, auto_ack=True, on_message_callback=self.parse_message)

        while True:
            try:
                log.info('Starting to consume from exchange: {}'.format(self.exchange_name))
                channel.start_consuming()
            except StreamLostError as e:
                log.warning('Lost connection to broker: {}'.format(str(e)))
                time.sleep(1)
            except (InterruptedError, KeyboardInterrupt) as e:
                log.error('Interrupted, exiting consumer: {}'.format(str(e)))
                break
        log.info('Finished consuming from exchange: {}'.format(self.exchange_name))

    def parse_message(self, ch, method, properties, body):
        log.info('Received message. Processing starts after delay ({} seconds)'.format(self.delay))
        time.sleep(self.delay)

        try:
            log.debug('Received channel: {}'.format(ch))
            log.debug('Received method: {}'.format(method))
            log.debug('Received properties: {}'.format(properties))
            log.debug('Received message: {}'.format(body))

            body = self.validate_message(body)

            self.processor(body)
        except Exception as e:
            err = 'Could not process received message: {}'.format(str(e))
            log.warning(err)

    def validate_message(self, body):
        log.debug('Validating message')
        # Format
        message = json.loads(body)

        # Validate fields
        self.validate_fields(message)

        log.debug('Validating message mime type')
        msg_type = message.get('data_type', 'UNKNOWN')
        if self.mime_types and msg_type not in self.mime_types:
            err = 'Mime type {} is not supported by this sqAPI'.format(msg_type)
            log.debug(err)
            raise NotImplementedError(err)

        log.debug('Message validated successfully')
        return message

    def validate_fields(self, message):
        log.debug('Validating required fields')
        log.debug('Required fields: {}'.format(self.msg_fields))
        missing_fields = []

        for f in self.msg_fields:
            if f not in dict(message.items()):
                log.debug('Field {} is missing'.format(f))
                missing_fields.append(f)

        if missing_fields:
            err = 'The field(/s) {} are missing in the message'.format('", "'.join(missing_fields))
            log.debug(err)
            raise AttributeError(err)
