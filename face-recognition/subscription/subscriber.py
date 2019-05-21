#! /usr/bin/env python
import threading
from _thread import interrupt_main

from subscription.listeners.RabbitMQ import RabbitMQ
#from listeners.RabbitMQ import RabbitMQ


def start_listener(configuration: dict, transformer, callback):
    print('Initializing message queue listener')

    listener = detect_listener(configuration)

    threading.Thread(
        name='Message Broker Listener',
        target=listener.listen,
        args=[transformer, callback]
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
