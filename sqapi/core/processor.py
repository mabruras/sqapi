#! /usr/bin/env python

import json

from query import data as d_query
from query import metadata as m_query

MIME_TYPES = ['image/jpeg', 'image/png', 'image/gif']
MSG_FIELDS = ['data_type', 'data_location', 'meta_location', 'uuid_ref']


class Processor:
    def __init__(self, config, database):
        self.config = config
        self.msg_fields = config.cfg_broker('message_fields', MSG_FIELDS)
        self.mime_types = config.cfg_broker('supported_mime', MIME_TYPES)

        self.db = database

    def process_message(self, ch, method, properties, body):
        print('Received channel: {}'.format(ch))
        print('Received method: {}'.format(method))
        print('Received properties: {}'.format(properties))
        print('Received message: {}'.format(body))

        try:
            message = self.validate_message(body)

            # Query
            data = d_query.fetch_data(self.config, message)
            meta = m_query.fetch_metadata(self.config, message)

            self.process_content(meta, data)
        except Exception as e:
            print('Could not process message')
            print(body)
            print(e)

    def validate_message(self, body):
        # TODO: Formatting should be configurable here
        # Format
        message = json.loads(body)

        # Validate fields
        for f in self.msg_fields:
            if f not in dict(message.items()):
                raise AttributeError('The field "{}" is missing in the message'.format(f))

        msg_type = message.get('data_type', 'UNKNOWN')
        if msg_type not in self.mime_types:
            raise NotImplementedError('Mime-type "{}" is not supported by this sqAPI'.format(msg_type))

        return message

    def process_content(self, meta, data):
        print('Meta processing:')
        print(meta)

        print('Data processing:')
        out = data.read()
        data.close()
        print('File size: {}'.format(len(out)))
