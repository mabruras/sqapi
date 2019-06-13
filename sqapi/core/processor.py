#! /usr/bin/env python

import json
import logging
import os
import threading
import time

from sqapi.query import data as d_query
from sqapi.query import metadata as m_query
from sqapi.util import detector, cfg_util, plugin_util

STATUS_VALIDATING = 'VALIDATING'
STATUS_QUERYING = 'QUERYING'
STATUS_PROCESSING = 'PROCESSING'
STATUS_DONE = 'DONE'
STATUS_RETRY = 'RETRY'
STATUS_FAILED = 'FAILED'

MIME_TYPES = ['image/jpeg', 'image/png', 'image/gif']
MSG_FIELDS = ['data_type', 'data_location', 'meta_location', 'uuid_ref']

log = logging.getLogger(__name__)


class Processor:
    def __init__(self, config, plugin_name, plugin):
        self.config = config

        self.plugin = plugin
        self.name = plugin_name
        self.plugin_dir = os.path.dirname(plugin.__file__)
        self.config.plugin = {'name': self.name, 'directory': self.plugin_dir}

        config_file = os.path.join(self.plugin_dir, 'config.yml')
        custom_config = cfg_util.Config(config_file)
        self.config.merge_config(custom_config)

        self.execute = plugin.execute
        blueprints_dir = self.config.api.get('blueprints_directory', None)
        self.blueprints = plugin_util.load_blueprints(plugin_name, blueprints_dir)

        self.config.database['init'] = self.validate_db_init_script(self.config.database)
        self.database = detector.detect_database(self.config.database)
        self.database.initialize_database()

        self.listener = detector.detect_listener(self.config.msg_broker)

        self.msg_fields = config.msg_broker.get('message_fields', MSG_FIELDS)
        self.mime_types = config.msg_broker.get('supported_mime', MIME_TYPES)

    def start_loader(self):
        # Setup sqAPI general exchange listener
        log.info('Starting Exchange Listener for {}'.format(self.name))
        threading.Thread(
            name='{} Exchange Listener'.format(self.name),
            target=self.listener.listen_exchange,
            args=[self.process_message]
        ).start()

        # Setup sqAPI unique queue listener
        log.info('Starting Queue Listener for {}'.format(self.name))
        threading.Thread(
            name='{} Queue Listener'.format(self.name),
            target=self.listener.listen_queue,
            args=[self.process_message]
        ).start()

    def process_message(self, ch, method, properties, body):
        delay = self.config.msg_broker.get('process_delay', 0)
        log.info('Received message. Processing starts after delay ({} seconds)'.format(delay))
        time.sleep(delay)

        log.debug('Received channel: {}'.format(ch))
        log.debug('Received method: {}'.format(method))
        log.debug('Received properties: {}'.format(properties))
        log.debug('Received message: {}'.format(body))

        try:
            log.info('Processing started')
            message = self.validate_message(body)

            # Query
            data, meta = self.query(message)

            self.database.update_message(message, STATUS_PROCESSING)

            log.info('Executing logic for "{}" plugin'.format(self.name))
            self.execute(self.config, self.database, message, meta, data)
            self.database.update_message(message, STATUS_DONE)
            log.info('Processing completed')
        except LookupError as e:
            self.database.update_message(message, STATUS_RETRY, str(e))
            log.warning('Could not fetch data and/or metadata at this point: {}'.format(str(e)))
        except Exception as e:
            try:
                self.database.update_message(message, STATUS_FAILED, str(e))
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

    def validate_message(self, body):
        log.info('Validating message')
        # Format
        message = json.loads(body)
        self.database.update_message(message, STATUS_VALIDATING)

        # Validate fields
        self.validate_fields(message)

        log.debug('Validating message mime type')
        msg_type = message.get('data_type', 'UNKNOWN')
        if self.mime_types and msg_type not in self.mime_types:
            err = 'Mime type "{}" is not supported by this sqAPI'.format(msg_type)
            log.debug(err)
            raise NotImplementedError(err)

        log.debug('Message validated successfully')
        return message

    def validate_fields(self, message):
        log.debug('Validating required fields')
        log.debug('Required fields: {}'.format(self.msg_fields))
        missing_fields = []

        for f in self.msg_fields:
            if f not in dict(message.items()):
                log.debug('Field {} is missing'.format(f))
                missing_fields.append(f)

        if missing_fields:
            err = 'The field(/s) "{}" are missing in the message'.format('", "'.join(missing_fields))
            log.debug(err)
            raise AttributeError(err)

    def validate_db_init_script(self, config):
        init_path = config.get('init', None)

        if not init_path:
            err = 'Missing configuration for database initialization script in plugin "{}"'.format(self.name)
            log.warning(err)
            raise AttributeError('Missing configuration for database initialization script')

        if not os.path.exists(init_path):
            init_path = os.path.join(self.plugin_dir, init_path)
        if not os.path.exists(init_path):
            err = 'Database initialization script defined ({}) does not exist'.format(init_path)
            log.warning(err)
            raise AttributeError('Database initialization script defined ({}) does not exist'.format(init_path))

        return init_path
