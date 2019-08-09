#! /usr/bin/env python3
import logging

from elasticsearch import Elasticsearch

from sqapi.core.message import Message

log = logging.getLogger(__name__)


class Database:

    def __init__(self, config: dict):
        self.cfg = config
        self.cfg_con = config.get('connection')

    def get_connection(self):
        try:
            cluster = [{
                'host': c.get('host', 'localhost'),
                'port': c.get('port', '9200')
            } for c in self.cfg_con.get('connection')]
            log.debug('Establishing connection towards: {}'.format(cluster))

            es = Elasticsearch(cluster)

            return es

        except ConnectionError as e:
            err = 'Failed to establish connection to the Elasticsearch cluster, please verify the config: {}'
            format(str(e))
            log.debug(err)
            raise ConnectionError(err)

    def initialize_database(self):
        pass

    def execute_script(self, script_path: str, **kwargs):
        pass

    def execute_query(self, query: str, **kwargs):
        pass

    def update_message(self, message: Message, status: str, info: str = None):
        pass
