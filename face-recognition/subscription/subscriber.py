#! /usr/bin/env python
import threading
from _thread import interrupt_main

from subscription.listeners.RabbitMQ import RabbitMQ
#from listeners.RabbitMQ import RabbitMQ


def start_listener(configuration: dict, callback=None):
    print('Initializing message queue listener')
    if not callback:
        print('Using default callback')
        callback = default_callback

    listener = detect_listener(configuration)

    threading.Thread(
        name='Message Broker Listener',
        target=listener.listen,
        args=[callback]
    ).start()


def detect_listener(configuration):
    # TODO: Implement configurable listeners and callbacks

    listener_type = configuration.get('type', 'rabbitmq')
    host = configuration.get('host', 'localhost')

    if not listener_type:
        # Default Listener is RabbitMQ
        print('Using default listener')
        clazz = RabbitMQ
    elif listener_type.lower() == 'rabbitmq':
        print('RabbitMQ detected as listener type')
        clazz = RabbitMQ
    else:
        print('{} is not a supported Listener type'.format(type))
        clazz = None
        interrupt_main()
        exit(1)

    return clazz(host)


def default_callback(ch, method, properties, body):
    print('Received channel: {}'.format(ch))
    print('Received method: {}'.format(method))
    print('Received properties: {}'.format(properties))
    print('Received message: {}'.format(body))
