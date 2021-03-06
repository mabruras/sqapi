#! /usr/bin/env python
import logging
import time

from kafka import KafkaConsumer

log = logging.getLogger(__name__)


class Listener:

    def __init__(self, config: dict, process_message):
        self.config = config if config else dict()
        self.pm_callback = process_message
        log.info('Loading Kafka')

        self.retry_interval = float(config.get('retry_interval', 3))
        self.delay = config.get('process_delay', 0)

        self.host = config.get('host', 'localhost')
        self.port = config.get('port', 9092)

        self.topic_names = config.get('topic_names', [])
        self.sub_pattern = config.get('subscription_pattern', None)
        self.consumer_group = config.get('consumer_group', 'sqapi')
        self.api_version = tuple(config.get('api_version', [0, 10, 0]))

    def start_listener(self):
        while True:
            log.info(f'Listening for messages from Kafka')
            consumer = KafkaConsumer(
                group_id=self.consumer_group,
                api_version=self.api_version,
                bootstrap_servers=f'{self.host}:{self.port}'
            )

            log.info(f'Subscription topics: {self.topic_names}')
            log.info(f'Subscription pattern: {self.sub_pattern}')
            consumer.subscribe(topics=self.topic_names, pattern=self.sub_pattern)

            consumer.poll()
            for msg in consumer:
                log.info('Received message: {} (topic), {} (partition), {} (offset), {} (key)'.format(
                    msg.topic, msg.partition, msg.offset, msg.key
                ))
                self.parse_message(msg)

    def parse_message(self, body):
        log.info('Processing starts after delay ({} seconds)'.format(self.delay))
        time.sleep(self.delay)

        try:
            log.debug('Message body: {}'.format(body))

            self.pm_callback(body.value.decode('utf-8'))

        except Exception as e:
            err = 'Could not process received message: {}'.format(str(e))
            log.warning(err)
