#! /usr/bin/env python3
import importlib
import os
from os import path

from db import postgres
from listeners import rabbitmq


def detect_plugins(directory):
    plugins = {}

    plugin_list = ['.'.join([directory, d]) for d
                   in os.listdir(directory)
                   if path.isdir(path.join(directory, d))
                   and not d.startswith('__')]

    print('Found {} available plugins'.format(len(plugin_list)))
    for plugin_name in plugin_list:
        plugin = importlib.import_module(plugin_name)
        plugins.update({plugin.__name__.split('.')[1]: plugin})

    return plugins


def detect_database(config):
    db_type = config.get('type', 'postgres')

    if not db_type:
        # Default database is PostgreSQL
        print('Using default database')
        clazz = postgres.Postgres
    elif db_type.lower() == 'postgres':
        print('PostgreSQL detected as database type')
        clazz = postgres.Postgres
    else:
        err = '{} is not a supported database type'.format(type)
        print(err)
        raise AttributeError(err)

    return clazz(config)


def detect_listener(config):
    listener_type = config.get('type', 'rabbitmq')

    # TODO: More generic selection of listener type?
    # Eg.: 
    # listeners = { 'listener-name': listener_module }
    # clazz = listeners.get(listener_type, None)
    # if not clazz: raise Error(err) else return clazz(config)

    if not listener_type:
        # Default Listener is RabbitMQ
        print('Using default listener')
        clazz = rabbitmq.RabbitMQ
    elif listener_type.lower() == 'rabbitmq':
        print('RabbitMQ detected as listener type')
        clazz = rabbitmq.RabbitMQ
    else:
        err = '{} is not a supported Listener type'.format(type)
        print(err)
        raise AttributeError(err)

    return clazz(config)
