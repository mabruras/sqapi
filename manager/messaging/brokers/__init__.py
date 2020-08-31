#! /usr/bin/env python3
import abc
import logging

import time

log = logging.getLogger(__name__)


class BrokerConfig:

    # @staticmethod
    # def get_instance(kind: str):
    #     if kind.lower() in ['rabbitmq', 'rabbit', 'rmq']:
    #         return RabbitMQConfig()
    #     elif kind.lower() in ['kafka']:
    #         return KafkaConfig()
    #     elif kind.lower() in ['zeromq', 'zero', 'zmq']:
    #         return ZeroMQConfig()
    #     elif kind.lower() in ['nanomsg', 'nano']:
    #         return NanomsgConfig()
    #     else:
    #         raise ModuleNotFoundError(f'{kind} is not a valid broker kind')

    def __init__(self, port: int, host: str = 'localhost'):
        self.port = port
        self.host = host


class Broker(metaclass=abc.ABCMeta):
    @classmethod
    def __subclasshook__(cls, subclass):
        return (hasattr(subclass, 'send') and
                callable(subclass.send) and
                hasattr(subclass, 'receive') and
                callable(subclass.receive) and
                hasattr(subclass, 'receive') and
                not callable(subclass.config))

    @abc.abstractmethod
    def send(self, message: bytes, **kwargs):
        """
        Send a message to the broker

        :return: None
        """
        raise NotImplementedError

    @abc.abstractmethod
    def receive(self, callback=print, **kwargs):
        """
        Method for receiving messages from the broker,
        with received data sent to the callback function

        :param callback: function executed with arguments from received message
        :return: None
        """
        # # Tips for wrapping logic of this method
        # try:
        #   pass
        # except Exception as e:
        #   log.error('Something unexpected happened while listening on broker: {}'.format(str(e)))

        raise NotImplementedError

    @staticmethod
    def _process_message(body):
        log.info(f'Received message: {body}')


def send_dummy_messages(sender):
    while True:
        try:
            msg = str(uuid.uuid4()).encode('utf-8')
            print(f'Sending message: {msg}')
            sender.send(msg)
            time.sleep(5)

        except Exception as e:
            log.error('Something unexpected happened while listening on broker: {}'.format(str(e)))


def print_dummy_message(body):
    print(f'Received message: {body}')


if __name__ == '__main__':

    import uuid
    import threading

    from messaging.brokers.rabbitmq import RabbitMQBroker
    broker = RabbitMQBroker()
    # from messaging.brokers.kafka_client import KafkaBroker
    # broker = KafkaBroker()
    # from messaging.brokers.nanomsg import NanomsgBroker
    # broker = NanomsgBroker()
    # from messaging.brokers.zeromq import ZeroMQBroker
    # broker = ZeroMQBroker()

    t = threading.Thread(target=send_dummy_messages, args=[broker, ])
    t.start()

    while True:
        try:
            print('Receiver started')
            broker.receive(print_dummy_message)
            print('Receiver done')

        except Exception as e:
            log.error('Something unexpected happened while listening on broker: {}'.format(str(e)))
