#! /usr/bin/env python
import importlib
import logging
import os
import threading

from sqapi.query import data as d_query
from sqapi.query import metadata as m_query
from sqapi.util import detector, cfg_util, plugin_util, packager

STATUS_VALIDATING = 'VALIDATING'
STATUS_QUERYING = 'QUERYING'
STATUS_PROCESSING = 'PROCESSING'
STATUS_DONE = 'DONE'
STATUS_RETRY = 'RETRY'
STATUS_FAILED = 'FAILED'

log = logging.getLogger(__name__)


class Processor:
    def __init__(self, config, plugin_name, plugin):
        self.config = config

        self.name = plugin_name
        log.info('PLUGIN = {}'.format(plugin))
        log.info('TEST = {}'.format(__file__))
        self.plugin_dir = plugin.replace('.', os.sep)
        log.info('PLUGIN DIR = {}'.format(self.plugin_dir))
        self.config.plugin = {'name': self.name, 'directory': self.plugin_dir}

        config_file = os.path.join(self.plugin_dir, 'config.yml')
        custom_config = cfg_util.Config(config_file)
        self.config.merge_config(custom_config)

        if config.packages.get('install', True):
            log.info('Installing necessary packages for {}'.format(plugin_name))
            packager.install_packages(self.config.packages)

        plugin = importlib.import_module(plugin)

        self.execute = plugin.execute
        blueprints_dir = self.config.api.get('blueprints_directory', None)
        self.blueprints = plugin_util.load_blueprints(plugin_name, blueprints_dir)

        self.config.database['init'] = self.validate_db_init_script(self.config.database)
        self.database = detector.detect_database(self.config.database)
        self.database.initialize_database()

        self.listener = detector.detect_listener(self.config.msg_broker, self.process_message)

    def start_loader(self):
        log.info('{}: Starting listeners'.format(self.name))
        # Setup sqAPI general exchange listener
        log.debug('Starting Exchange Listener for {}'.format(self.name))
        threading.Thread(
            name='{} Exchange Listener'.format(self.name),
            target=self.listener.listen_exchange
        ).start()

        # Setup sqAPI unique queue listener
        log.debug('Starting Queue Listener for {}'.format(self.name))
        threading.Thread(
            name='{} Queue Listener'.format(self.name),
            target=self.listener.listen_queue
        ).start()

    def process_message(self, body: dict):

        try:
            log.info('Processing started')
            # Query
            data, meta = self.query(body)

            self.database.update_message(body, STATUS_PROCESSING)

            log.info('Executing logic for {} plugin'.format(self.name))
            self.execute(self.config, self.database, body, meta, data)
            self.database.update_message(body, STATUS_DONE)
            log.info('Processing completed')
        except LookupError as e:
            self.database.update_message(body, STATUS_RETRY, str(e))
            log.warning('Could not fetch data and/or metadata at this point: {}'.format(str(e)))
        except Exception as e:
            try:
                self.database.update_message(body, STATUS_FAILED, str(e))
            except:
                pass
            log.warning('{} could not process message'.format(self.name))
            log.warning(str(e))
            log.debug(body)

    def query(self, message):
        log.info('Querying metadata and data stores')
        self.database.update_message(message, STATUS_QUERYING)

        data = d_query.fetch_data(self.config, message)
        meta = m_query.fetch_metadata(self.config, message)

        log.debug('Queries completed')
        return data, meta

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
