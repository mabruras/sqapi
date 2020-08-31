#! /usr/bin/env python3
import logging

from kafka import KafkaConsumer, KafkaProducer

from messaging.brokers import BrokerConfig, Broker

log = logging.getLogger(__name__)


class KafkaConfig(BrokerConfig):
    def __init__(self):
        log.debug('Loading Kafka configuration')
        config = dict()  # Load configuration from file

        host = config.get('host', 'localhost')
        port = config.get('port', 9092)

        super().__init__(port, host)
        # port: 29092 is used for docker network internals,
        # use port 9092 for host machine connections

        self.retry_interval = float(config.get('retry_interval', 3))

        # Receiver
        # Note = Define either subscription_pattern OR topic_names - Not both!
        # subscription_pattern = '^.*$'
        self.subscription_pattern = config.get('subscription_pattern', None)
        #self.subscription_pattern = config.get('subscription_pattern', '^.*$')
        self.topic_names = config.get('topic_names', ['sqapi'])
        self.consumer_group = config.get('consumer_group', 'sqapi')
        self.api_version = tuple(config.get('api_version', [0, 10, 0]))

        # Sender
        self.client_id = config.get('client_id', 'sqapi')
        self.topic = config.get('topic', 'sqapi')


class KafkaBroker(Broker):

    def __init__(self):
        log.info('Initializing Kafka')
        self.config = KafkaConfig()
        self._process_message = super()._process_message

        self._producer = KafkaProducer(
            client_id=self.config.client_id,
            api_version=self.config.api_version,
            bootstrap_servers=f'{self.config.host}:{self.config.port}'
        )
        self._consumer = KafkaConsumer(
            group_id=self.config.consumer_group,
            api_version=self.config.api_version,
            bootstrap_servers=f'{self.config.host}:{self.config.port}'
        )

    def send(self, message: bytes, **kwargs):
        topic = kwargs.get('topic', self.config.topic)
        self._producer.send(topic=topic, value=message, **kwargs)

    def receive(self, callback=print, **kwargs):
        log.info(f'Listening for messages from Kafka')
        self._process_message = callback if callback else self._process_message

        log.info(f'Subscription topics: {self.config.topic_names}')
        log.info(f'Subscription pattern: {self.config.subscription_pattern}')
        self._consumer.subscribe(topics=self.config.topic_names, pattern=self.config.subscription_pattern)

        self._consumer.poll()
        for msg in self._consumer:
            self.parse_message(msg)

    def parse_message(self, body):
        try:
            log.debug('Message body: {}'.format(body))

            self._process_message(body.value)

        except Exception as e:
            err = 'Could not process received message: {}'.format(str(e))
            log.warning(err)
