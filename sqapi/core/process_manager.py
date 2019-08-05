import copy
import json
import logging
import multiprocessing

from sqapi.core.message import Message
from sqapi.core.plugin_manager import PluginManager
from sqapi.query import data as q_data, metadata as q_meta
from sqapi.util import detector
from sqapi.util.cfg_util import Config

STATUS_VALIDATING = 'VALIDATING'
STATUS_QUERYING = 'QUERYING'
STATUS_PROCESSING = 'PROCESSING'
STATUS_DONE = 'DONE'
STATUS_RETRY = 'RETRY'
STATUS_FAILED = 'FAILED'

log = logging.getLogger(__name__)


class ProcessManager:
    def __init__(self, config: Config, plugin_manager: PluginManager):
        self.config = config
        self.plugin_manager = plugin_manager

        self.database = detector.detect_database(self.config.database)
        self.database.initialize_message_table()

        self.listener = detector.detect_listener(self.config.msg_broker, self.process_message)

    def start_subscribing(self):
        log.info('Starting message subscription')
        self.listener.start_listeners()
        log.debug('Message subscription started')

    def process_message(self, message: Message):
        log.info('Message processing started')
        self.check_mime_type(message)

        try:
            # Query
            data_path, metadata = self.query(message)
            self.database.update_message(message, STATUS_PROCESSING)

            log.debug('Creating processor pool of plugin executions')
            process_pool = [
                multiprocessing.Process(target=plugin.execute, args=[
                    plugin.config, plugin.database, copy.deepcopy(message),
                    copy.deepcopy(metadata), open(data_path, 'rb')
                ]) for plugin in self.plugin_manager.plugins
                if valid_data_type(message, plugin)
            ]

            log.debug('Starting processor pool')
            [t.start() for t in process_pool]
            [t.join() for t in process_pool]

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

    def check_mime_type(self, message: Message):
        log.debug('Validating data type')
        log.debug('Message data type: {}'.format(message.type))
        log.debug('Accepted data types: {}'.format(self.plugin_manager.accepted_types))

        if self.plugin_manager.accepted_types and (
                message.type not in self.plugin_manager.accepted_types
                and '*' not in self.plugin_manager.accepted_types
        ):
            err = 'Data type "{}" is not supported by any of the active sqAPI plugins'.format(message.type)
            log.debug(err)
            raise NotImplementedError(err)

    def query(self, message: Message):
        log.info('Querying metadata and data stores')
        self.database.update_message(message, STATUS_QUERYING)

        data_path = q_data.download_data(self.config, message)

        if message.metadata:
            log.debug('Loading metadata from message')
            metadata = json.loads(message.metadata)
        else:
            log.debug('Fetching metadata by query')
            metadata = q_meta.fetch_metadata(self.config, message)

        log.debug('Queries completed')
        return data_path, metadata


def valid_data_type(message: Message, plugin):
    accepted_types = plugin.config.msg_broker.get('supported_mime') or []

    return message.type in accepted_types or not accepted_types
