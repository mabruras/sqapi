#! /usr/bin/env python
import os
import sys

import logging
import re
import signal
import yaml
from contextlib import contextmanager

CONFIG = dict()

log = logging.getLogger(__name__)

received_signal = False
in_progress = False


class Config:
    def __init__(self, config_file):
        cfg = load_config(config_file)

        self.plugin = cfg.get('plugin') or {}
        self.database = cfg.get('database') or {}
        self.broker = cfg.get('broker') or {}
        self.message = cfg.get('message') or {}
        self.meta_store = cfg.get('meta_store') or {}
        self.data_store = cfg.get('data_store') or {}
        self.active_plugins = cfg.get('active_plugins') or []
        self.disabled_plugins = cfg.get('disabled_plugins') or []
        self.api = cfg.get('api') or {}
        self.custom = cfg.get('custom') or {}
        self.packages = cfg.get('packages') or {}

    def merge_config(self, override):
        self.plugin.update(override.plugin)
        self.database.update(override.database)
        self.broker.update(override.broker)
        self.message.update(override.message)
        self.meta_store.update(override.meta_store)
        self.data_store.update(override.data_store)
        self.active_plugins.extend(override.active_plugins)
        self.disabled_plugins.extend(override.disabled_plugins)
        self.api.update(override.api)
        self.custom.update(override.custom)
        self.packages.update(override.packages)


def load_config(config_file):
    log.info('Loading configuration: {}'.format(config_file))
    path_matcher = re.compile(r'.*\$\{([^}^{]+)\}.*')

    def path_constructor(loader, node):
        return os.path.expandvars(node.value)

    class EnvVarLoader(yaml.SafeLoader):
        def __init__(self, stream):
            super().__init__(stream)

    EnvVarLoader.add_implicit_resolver('!path', path_matcher, None)
    EnvVarLoader.add_constructor('!path', path_constructor)

    with open(config_file, 'r') as stream:
        try:
            global CONFIG
            log.debug('Loading yaml config')
            config = yaml.load(stream, Loader=EnvVarLoader) or dict()

        except yaml.YAMLError as e:
            log.warning('Failed parsing yaml config - continues with default configuration')
            log.debug(e)
            config = dict()

    return config


def signal_handler(sig, frame):
    global received_signal
    log.info('Shutdown signal received: {}'.format(sig))
    received_signal = True

    if not in_progress:
        log.info('sqAPI is shutting down')
        sys.exit()

    log.warning('sqAPI is still working.. Shutting down after finishing current processes')


@contextmanager
def signal_blocker():
    global in_progress
    global received_signal

    if received_signal:
        sys.exit()

    try:
        in_progress = True
        yield

    finally:
        in_progress = False

        if received_signal:
            log.info('Completed current processes; sqAPI is shutting down')
            sys.exit()


class Timeout:

    def __init__(self, seconds=30, error_message='TimeoutError'):
        self.seconds = seconds
        self.error_message = error_message

    def handle_timeout(self, signum, frame):
        raise TimeoutError(self.error_message)

    def __enter__(self):
        if self.seconds:
            signal.signal(signal.SIGALRM, self.handle_timeout)
            signal.alarm(self.seconds)

    def exit(self, exc_type, exc_val, exc_tb):
        signal.alarm(0)
