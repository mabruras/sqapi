#! /usr/bin/env python
import yaml

CONFIG = dict()


class Config:
    def __init__(self, config_file):
        self.config = dict()
        self.load_config(config_file)

    def load_config(self, config_file):
        print('Loading configuration: {}'.format(config_file))
        with open(config_file, 'r') as stream:
            try:
                global CONFIG
                self.config = yaml.safe_load(stream) or dict()
            except yaml.YAMLError as exc:
                print('Failed parsing yaml config - continues with default configuration')
                print(exc)
                self.config = dict()

    def cfg_broker(self, key, default=None):
        return self.cfg('msg_broker', {}).get(key, default)

    def cfg_meta(self, key, default=None):
        return self.cfg('meta_store', {}).get(key, default)

    def cfg(self, key, default):
        return self.config.get(key, default)
