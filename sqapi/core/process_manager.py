import copy
import logging
import os
import threading

from sqapi.core.message import Message
from sqapi.core.processor import Processor
from sqapi.query import data as q_data, metadata as q_meta
from sqapi.util import detector
from sqapi.util.cfg_util import Config

SINGLE_PLUGIN = os.environ.get('PLUGIN', None)

STATUS_VALIDATING = 'VALIDATING'
STATUS_QUERYING = 'QUERYING'
STATUS_PROCESSING = 'PROCESSING'
STATUS_DONE = 'DONE'
STATUS_RETRY = 'RETRY'
STATUS_FAILED = 'FAILED'

log = logging.getLogger(__name__)


class ProcessManager:
    def __init__(self, config: Config):
        self.config = config

        self.database = detector.detect_database(self.config.database)
        self.database.initialize_message_table()

        self.plugins = []
        self.failed_plugins = []
        self.register_plugins()

        self.accepted_types = set()
        for data_types in [p.config.msg_broker.get('supported_mime', []) for p in self.plugins]:
            self.accepted_types.update(data_types)

        self.listener = detector.detect_listener(self.config.msg_broker, self.process_message)

    def register_plugins(self):
        log.debug('Searching for available and active plugins')
        detected_plugins = detector.detect_plugins().items()
        for plugin_name, plugin in detected_plugins:
            if not self.active_plugin(plugin_name):
                log.debug('Plugin {} is not listed as active'.format(plugin_name))
                continue

            try:
                log.debug('Registering a processor for plugin {}'.format(plugin_name))
                processor = Processor(copy.copy(self.config), plugin_name, plugin)
                self.plugins.append(processor)

            except Exception as e:
                err = 'Could not register plugin {} ({}): {}'.format(plugin_name, plugin, str(e))
                log.warning(err)
                self.failed_plugins.append({
                    plugin_name: err
                })

        log.info('{}/{} registered plugins'.format(len(self.plugins), len(detected_plugins)))
        log.info('{}/{} failed plugins'.format(len(self.failed_plugins), len(detected_plugins)))
        log.info('{}/{} inactive plugins'.format(len(self.plugins) + len(self.failed_plugins), len(detected_plugins)))

    def active_plugin(self, plugin_name):
        if SINGLE_PLUGIN:
            return SINGLE_PLUGIN == plugin_name

        return not self.config.active_plugins or plugin_name in self.config.active_plugins

    def start_subscribing(self):
        log.debug('Starting message subscription')

        # Setup sqAPI general exchange listener
        log.debug('Starting Exchange Listener')
        threading.Thread(
            name='Exchange Listener',
            target=self.listener.listen_exchange
        ).start()

        # Setup sqAPI unique queue listener
        log.debug('Starting Queue Listener')
        threading.Thread(
            name='Queue Listener',
            target=self.listener.listen_queue
        ).start()

        log.debug('Message subscription started')

    def process_message(self, message: Message):
        log.info('Message processing started')
        self.check_mime_type(message.body)

        try:
            # Query
            data_path, metadata = self.query(message)
            self.database.update_message(message, STATUS_PROCESSING)

            thread_pool = [
                threading.Thread(target=plugin.execute, args=[
                    plugin.config, plugin.database, message.body, metadata, open(data_path, 'rb')
                ]) for plugin in self.plugins
                if valid_data_type(message, plugin)
            ]

            [t.start() for t in thread_pool]
            [t.join() for t in thread_pool]

            self.database.update_message(message, STATUS_DONE)
            log.info('Processing completed')

        except LookupError as e:
            self.database.update_message(message, STATUS_RETRY, str(e))
            log.warning('Could not fetch data and/or metadata at this point: {}'.format(str(e)))

        except Exception as e:
            try:
                self.database.update_message(message, STATUS_FAILED, str(e))

            except Exception as _:
                log.debug('Could not update message status in database: {}'.format(str(_)))
                pass

            log.error('Could not process message: {}'.format(str(e)))
            log.debug(message)
            log.debug(e)

    def check_mime_type(self, message: dict):
        log.debug('Validating mime type')
        msg_type = message.get('data_type', 'UNKNOWN')
        log.debug('Message Mime type: {}'.format(msg_type))
        log.debug('Accepted Mime types: {}'.format(self.accepted_types))

        if self.accepted_types and msg_type not in self.accepted_types:
            err = 'Mime type {} is not supported by any of the active sqAPI plugins'.format(msg_type)
            log.debug(err)
            raise NotImplementedError(err)

    def query(self, message: Message):
        log.info('Querying metadata and data stores')
        self.database.update_message(message, STATUS_QUERYING)

        data_path = q_data.download_data(self.config, message.body)
        metadata = q_meta.fetch_metadata(self.config, message.body)

        log.debug('Queries completed')
        return data_path, metadata


def valid_data_type(message: Message, plugin):
    accepted_types = plugin.config.msg_broker.get('supported_mime', [])
    data_type = message.body.get('data_type')

    return data_type in accepted_types or not accepted_types
