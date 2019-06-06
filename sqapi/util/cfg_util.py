#! /usr/bin/env python
import yaml

CONFIG = dict()


class Config:
    def __init__(self, config_file):
        cfg = load_config(config_file)

        self.database = cfg.get('database', {})
        self.msg_broker = cfg.get('msg_broker', {})
        self.meta_store = cfg.get('meta_store', {})
        self.data_store = cfg.get('data_store', {})
        self.api = cfg.get('api', {})

    def merge_config(self, override):
        self.database.update(override.database)
        self.msg_broker.update(override.msg_broker)
        self.meta_store.update(override.meta_store)
        self.data_store.update(override.data_store)
        self.api.update(override.api)


def load_config(config_file):
    print('Loading configuration: {}'.format(config_file))
    with open(config_file, 'r') as stream:
        try:
            global CONFIG
            config = yaml.safe_load(stream) or dict()
        except yaml.YAMLError as exc:
            print('Failed parsing yaml config - continues with default configuration')
            print(exc)
            config = dict()

    return config
