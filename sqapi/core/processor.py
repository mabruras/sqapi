#! /usr/bin/env python

import json

import redis

MIME_TYPES = ['image/jpeg', 'image/png', 'image/gif']
MSG_FIELDS = ['data_type', 'data_location', 'meta_location', 'uuid_ref']


class Processor:
    def __init__(self, config):
        self.config = config

    def process_message(self, ch, method, properties, body):
        print('Received channel: {}'.format(ch))
        print('Received method: {}'.format(method))
        print('Received properties: {}'.format(properties))
        print('Received message: {}'.format(body))

        try:
            message = self.validate_message(body)

            # Query
            data = self.query_data(message)
            meta = self.query_metadata(message)

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
        for f in MSG_FIELDS:
            if f not in dict(message.items()):
                raise AttributeError('The field "{}" is missing in the message'.format(f))

        msg_type = message.get('data_type', 'UNKNOWN')
        if msg_type not in MIME_TYPES:
            raise NotImplementedError('Mime-type "{}" is not supported by this sqAPI'.format(msg_type))

        return message

    def query_data(self, message):
        # TODO: Based on message extract the following:
        # Data location (database, disk, object store etc.) + identifier (lookup reference)
        loc = message.get('data_location', None)
        if not loc:
            raise AttributeError('Could not find "data_location" in message')
        data = self.fetch_data(loc)

        return data

    def fetch_data(self, location):
        disk_loc = self.fetch_data_to_disk(location)

        return self.fetch_file_from_disk(disk_loc)

    def fetch_data_to_disk(self, location):
        # TODO: this return should be from a specific/configurable module
        # so it will download/get file data from all kinds of storage places

        # TODO: Now location is returned since we know in this POC that the file is on disk
        return location

    def fetch_file_from_disk(self, file):
        return open(file, "rb")

    def query_metadata(self, message):
        # TODO: Based on query content, the query should be executed to the intended system:
        # Key/Value location (Redis, file etc.) + identifier (lookup reference) + optional field limitation

        meta_store = self.config.cfg_meta('type', 'redis')

        # TODO: More generic selection of metadata store?
        if not meta_store:
            # Default Metadata store is Redis
            print('Using default metadata store: Redis')
            clazz = redis.Redis
        elif meta_store.lower() == 'redis':
            print('Redis was detected as metadata store')
            clazz = redis.Redis
        else:
            print('{} is not a supported metadata store'.format(type))
            clazz = None
            exit(1)

        return self.fetch_meta_from_redis(clazz, message)

    def fetch_meta_from_redis(self, clazz, message):
        host = self.config.cfg_meta('host', 'localhost')
        port = self.config.cfg_meta('port', 6379)
        r = clazz(host=host, port=port)

        return r.get(message.get('uuid_ref'))

    def process_content(self, meta, data):
        print('Meta processing:')
        print(meta)

        print('Data processing:')
        out = data.read()
        data.close()
        print('File size: {}'.format(len(out)))
