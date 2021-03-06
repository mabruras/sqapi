#! /usr/bin/env python
import logging
import time

import pika
from pika.exceptions import StreamLostError

log = logging.getLogger(__name__)


class Listener:

    def __init__(self, config: dict, process_message):
        self.config = config if config else dict()
        self.pm_callback = process_message
        log.info('Loading RabbitMQ')

        self.retry_interval = float(config.get('retry_interval', 3))
        self.delay = config.get('process_delay', 0)

        self.routing_key = config.get('routing_key', 'q_sqapi')
        self.exchange_name = config.get('exchange_name', 'x_sqapi')
        self.exchange_type = config.get('exchange_type', 'fanout')
        self.requeue_failures = config.get('requeue', True)

        self.host = config.get('host', 'localhost')
        self.port = config.get('port', 5672)

        self.test_connection()

    def test_connection(self):
        log.debug('Testing connection to RabbitMQ on {}:{}'.format(self.host, self.port))
        while True:
            try:
                log.debug('Establishing connection through Pika module')
                connection = pika.BlockingConnection(pika.ConnectionParameters(self.host, self.port))

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

    def start_listener(self):
        while True:
            try:
                listener = self.listen_exchange if self.config.get('exchange_name') else self.listen_queue
                listener()

            except StreamLostError as e:
                log.warning('Lost connection to broker: {}'.format(str(e)))
                time.sleep(1)

            except (InterruptedError, KeyboardInterrupt) as e:
                log.error('Interrupted, exiting consumer: {}'.format(str(e)))
                break

            except Exception as e:
                log.error('Something unexpected happened while listening on broker: {}'.format(str(e)))

        log.info('Finished consuming from RabbitMQ')

    def listen_queue(self):
        log.debug('Starting Queue listener with routing key: {}'.format(self.routing_key))

        connection = pika.BlockingConnection(pika.ConnectionParameters(self.host, self.port))
        channel = connection.channel()

        # Create a queue
        channel.queue_declare(queue=self.routing_key)
        channel.basic_consume(queue=self.routing_key, auto_ack=True, on_message_callback=self.parse_message)

        log.debug('Starting to consume from queue: {}'.format(self.routing_key))
        channel.start_consuming()

    def listen_exchange(self):
        log.debug('Starting Exchange listener {} as type {}'.format(self.exchange_name, self.exchange_type))
        connection = pika.BlockingConnection(pika.ConnectionParameters(self.host, self.port))
        channel = connection.channel()

        channel.exchange_declare(exchange=self.exchange_name, exchange_type=self.exchange_type)

        # Create a queue
        res = channel.queue_declare(self.routing_key)
        queue_name = res.method.queue
        channel.queue_bind(exchange=self.exchange_name, queue=queue_name)
        channel.basic_consume(queue=queue_name, on_message_callback=self.parse_message)

        log.debug('Starting to consume from exchange: {}'.format(self.exchange_name))
        channel.start_consuming()

    def parse_message(self, ch, method, properties, body):
        log.info('Received message. Processing starts after delay ({} seconds)'.format(self.delay))
        time.sleep(self.delay)

        try:
            log.debug('Received channel: {}'.format(ch))
            log.debug('Received method: {}'.format(method))
            log.debug('Received properties: {}'.format(properties))
            log.debug('Received message: {}'.format(body))

            self.pm_callback(body)
            ch.basic_ack(delivery_tag=method.delivery_tag)
            log.info('Message acknowledged sent')

        except Exception as e:
            err = 'Could not process received message: {}'.format(str(e))
            log.warning(err)
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=self.requeue_failures)
            log.info('Message not-acknowledged sent')
