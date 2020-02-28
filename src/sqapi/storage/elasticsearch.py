#! /usr/bin/env python3
import json
import logging

from elasticsearch import Elasticsearch, Transport

log = logging.getLogger(__name__)


class Database:
    def __init__(self, config: dict):
        self.cfg = config

        cluster = [{**c} for c in config.get('connection') or []]
        log.debug('Establishing connection towards: {}'.format(cluster))

        try:
            self.es = Elasticsearch(
                cluster,
                Transport,
                **(config.get('kwargs') or {})
            )
            self.es.ping()
        except ConnectionError as e:
            err = 'Failed to establish connection to the Elasticsearch cluster, please verify the config: {}'
            format(str(e))
            log.debug(err)
            raise ConnectionError(err)

    def get_connection(self):
        try:
            self.es.ping()

            return self.es
        except ConnectionError as e:
            err = 'Could not ping the ElasticSearch cluster, please try again later'
            format(str(e))
            log.debug(err)
            raise ConnectionError(err)

    def create_document(self, area: str, body: dict, kind: str = '_doc'):
        # Creates a new document(body) of a specified type(optional),
        # within a specific area (index/collection/etc)
        con = self.get_connection()
        con.index(area, body, kind)

    def fetch_document(self, area: str, body: dict, query_clause='match', **kwargs):
        # Uses Elasticsearch Query DSL:
        # https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl.html
        con = self.get_connection()

        offset = kwargs.get('start', 0)
        size = kwargs.get('size', 10)
        search_body = json.dumps({'from': offset, 'size': size, 'query': {query_clause: body}})

        res = con.search(area, body=search_body)

        return res.get('hits', {})

    def initialize_database(self):
        pass
