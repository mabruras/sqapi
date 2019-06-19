#! /usr/bin/env python3
import importlib
import logging
import os
from os import path

from sqapi.db import postgres

log = logging.getLogger(__name__)


def detect_plugins():
    directory = os.sep.join(['sqapi', 'plugins'])

    log.debug('Detecting plugins in dir {}'.format(directory))
    plugin_dict = detect_modules(directory, True)

    log.info('Found {} available plugins'.format(len(plugin_dict)))
    log.debug(plugin_dict)

    plugins = {}
    for plugin_name in plugin_dict:
        log.debug('Importing plugin: {}'.format(plugin_name))
        plugin = importlib.import_module(plugin_dict.get(plugin_name))
        plugins.update({plugin.__name__.split('.')[-1]: plugin})

    return plugins


def detect_database(config):
    log.debug('Looking up database type in configuration')
    log.debug(config)
    db_type = config.get('type', 'postgres')

    if not db_type or db_type.lower() == 'postgres':
        log.info('PostgreSQL (default) detected as database type')
        clazz = postgres.Postgres
    else:
        err = '{} is not a supported database type'.format(type)
        log.warning(err)
        raise AttributeError(err)

    return clazz(config)


def detect_listener(config):
    log.debug('Looking up listener type in configuration')
    log.debug(config)

    listener_type = config.get('type', 'rabbitmq')
    directory = os.sep.join(['sqapi', 'connectors', 'listeners'])

    try:
        listener_dict = detect_modules(directory, False)

        log.debug('Found {} available listeners'.format(len(listener_dict)))
        log.debug(listener_dict)

        module = importlib.import_module(listener_dict.get(listener_type))

        return module.Listener(config)
    except Exception as e:
        err = '{} is not a supported Listener type: '.format(listener_type, str(e))
        log.warning(err)
        raise AttributeError(err)


def detect_modules(directory, res_as_dir=False) -> dict:
    package = '.'.join(directory.split(os.sep))

    return dict({
        e.strip('.py'): '.'.join([package, e]).strip('.py')
        for e in os.listdir(directory)

        if not e.startswith('__') and (
            (res_as_dir and path.isdir(path.join(directory, e)))
            or
            (not res_as_dir and path.isfile(path.join(directory, e))))
    })
