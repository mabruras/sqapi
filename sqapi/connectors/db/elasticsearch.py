#! /usr/bin/env python3
import json

from elasticsearch import Elasticsearch


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
            #            log.debug('Establishing connection towards: {}'.format(cluster))
            es = Elasticsearch(cluster)
            return es
        except ConnectionError as e:
            err = 'Failed to establish connection to the Elasticsearch cluster, please verify the config: {}'
            format(str(e))
            #            log.debug(err)
            raise ConnectionError(err)

    def create_document(self, index: str, type: str, body):
        # Creates a new document(body) of a specified type, with a specific index
        con = self.get_connection()
        con.index(index, body, type)

    def fetch_document(self, index: str, body, query_clause='match'):
        # Uses Elasticsearch Query DSL:
        # https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl.html
        con = self.get_connection()
        con.search(index, body=json.dumps({'query': {query_clause: body}}))
