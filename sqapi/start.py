#! /usr/bin/env python
import json
import os
import threading

import yaml
from flask import Flask
from flask_cors import CORS

from listeners.RabbitMQ import RabbitMQ

CONFIG = dict()

PROJECT_DIR = os.environ.get('WRK_DIR', '.')
CONFIG_DIR = '{}{}conf'.format(PROJECT_DIR, os.sep)
CONFIG_FILE = os.environ.get('CFG_FILE', '{}{}sqapi.yml'.format(CONFIG_DIR, os.sep))


def load_config():
    print('Loading configuration')
    with open(CONFIG_FILE, 'r') as stream:
        try:
            global CONFIG
            CONFIG = yaml.safe_load(stream) or dict()
            print('Config loaded')
            print(CONFIG)
        except yaml.YAMLError as exc:
            print(exc)


def start_subscription():
    listener = detect_listener()

    threading.Thread(
        name='Message Broker Listener',
        target=listener.listen,
        args=[process_message]
    ).start()


def detect_listener():
    listener_type = CONFIG.get('msg_broker_type', 'rabbitmq')
    host = CONFIG.get('msg_broker_host', 'localhost')
    routing_key = CONFIG.get('msg_broker_routing', 'msg_queue')

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

    return clazz(host, routing_key)


def process_message(ch, method, properties, body):
    print('Received channel: {}'.format(ch))
    print('Received method: {}'.format(method))
    print('Received properties: {}'.format(properties))
    print('Received message: {}'.format(body))

    try:
        # TODO: Formatting should be configurable here
        # Format
        message = json.loads(body)

        # Query
        q_data, q_kv = build_queries(message)
        data, kv = execute_queries(q_data, q_kv)

        # Storage
        store_data(data)
        store_kv(kv)
    except Exception as e:
        print('Could not parse message body to dictionary')
        print(body)
        print(e)


def build_queries(message):
    # TODO: Based on message extract the following:
    # Data location (database, disk, object store etc.) + identifier (lookup reference)
    # Key/Value location (Redis, file etc.) + identifier (lookup reference) + optional field limitation

    return message, message


def execute_queries(data_query, kv_query):
    # TODO: Based on query content, the query should be executed to the intended system:
    # Use _query.location to find defined system, _query.id for lookup and kv_query.fields ([]) for optional limitation

    return data_query, kv_query


def store_data(data):
    # TODO: Connect to a database defined in configuration and store based on configured structure
    pass


def store_kv(kv):
    # TODO: Connect to a database defined in configuration and store based on configured structure
    pass


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
    load_config()
    start_subscription()
    start_api()
