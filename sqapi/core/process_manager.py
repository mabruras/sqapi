import copy
import hashlib
import json
import logging
import multiprocessing
import time

import filetype

from sqapi.core.message import Message
from sqapi.core.plugin_manager import PluginManager
from sqapi.query import data as q_data, metadata as q_meta
from sqapi.util import detector
from sqapi.util.cfg_util import Config

CHUNK_SIZE = 65536

log = logging.getLogger(__name__)


class ProcessManager:
    def __init__(self, config: Config, plugin_manager: PluginManager):
        self.config = config
        self.plugin_manager = plugin_manager

        self.database = detector.detect_database(self.config.database)
        self.listener = detector.detect_listener(self.config.msg_broker, self.process_message)

    def start_subscribing(self):
        log.info('Starting message subscription')
        self.listener.start_listeners()
        log.debug('Message subscription started')

    def process_message(self, message: Message):
        try:
            log.info('Message processing started')
            data_path, metadata = self.query(message)

            if not message.type:
                message.type = self.detect_filetype(data_path).mime
            self.check_mime_type(message)

            message.hash_digest = self._calculate_hash_digest(data_path)

            log.debug('Creating processor pool of plugin executions')
            process_pool = [
                multiprocessing.Process(target=self.plugin_execution, args=[
                    plugin, message, metadata, data_path
                ]) for plugin in self.plugin_manager.plugins
                if self.valid_data_type(message, plugin)
            ]

            log.debug('Starting processor pool')
            [t.start() for t in process_pool]
            [t.join() for t in process_pool]

            log.info('Processing completed')

        except LookupError as e:
            log.warning('Could not fetch data and/or metadata at this point: {}'.format(str(e)))

        except Exception as e:
            log.error('Could not process message: {}'.format(str(e)))
            log.debug(message)
            log.debug(e)

    def detect_filetype(self, file_path):
        return filetype.guess(file_path) or self._get_default_filetype()

    def check_mime_type(self, mime):
        log.debug('Validating mime type')
        log.debug('Accepted mime types: {}'.format(self.plugin_manager.accepted_types))

        if self.plugin_manager.accepted_types and (
                mime not in self.plugin_manager.accepted_types
                and '*' not in self.plugin_manager.accepted_types
        ):
            err = 'Mime type "{}" is not supported by any of the active sqAPI plugins'.format(mime)
            log.debug(err)
            raise NotImplementedError(err)

    def query(self, message: Message):
        log.info('Querying metadata and data stores')

        data_path = q_data.download_data(self.config, message)

        if message.metadata:
            log.debug('Loading metadata from message')
            metadata = json.loads(message.metadata)

        elif self.config.meta_store:
            log.debug('Fetching metadata by query')
            metadata = q_meta.fetch_metadata(self.config, message)

        else:
            log.debug('No metadata storage defined in configuration, skipping metadata retrieval')
            metadata = {}

        log.debug('Queries completed')
        return data_path, metadata

    @staticmethod
    def plugin_execution(plugin, message, metadata, data_path):
        log.info('{} started processing on {}'.format(plugin.name, message.uuid))
        start = time.time()

        try:
            plugin.execute(
                plugin.config,
                plugin.database,
                copy.deepcopy(message),
                copy.deepcopy(metadata),
                open(data_path, 'rb')
            )

        except Exception as e:
            log.warning('{} failed processing {}: {}'.format(plugin.name, message.uuid, str(e)))

        else:
            run_time = (time.time() - start) * 1000.0
            log.info('{} used {} (milliseconds) processing {}'.format(plugin.name, run_time, message.uuid))

    @staticmethod
    def _calculate_hash_digest(file_path):
        digest = hashlib.sha256()

        with open(file_path, 'rb') as f:
            while True:
                chunk = f.read(CHUNK_SIZE)

                if not chunk:
                    break

                digest.update(chunk)

        return digest.hexdigest()

    @staticmethod
    def valid_data_type(message: Message, plugin):
        accepted_types = plugin.config.msg_broker.get('supported_mime') or []

        return message.type in accepted_types or not accepted_types

    @staticmethod
    def _get_default_filetype():
        kind = type('', (), {})()
        kind.extension = None
        kind.mime = 'application/octet-stream'

        return kind
