#! /usr/bin/env python3
import importlib
import logging
import os
from os import path

from sqapi.connectors.listeners import rabbitmq
from sqapi.db import postgres

log = logging.getLogger(__name__)


def detect_plugins():
    directory = os.sep.join(['sqapi', 'plugins'])

    log.debug('Detecting plugins in dir {}'.format(directory))
    plugin_list = detect_modules(directory, True)

    log.info('Found {} available plugins'.format(len(plugin_list)))
    log.debug(plugin_list)

    plugins = {}
    for plugin_name in plugin_list:
        log.debug('Importing plugin: {}'.format(plugin_name))
        plugin = importlib.import_module(plugin_name)
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

    # TODO: More generic selection of listener type?
    # Eg.:
    # listeners = { 'listener-name': listener_module }
    # clazz = listeners.get(listener_type, None)
    # if not clazz: raise Error(err) else return clazz(config)

    if not listener_type or listener_type.lower() == 'rabbitmq':
        log.info('RabbitMQ (default) detected as listener type')
        clazz = rabbitmq.RabbitMQ
    else:
        err = '{} is not a supported Listener type'.format(type)
        log.warning(err)
        raise AttributeError(err)

    return clazz(config)


def detect_modules(directory, res_as_dir=False):
    package = '.'.join(directory.split(os.sep))

    return [
        '.'.join([package, e]) for e in os.listdir(directory)

        if not e.startswith('__') and (
                (
                        res_as_dir and path.isdir(path.join(directory, e))
                ) or (
                        not res_as_dir and path.isfile(path.join(directory, e))
                )
        )
    ]
