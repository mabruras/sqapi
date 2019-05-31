#! /usr/bin/env python
import os
import sys
import threading

from flask import Flask
from flask_cors import CORS

from core.processor import Processor
from listeners.RabbitMQ import RabbitMQ
from util.cfg_util import Config

PROJECT_DIR = os.environ.get('WRK_DIR', '.')
CONFIG_DIR = '{}{}conf'.format(PROJECT_DIR, os.sep)
CONFIG_FILE = os.environ.get('CFG_FILE', '{}{}sqapi.yml'.format(CONFIG_DIR, os.sep))


def start_subscription():
    processor = Processor(config)
    listener = detect_listener()

    # Setup sqAPI general exchange listener
    threading.Thread(
        name='Exchange Listener',
        target=listener.listen_exchange,
        args=[processor.process_message]
    ).start()

    # Setup sqAPI unique queue listener
    routing_key = config.cfg_broker('routing', 'q_sqapi')
    threading.Thread(
        name='Queue Listener',
        target=listener.listen_queue,
        args=[processor.process_message, routing_key]
    ).start()


def detect_listener():
    listener_type = config.cfg_broker('type', 'rabbitmq')
    host = config.cfg_broker('host', 'localhost')
    port = config.cfg_broker('port', 5672)

    # TODO: More generic selection of listener type?
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
        exit(1)

    return clazz(host, port)


def start_api():
    app = Flask(__name__)
    CORS(app)
    app.url_map.strict_slashes = False
    app.config['CORS_HEADERS'] = 'Content-Type,Authorization,X-Requested-With,Content-Length,Accept,Origin'

    register_endpoints(app)

    app.run(host='0.0.0.0')


def register_endpoints(app):
    from api import edge

    app.register_blueprint(edge.bp)


if __name__ == '__main__':
    config = Config(CONFIG_FILE)

    if len(sys.argv) > 1 and sys.argv[1] == 'loader':
        start_subscription()
    elif len(sys.argv) > 1 and sys.argv[1] == 'api':
        start_api()
    else:
        start_subscription()
        start_api()
