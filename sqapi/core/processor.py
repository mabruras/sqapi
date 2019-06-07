#! /usr/bin/env python

import json
import os
import threading
import time

from query import data as d_query
from query import metadata as m_query
from util import detector, cfg_util, plugin_util

STATUS_VALIDATING = 'VALIDATING'
STATUS_QUERYING = 'QUERYING'
STATUS_PROCESSING = 'PROCESSING'
STATUS_DONE = 'DONE'
STATUS_RETRY = 'RETRY'
STATUS_FAILED = 'FAILED'

MIME_TYPES = ['image/jpeg', 'image/png', 'image/gif']
MSG_FIELDS = ['data_type', 'data_location', 'meta_location', 'uuid_ref']


class Processor:
    def __init__(self, config, plugin_name, plugin):
        self.plugin = plugin
        self.name = plugin_name
        self.plugin_dir = os.path.dirname(plugin.__file__)

        self.config = config
        config_file = os.path.join(self.plugin_dir, 'config.yml')
        custom_config = cfg_util.Config(config_file)
        self.config.merge_config(custom_config)

        self.execute = plugin.execute  # Actual business logic to create a data structure

        # TODO: Handle import blueprints
        # Maybe only: plugin.blueprints will be enough (if defined in __init__.py)
        self.blueprints = plugin_util.load_blueprints(plugin_name, self.config.api.get('blueprints_directory', None))

        self.config.database['init'] = self.validate_db_init_script(self.config.database)
        self.database = detector.detect_database(self.config.database)
        self.database.initialize_database()

        self.listener = detector.detect_listener(self.config.msg_broker)

        self.msg_fields = config.msg_broker.get('message_fields', MSG_FIELDS)
        self.mime_types = config.msg_broker.get('supported_mime', MIME_TYPES)

    def start_loader(self):
        # Setup sqAPI general exchange listener
        threading.Thread(
            name='{} Exchange Listener'.format(self.name),
            target=self.listener.listen_exchange,
            args=[self.process_message]
        ).start()

        # Setup sqAPI unique queue listener
        threading.Thread(
            name='{} Queue Listener'.format(self.name),
            target=self.listener.listen_queue,
            args=[self.process_message]
        ).start()

    def process_message(self, ch, method, properties, body):
        delay = self.config.msg_broker.get('process_delay', 0)
        print('Received message. Processing starts after delay ({} seconds)'.format(delay))
        time.sleep(delay)

        print('Received channel: {}'.format(ch))
        print('Received method: {}'.format(method))
        print('Received properties: {}'.format(properties))
        print('Received message: {}'.format(body))

        try:
            message = self.validate_message(body)

            # Query
            data, meta = self.query(message)

            self.database.update_message(message, STATUS_PROCESSING)
            self.execute(self.config, self.database, message, meta, data)
            self.database.update_message(message, STATUS_DONE)
        except LookupError as e:
            self.database.update_message(message, STATUS_RETRY, str(e))
            print('Could not fetch data and/or metadata at this point: {}'.format(str(e)))
        except Exception as e:
            try:
                self.database.update_message(message, STATUS_FAILED, str(e))
            except:
                pass
            print('{} could not process message'.format(self.name))
            print(body)
            print(e)

    def query(self, message):
        self.database.update_message(message, STATUS_QUERYING)

        data = d_query.fetch_data(self.config, message)
        meta = m_query.fetch_metadata(self.config, message)

        return data, meta

    def validate_message(self, body):
        # TODO: Formatting should be configurable here
        # Format
        message = json.loads(body)
        self.database.update_message(message, STATUS_VALIDATING)

        # Validate fields
        self.validate_fields(message)

        msg_type = message.get('data_type', 'UNKNOWN')
        if msg_type not in self.mime_types:
            raise NotImplementedError('Mime-type "{}" is not supported by this sqAPI'.format(msg_type))

        return message

    def validate_fields(self, message):
        missing_fields = []

        for f in self.msg_fields:
            if f not in dict(message.items()):
                missing_fields.append(f)

        if missing_fields:
            raise AttributeError('The field(/s) "{}" are missing in the message'.format('", "'.join(missing_fields)))

    def validate_db_init_script(self, config):
        init_path = config.get('init', None)

        if not init_path:
            raise AttributeError('Missing configuration for database initialization script')

        if not os.path.exists(init_path):
            init_path = os.path.join(self.plugin_dir, init_path)
        if not os.path.exists(init_path):
            raise AttributeError('Database initialization script defined ({}) does not exist'.format(init_path))

        return init_path
