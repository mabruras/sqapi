#! /usr/bin/env python3
import importlib
import logging
import os
from os import path

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

    target_module = config.get('type', 'postgres')
    directory = os.sep.join(['sqapi', 'connectors', 'db'])

    try:
        module = find_module(target_module, directory)

        return module.Database(config)
    except Exception as e:
        err = '{} is not a supported Database type: '.format(target_module, str(e))
        log.warning(err)
        raise AttributeError(err)


def detect_listener(config):
    log.debug('Looking up listener type in configuration')
    log.debug(config)

    target_module = config.get('type', 'rabbitmq')
    directory = os.sep.join(['sqapi', 'connectors', 'listeners'])

    try:
        module = find_module(target_module, directory)

        return module.Listener(config)
    except Exception as e:
        err = '{} is not a supported Listener type: '.format(target_module, str(e))
        log.warning(err)
        raise AttributeError(err)


def detect_data_connectors(config):
    log.debug('Looking up data store connector type in configuration')
    log.debug(config)

    target_module = config.get('type', 'disk')
    directory = os.sep.join(['sqapi', 'connectors', 'data'])

    try:
        module = find_module(target_module, directory)

        return module
    except Exception as e:
        err = '{} is not a supported Database type: '.format(target_module, str(e))
        log.warning(err)
        raise AttributeError(err)


def find_module(target_module, directory):
    module_dict = detect_modules(directory)

    log.debug('Found {} available modules'.format(len(module_dict)))
    log.debug(module_dict)

    module = importlib.import_module(module_dict.get(target_module))

    return module


def detect_modules(directory, res_as_dir=False) -> dict:
    package = '.'.join(directory.split(os.sep))

    return dict({
        e.rstrip('.py'): '.'.join([package, e]).strip('.py')
        for e in os.listdir(directory)

        if not e.startswith('__') and (
            (res_as_dir and path.isdir(path.join(directory, e)))
            or
            (not res_as_dir and path.isfile(path.join(directory, e))))
    })
