#! /usr/bin/env python
import logging

import yaml

CONFIG = dict()

log = logging.getLogger(__name__)


class Config:
    def __init__(self, config_file):
        cfg = load_config(config_file)

        self.plugin = cfg.get('plugin', {})
        self.database = cfg.get('database', {})
        self.msg_broker = cfg.get('msg_broker', {})
        self.meta_store = cfg.get('meta_store', {})
        self.data_store = cfg.get('data_store', {})
        self.active_plugins = cfg.get('active_plugins', [])
        self.api = cfg.get('api', {})
        self.custom = cfg.get('custom', {})
        self.packages = cfg.get('packages', {})

    def merge_config(self, override):
        self.plugin.update(override.plugin)
        self.database.update(override.database)
        self.msg_broker.update(override.msg_broker)
        self.meta_store.update(override.meta_store)
        self.data_store.update(override.data_store)
        self.active_plugins.extend(override.active_plugins)
        self.api.update(override.api)
        self.custom.update(override.custom)
        self.packages.update(override.packages)


def load_config(config_file):
    log.info('Loading configuration: {}'.format(config_file))
    with open(config_file, 'r') as stream:
        try:
            global CONFIG
            config = yaml.safe_load(stream) or dict()
        except yaml.YAMLError as e:
            log.warning('Failed parsing yaml config - continues with default configuration')
            log.debug(e)
            config = dict()

    return config
