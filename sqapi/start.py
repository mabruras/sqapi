#! /usr/bin/env python
import json
import os
import sys
import threading

import redis
import yaml
from flask import Flask
from flask_cors import CORS

from listeners.RabbitMQ import RabbitMQ

CONFIG = dict()

PROJECT_DIR = os.environ.get('WRK_DIR', '.')
CONFIG_DIR = '{}{}conf'.format(PROJECT_DIR, os.sep)
CONFIG_FILE = os.environ.get('CFG_FILE', '{}{}sqapi.yml'.format(CONFIG_DIR, os.sep))
MIME_TYPES = ['image/jpeg', 'image/png', 'image/gif']
MSG_FIELDS = ['data_type', 'data_location', 'meta_location', 'uuid']


def load_config():
    print('Loading configuration: {}'.format(CONFIG_FILE))
    with open(CONFIG_FILE, 'r') as stream:
        try:
            global CONFIG
            CONFIG = yaml.safe_load(stream) or dict()
            print('Config loaded: {}'.format(CONFIG))
        except yaml.YAMLError as exc:
            print(exc)


def start_subscription():
    listener = detect_listener()

    # Setup sqAPI general exchange listener
    threading.Thread(
        name='Exchange Listener',
        target=listener.listen_exchange,
        args=[process_message]
    ).start()

    # Setup sqAPI unique queue listener
    routing_key = cfg_broker('routing', 'q_sqapi')
    threading.Thread(
        name='Queue Listener',
        target=listener.listen_queue,
        args=[process_message, routing_key]
    ).start()


def detect_listener():
    listener_type = cfg_broker('type', 'rabbitmq')
    host = cfg_broker('host', 'localhost')
    port = cfg_broker('port', 5672)

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


def process_message(ch, method, properties, body):
    print('Received channel: {}'.format(ch))
    print('Received method: {}'.format(method))
    print('Received properties: {}'.format(properties))
    print('Received message: {}'.format(body))

    try:
        message = validate_message(body)

        # Query
        data = query_data(message)
        meta = query_metadata(message)

        process_content(meta, data)
    except Exception as e:
        print('Could not process message')
        print(body)
        print(e)


def validate_message(body):
    # TODO: Formatting should be configurable here
    # Format
    message = json.loads(body)

    print('MESSAGE:')
    print(message)
    print('TYPE:')
    print(type(message))

    # Validate fields
    for f in MSG_FIELDS:
        if f not in dict(message.items()):
            raise AttributeError('The field "{}" is missing in the message'.format(f))

    msg_type = message.get('data_type', 'UNKNOWN')
    if msg_type not in MIME_TYPES:
        raise NotImplementedError('Mime-type "{}" is not supported by this sqAPI'.format(msg_type))

    return message


def query_data(message):
    # TODO: Based on message extract the following:
    # Data location (database, disk, object store etc.) + identifier (lookup reference)
    loc = message.get('data_location', None)
    if not loc:
        raise AttributeError('Could not find "data_location" in message')
    data = fetch_data(loc)

    return data


def fetch_data(location):
    disk_loc = fetch_data_to_disk(location)

    return fetch_file_from_disk(disk_loc)


def fetch_data_to_disk(location):
    # TODO: this return should be from a specific/configurable module
    # so it will download/get file data from all kinds of storage places

    # TODO: Now location is returned since we know in this POC that the file is on disk
    return location


def fetch_file_from_disk(file):
    return open(file, "rb")


def query_metadata(message):
    # TODO: Based on query content, the query should be executed to the intended system:
    # Key/Value location (Redis, file etc.) + identifier (lookup reference) + optional field limitation

    meta_store = cfg_meta('type', 'redis')

    # TODO: More generic selection of metadata store?
    if not meta_store:
        # Default Metadata store is Redis
        print('Using default listener')
        clazz = redis.Redis
    elif meta_store.lower() == 'redis':
        print('RabbitMQ detected as metadata type')
        clazz = redis.Redis
    else:
        print('{} is not a supported metadata type'.format(type))
        clazz = None
        exit(1)

    return fetch_meta_from_redis(clazz, message)


def fetch_meta_from_redis(clazz, message):
    host = cfg_meta('host', 'localhost')
    port = cfg_meta('port', 6379)
    r = clazz(host=host, port=port)

    return r.hgetall(message.get('uuid'))


def process_content(meta, data):
    print('Meta processing:')
    print(meta)

    print('Data processing:')
    out = data.read()
    data.close()
    print('File size: {}'.format(len(out)))


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


def cfg_broker(key, default=None):
    return cfg('msg_broker', {}).get(key, default)


def cfg_meta(key, default=None):
    return cfg('meta_store', {}).get(key, default)


def cfg(key, default):
    return CONFIG.get(key, default)


if __name__ == '__main__':
    load_config()

    if len(sys.argv) > 1 and sys.argv[1] == 'loader':
        start_subscription()
    elif len(sys.argv) > 1 and sys.argv[1] == 'api':
        start_api()
    else:
        start_subscription()
        start_api()
