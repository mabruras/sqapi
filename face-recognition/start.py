#! /usr/bin/env python
import os

import yaml

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
    subscriber.start_listener(configuration=CONFIG.get('listener', {}))


def callback():
    pass


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
