#! /usr/bin/env python
import logging
import time

import pika

from messaging.brokers import BrokerConfig, Broker

log = logging.getLogger(__name__)


class RabbitMQConfig(BrokerConfig):

    def __init__(self):
        log.debug('Loading RabbitMQ configuration')
        config = dict()  # Load configuration from file

        host = config.get('host', 'localhost')
        port = config.get('port', 5672)

        super().__init__(port, host)

        self.retry_interval = float(config.get('retry_interval', 3))

        self.routing_key = config.get('routing_key', 'q_sqapi')
        self.exchange_name = config.get('exchange_name', 'x_sqapi')
        self.exchange_type = config.get('exchange_type', 'fanout')
        self.requeue_failures = config.get('requeue', True)


class RabbitMQBroker(Broker):

    def __init__(self):
        log.info('Initializing RabbitMQ')
        self.config = RabbitMQConfig()
        self._process_message = super()._process_message

        log.info(f'Creating and testing connection to RabbitMQ on {self.config.host}:{self.config.port}')
        while not self._test_connection():
            time.sleep(self.config.retry_interval)

        self.channel = self._create_rabbit_channel()

    def _test_connection(self):
        try:
            connection = self._init_rabbit_connection()
            if connection.is_open:
                connection.close()
                return True

        except Exception as e:
            log.debug(f'Connection test failed: {str(e)}')
            return False

    def _init_rabbit_connection(self):
        log.debug('Establishing connection through Pika module')
        return pika.BlockingConnection(pika.ConnectionParameters(self.config.host, self.config.port))

    def _create_rabbit_channel(self):
        connection = self._init_rabbit_connection()
        channel = connection.channel()

        exchange = self.config.exchange_name

        if exchange:
            exchange_type = self.config.exchange_type
            self._exchange_setup(channel, exchange, exchange_type, self.config.routing_key)
        else:
            self._queue_setup(channel, self.config.routing_key)

        return channel

    def send(self, message: bytes, **kwargs):
        self._verify_channel()

        self.channel.basic_publish(
            exchange=kwargs.get('exchange', self.config.exchange_name or str()),
            routing_key=kwargs.get('routing_key', self.config.routing_key or str()),
            body=message
        )

    def receive(self, callback=print, **kwargs):
        self._verify_channel()

        self._process_message = callback if callback else self._process_message
        self.channel.start_consuming()

    def _verify_channel(self):
        if self.channel.is_closed:
            print(f'Recreating channel')
            self.channel = self._create_rabbit_channel()

    def _exchange_setup(self, channel, exchange_name, exchange_type, queue_name=str()):
        log.debug(f'Setting up exchange listener {self.config.exchange_name} as type {self.config.exchange_type}')

        channel.exchange_declare(exchange=exchange_name, exchange_type=exchange_type)

        res = channel.queue_declare(queue_name)
        queue = res.method.queue

        channel.queue_bind(exchange=self.config.exchange_name, queue=queue)
        channel.basic_consume(queue=queue, on_message_callback=self._parse_message)

    def _queue_setup(self, channel, queue_name=str()):
        log.debug(f'Setting up queue listener with queue: {queue_name}')

        res = channel.queue_declare(queue=queue_name)
        queue = res.method.queue
        channel.basic_consume(queue=queue, on_message_callback=self._parse_message)

    def _parse_message(self, ch, method, properties, body):
        try:
            log.debug('Received channel: {}'.format(ch))
            log.debug('Received method: {}'.format(method))
            log.debug('Received properties: {}'.format(properties))
            log.debug('Received message: {}'.format(body))

            self._process_message(body)

            ch.basic_ack(delivery_tag=method.delivery_tag)
            log.debug('Message acknowledged sent')

        except Exception as e:
            err = 'Could not process received message: {}'.format(str(e))
            log.warning(err)
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=self.config.requeue_failures)
            log.debug('Message not-acknowledged sent')
