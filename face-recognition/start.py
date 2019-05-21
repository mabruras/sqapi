#! /usr/bin/env python
import os

import yaml

from transform import transformer

CONFIG = dict()

PROJECT_DIR = os.environ.get('WRK_DIR', '.')
CONFIG_DIR = '{}{}conf'.format(PROJECT_DIR, os.sep)
CONFIG_FILE = '{}{}sqapi.yml'.format(CONFIG_DIR, os.sep)


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


def initialize_subscriber():
    print('Initializing subscriber')
    from subscription import subscriber
    # subscriber.start_listener(configuration=CONFIG.get('listener', {}), callback=callback)
    cfg = CONFIG.get('listener', {})
    callback = get_msg_transformer()

    subscriber.start_listener(configuration=cfg, transformer=transformer, callback=callback)


def get_msg_transformer():
    cfg = CONFIG.get('transformer', {})

    return transformer.get_message_transformer(configuration=cfg)


def initialize_queries():
    print('Initializing query manager')
    pass


def initialize_api():
    print('Initializing API')
    pass


def verify_setup():
    print('Verifying setup, configuration and connections')
    pass


if __name__ == '__main__':
    load_config()

    initialize_subscriber()
    initialize_queries()
    initialize_api()
    verify_setup()
