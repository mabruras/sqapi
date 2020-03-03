import copy
import hashlib
import json
import logging
import multiprocessing
import threading
import time

from sqapi.configuration import detector, fileinfo
from sqapi.configuration.util import Config
from sqapi.configuration.util import signal_blocker
from sqapi.messaging import util
from sqapi.messaging.message import Message
from sqapi.plugin.manager import PluginManager
from sqapi.query import data, meta

CHUNK_SIZE = 65536

log = logging.getLogger(__name__)


class ProcessManager:
    def __init__(self, config: Config, plugin_manager: PluginManager):
        self.config = config
        self.plugin_manager = plugin_manager

        self.listener = detector.detect_listener(self.config.msg_broker, self.process_message)

    def start_subscribing(self):
        log.info('Starting message subscription')

        threading.Thread(
            name='{} Listener'.format(self.listener.__class__),
            target=self.listener.start_listener
        ).start()
        log.debug('Message subscription started')

    def process_message(self, body: bytes):
        try:
            message = util.parse_message(body, self.config.msg_broker)

            log.info('Message processing started')
            data_path, metadata = self.query(message)

            message.type = message.type or fileinfo.get_mime_type(data_path, metadata, self.config.msg_broker)
            fileinfo.validate_mime_type(message.type, self.plugin_manager.accepted_types)

            message.hash_digest = self._calculate_hash_digest(data_path)

            with signal_blocker():
                self.execute_plugins(data_path, message, metadata)

            log.info('Processing completed')

        except LookupError as e:
            log.warning('Could not fetch content and/or metadata at this point: {}'.format(str(e)))

        except Exception as e:
            log.error('Could not process message: {}'.format(str(e)))

    def execute_plugins(self, data_path, message, metadata):
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

    def query(self, message: Message):
        log.info('Querying metadata and content stores')

        data_path = data.download_data(self.config, message)

        if message.metadata:
            log.info('Loading metadata from message')
            metadata = json.loads(message.metadata)

        elif self.config.meta_store:
            log.info('Fetching metadata by query')
            metadata = meta.fetch_metadata(self.config, message)

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
