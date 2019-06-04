#! /usr/bin/env python

import json
import time

from core import logic
from query import data as d_query
from query import metadata as m_query

STATUS_VALIDATING = 'VALIDATING'
STATUS_QUERYING = 'QUERYING'
STATUS_PROCESSING = 'PROCESSING'
STATUS_DONE = 'DONE'
STATUS_RETRY = 'RETRY'
STATUS_FAILED = 'FAILED'

MIME_TYPES = ['image/jpeg', 'image/png', 'image/gif']
MSG_FIELDS = ['data_type', 'data_location', 'meta_location', 'uuid_ref']

PROCESS_DELAY = 5  # Delay to keep the PoC from processing message before data is available


class Processor:
    def __init__(self, config, database):
        self.config = config
        self.msg_fields = config.cfg_broker('message_fields', MSG_FIELDS)
        self.mime_types = config.cfg_broker('supported_mime', MIME_TYPES)

        self.db = database

    def process_message(self, ch, method, properties, body):
        print('Received message. Processing starts after delay ({} seconds)'.format(PROCESS_DELAY))
        time.sleep(PROCESS_DELAY)

        print('Received channel: {}'.format(ch))
        print('Received method: {}'.format(method))
        print('Received properties: {}'.format(properties))
        print('Received message: {}'.format(body))

        try:
            message = self.validate_message(body)

            # Query
            data, meta = self.query(message)

            self.db.update_message(message, STATUS_PROCESSING)
            logic.execute_logic(self.config, self.db, message, meta, data)
            self.db.update_message(message, STATUS_DONE)
        except LookupError as e:
            self.db.update_message(message, STATUS_RETRY, str(e))
            print('Could not fetch data and/or metadata at this point: {}'.format(str(e)))
        except Exception as e:
            try:
                self.db.update_message(message, STATUS_FAILED, str(e))
            except:
                pass
            print('Could not process message')
            print(body)
            print(e)

    def query(self, message):
        self.db.update_message(message, STATUS_QUERYING)

        data = d_query.fetch_data(self.config, message)
        meta = m_query.fetch_metadata(self.config, message)

        return data, meta

    def validate_message(self, body):
        # TODO: Formatting should be configurable here
        # Format
        message = json.loads(body)
        self.db.update_message(message, STATUS_VALIDATING)

        # Validate fields
        for f in self.msg_fields:
            if f not in dict(message.items()):
                raise AttributeError('The field "{}" is missing in the message'.format(f))

        msg_type = message.get('data_type', 'UNKNOWN')
        if msg_type not in self.mime_types:
            raise NotImplementedError('Mime-type "{}" is not supported by this sqAPI'.format(msg_type))

        return message
