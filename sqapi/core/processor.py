#! /usr/bin/env python
import importlib
import logging
import os

from sqapi.util import detector, cfg_util, plugin_util, packager

log = logging.getLogger(__name__)


class Processor:
    def __init__(self, config, plugin_name, plugin):
        self.config = config

        self.name = plugin_name
        self.plugin_dir = plugin.replace('.', os.sep)
        self.config.plugin = {'name': self.name, 'directory': self.plugin_dir}

        config_file = os.path.join(self.plugin_dir, 'config.yml')
        custom_config = cfg_util.Config(config_file)
        self.config.merge_config(custom_config)

        if self.config.packages.get('install', True):
            log.info('Installing necessary packages for {}'.format(plugin_name))
            packager.install_packages(self.config.packages)

        plugin = importlib.import_module(plugin)

        self.execute = plugin.execute
        blueprints_dir = self.config.api.get('blueprints_directory', None)
        self.blueprints = plugin_util.load_blueprints(plugin_name, blueprints_dir)

        self.config.database['init'] = self.validate_db_init_script(self.config.database)
        self.database = detector.detect_database(self.config.database)
        self.database.initialize_database()

    def validate_db_init_script(self, config):
        init_path = config.get('init', None)

        if not init_path:
            err = 'Missing configuration for database initialization script in plugin {}'.format(self.name)
            log.warning(err)
            raise AttributeError('Missing configuration for database initialization script')

        if not os.path.exists(init_path):
            init_path = os.path.join(self.plugin_dir, init_path)
        if not os.path.exists(init_path):
            err = 'Database initialization script defined ({}) does not exist'.format(init_path)
            log.warning(err)
            raise AttributeError('Database initialization script defined ({}) does not exist'.format(init_path))

        return init_path
