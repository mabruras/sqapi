#! /usr/bin/env python
import time

import datetime
import functools
import logging
import pika
import threading
from contextlib import suppress
from pika.exceptions import StreamLostError, ChannelClosed, AMQPConnectionError, ConnectionWrongStateError
from sqapi.processing.exception import SqapiPluginExecutionError, PluginFailure

log = logging.getLogger(__name__)


class Listener:

    def __init__(self, config: dict, process_message):
        self.config = config if config else dict()
        self.pm_callback = process_message
        log.info('Loading RabbitMQ')

        self.retry_interval = float(config.get('retry_interval', 3))
        self.delay = config.get('process_delay', 0)

        self.routing_keys = config.get('routing_keys', [])
        routing_key = config.get('routing_key')
        if routing_key:
            self.routing_keys.append(routing_key)
        self.queue_name = config.get('queue_name', 'q_sqapi')
        self.exchange_name = config.get('exchange_name', 'x_sqapi')
        self.exchange_type = config.get('exchange_type', 'fanout')
        self.requeue_failures = config.get('requeue', True)

        dlq_config = config.get('dlq', {})
        self.dlq_exchange = dlq_config.get('exchange', 'DLQ')
        self.dlq_exchange_type = dlq_config.get('exchange_type', 'topic')
        self.dlq_routing_key = dlq_config.get('routing_key', 'message.sqapi')

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

            except (StreamLostError, ChannelClosed, AMQPConnectionError) as e:
                log.warning('Lost connection to broker: {}'.format(str(e)))

            except (InterruptedError, KeyboardInterrupt) as e:
                log.error('Interrupted, exiting consumer: {}'.format(str(e)))
                break

            except SystemExit:
                log.error('System is shutting down - exiting RabbitMQ consumer')
                break

            except Exception as e:
                log.error('Something unexpected happened ({}) while listening on broker: {}'.format(type(e), str(e)))

            finally:
                time.sleep(1)

        log.info('Finished consuming from RabbitMQ')

    def listen_queue(self):
        log.info('Starting Queue listener with routing key: {}'.format(self.routing_key))
        connection, channel = self._create_connection()

        # Create a queue
        res = channel.queue_declare(
            queue=self.queue_name,
            arguments={
                'x-max-priority': 3
            })
        queue_name = res.method.queue
        callback = functools.partial(self.message_receiver, connection=connection)
        channel.basic_consume(queue=queue_name, on_message_callback=callback)

        log.debug('Starting to consume from queue: {}'.format(queue_name))
        channel.start_consuming()

    def listen_exchange(self):
        log.debug('Starting Exchange listener {} as type {}'.format(self.exchange_name, self.exchange_type))
        connection, channel = self._create_connection()

        channel.exchange_declare(exchange=self.exchange_name, exchange_type=self.exchange_type, durable=True)

        # Create a queue
        res = channel.queue_declare(
            self.queue_name,
            arguments={
                'x-max-priority': 3
            })
        queue_name = res.method.queue
        for key in self.routing_keys:
            channel.queue_bind(exchange=self.exchange_name, queue=queue_name, routing_key=key)
        callback = functools.partial(self.message_receiver, connection=connection)
        channel.basic_consume(queue=queue_name, on_message_callback=callback)

        log.debug('Starting to consume from exchange: {}'.format(self.exchange_name))
        channel.start_consuming()

    def _create_connection(self):
        connection = pika.BlockingConnection(pika.ConnectionParameters(self.host, self.port))
        channel = connection.channel()

        return channel

    def publish_to_dlq(self, method, properties, body, e: SqapiPluginExecutionError):
        try:
            connection, channel = self._create_connection()
            channel.exchange_declare(exchange=self.dlq_exchange, exchange_type=self.dlq_exchange_type, durable=True)

            for error in e.failures:
                properties.headers = {
                    'x-death': {
                        'x-exception-information': {
                            'x-exception-timestamp': str(datetime.datetime.utcnow().isoformat()),
                            'x-exception-reason': str(error.reason),
                            'x-exception-system': 'Sqapi',
                            'x-exception-type': str(error.exception_type),
                        },
                        'queue': '.'.join([x for x in [self.queue_name, error.plugin] if x]),
                        'exchange': method.exchange,
                        'routing-keys': [method.routing_key],
                    }
                }
                log.debug(f'Headers: {properties.headers}')

                channel.basic_publish(exchange=self.dlq_exchange,
                                      routing_key='.'.join([
                                          self.dlq_routing_key, error.plugin
                                      ]),
                                      properties=properties,
                                      body=body)

        except Exception as e:
            log.error(f'Failed publishing message to DLQ: {str(e)}')

    def message_receiver(self, ch, method, properties, body, connection):
        log.info('Received message')
        log.debug(f'Channel: {ch}, Method: {method}, Properties: {properties}, Message: {body}')

        t = threading.Thread(target=self.handle_message, args=(connection, ch, method, properties, body))
        t.start()

    def handle_message(self, connection, ch, method, properties, body):
        cb = None

        try:
            rk_parts = method.routing_key.split('.')
            specific_plugin = rk_parts[2] if len(rk_parts) is 3 else None

            self.pm_callback(body, specific_plugin)
            cb = functools.partial(self.send_ack, ch=ch, tag=method.delivery_tag)

        except SqapiPluginExecutionError as e:
            log.warning('Registering {len(e.failures)} errors from plugin execution')
            cb = functools.partial(self.send_nack, ch=ch, tag=method.delivery_tag)
            self.publish_to_dlq(method, properties, body, e)

        except Exception as e:
            log.warning(f'Could not process received message: {str(e)}')
            cb = functools.partial(self.send_nack, ch=ch, tag=method.delivery_tag, rq=self.requeue_failures)
            self.publish_to_dlq(method, properties, body, SqapiPluginExecutionError([PluginFailure('', e)]))

        except SystemExit as e:
            log.warning('Could not process received message, due to shutdown')
            with suppress(ConnectionWrongStateError, StreamLostError):
                ch.stop_consuming()
                ch.close()
                connection.close()

            raise e

        finally:
            if cb:
                connection.add_callback_threadsafe(cb)

    def send_ack(self, ch, tag):
        try:
            ch.basic_ack(delivery_tag=tag)
            log.info('Message acknowledged sent')
        except Exception as e:
            err = f'Failed sending ack'
            log.warning(err)
            raise ConnectionError(err, e)

    def send_nack(self, ch, tag, rq=False):
        try:
            ch.basic_nack(delivery_tag=tag, requeue=rq)
            log.info('Message acknowledged sent')
        except Exception as e:
            err = f'Failed sending nack'
            log.warning(err)
            raise ConnectionError(err, e)
