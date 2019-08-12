#! /usr/bin/env python3
import json
import logging

from elasticsearch import Elasticsearch

log = logging.getLogger(__name__)


class Database:
    def __init__(self, config: dict):
        self.cfg = config
        self.cfg_con_list = config.get('connection') or []

    def get_connection(self):
        try:
            cluster = [{
                'host': c.get('host', 'localhost'),
                'port': c.get('port', '9200')
            } for c in self.cfg_con_list or []]
            log.debug('Establishing connection towards: {}'.format(cluster))
            es = Elasticsearch(cluster)
            return es
        except ConnectionError as e:
            err = 'Failed to establish connection to the Elasticsearch cluster, please verify the config: {}'
            format(str(e))
            log.debug(err)
            raise ConnectionError(err)

    def create_document(self, area: str, body, kind: str = '_doc'):
        # Creates a new document(body) of a specified type(optional),
        # within a specific area (index/collection/etc)
        con = self.get_connection()
        con.index(area, body, kind)

    def fetch_document(self, area: str, body, query_clause='match'):
        # Uses Elasticsearch Query DSL:
        # https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl.html
        con = self.get_connection()
        res = con.search(area, body=json.dumps({'query': {query_clause: body}}))

        return res.get('hits', {}).get('hits', [])

    def initialize_database(self):
        pass
