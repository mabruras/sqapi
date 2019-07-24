import logging
import multiprocessing
import threading

from sqapi.core.plugin_manager import PluginManager
from sqapi.core.message import Message
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

        # Setup sqAPI general exchange listener
        log.debug('Starting Exchange Listener')
        threading.Thread(
            name='ExchangeListener',
            target=self.listener.listen_exchange
        ).start()

        # Setup sqAPI unique queue listener
        log.debug('Starting Queue Listener')
        threading.Thread(
            name='QueueListener',
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

            process_pool = [
                multiprocessing.Process(target=plugin.execute, args=[
                    plugin.config, plugin.database, message.body, metadata, open(data_path, 'rb')
                ]) for plugin in self.plugin_manager.plugins
                if valid_data_type(message, plugin)
            ]

            log.debug('Starting pool')
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

    def check_mime_type(self, message: dict):
        log.debug('Validating mime type')
        msg_type = message.get('data_type', 'UNKNOWN')
        log.debug('Message Mime type: {}'.format(msg_type))
        log.debug('Accepted Mime types: {}'.format(self.plugin_manager.accepted_types))

        if self.plugin_manager.accepted_types and (
                msg_type not in self.plugin_manager.accepted_types
                and '*' not in self.plugin_manager.accepted_types
        ):
            err = 'Mime type {} is not supported by any of the active sqAPI plugins'.format(msg_type)
            log.debug(err)
            raise NotImplementedError(err)

    def query(self, message: Message):
        log.info('Querying metadata and data stores')
        self.database.update_message(message, STATUS_QUERYING)

        data_path = q_data.download_data(self.config, message)
        metadata = q_meta.fetch_metadata(self.config, message)

        log.debug('Queries completed')
        return data_path, metadata


def valid_data_type(message: Message, plugin):
    accepted_types = plugin.config.msg_broker.get('supported_mime') or []
    data_type = message.body.get('data_type')

    return data_type in accepted_types or not accepted_types
