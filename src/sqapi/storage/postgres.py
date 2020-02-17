#! /usr/bin/env python3
import logging
import os
import time

import psycopg2
import psycopg2.extras

DB_TYPE = 'postgres'

log = logging.getLogger(__name__)


class Database:

    def __init__(self, config: dict):
        self.cfg = config
        self.cfg_con = config.get('connection')
        self.init_script = config.get('init', None)
        db_type = config.get('type', 'UNKNOWN')

        if not db_type == DB_TYPE:
            err = 'Attempt to establish connection with a Postgres DB, using {} configuration'.format(db_type)
            log.warning(err)
            raise ConnectionError(err)

        log.info('Testing database connection')
        while not self.active_connection():
            log.debug('Testing database connection again in 1 second..')
            time.sleep(1)

        log.debug('Initialized and tested connection OK, towards the {} database'.format(db_type))

    def active_connection(self):
        try:
            log.debug('Trying to open connection')
            self._create_connection().close()
            return True

        except Exception as e:
            log.debug('Failed to open database connection: {}'.format(str(e)))
            return False

    def _create_connection(self):
        try:
            log.debug('Establishing connection towards {}:{}'.format(
                self.cfg_con.get('host', 'localhost'),
                self.cfg_con.get('port', '5432')
            ))
            connection = psycopg2.connect(
                dbname=self.cfg_con.get('name', 'postgres'),
                port=self.cfg_con.get('port', '5432'),
                user=self.cfg_con.get('user', 'postgres'),
                host=self.cfg_con.get('host', 'localhost'),
                password=self.cfg_con.get('password', 'postgres'),
                connect_timeout=self.cfg_con.get('timeout', 5)
            )
            connection.autocommit = True

            return connection

        except ConnectionError as e:
            err = 'Failed to establish connection towards the database, please verify the configuration: {}'.format(
                str(e)
            )
            log.debug(err)
            raise ConnectionError(err)

    def initialize_database(self):
        log.info('Initializing Postgres database')
        try:
            log.debug('Executes custom initialization script {}'.format(self.init_script))
            out = self.execute_script(self.init_script)
            log.debug('Result of custom database initialization: {}'.format(out))

        except Exception as e:
            err = 'Could not initialize database: {}'.format(str(e))
            log.warning(err)
            raise type(e)(err)

    def execute_script(self, script_path: str, **kwargs):
        log.debug('Preparing script {}'.format(script_path))

        if not script_path:
            err = 'Could not detect any script as argument to method'
            log.warning(err)
            raise ConnectionError(err)

        if not os.path.exists(script_path):
            err = 'Script path "{}" does not exists'.format(script_path)
            log.warning(err)
            raise FileNotFoundError(err)

        try:
            log.debug('Opening script file')
            with open(script_path, 'r') as f:
                return self.execute_query(f.read(), **kwargs)

        except ConnectionError as e:
            err = 'Could not execute query: {}'.format(str(e))
            log.warning(err)
            raise Exception(err)

    def execute_query(self, query: str, **kwargs):
        """
        Executes query towards the configured database connection

        :param query: Query to be executed
        :param kwargs: Read about how to implement variables in your queries here:
                        http://initd.org/psycopg/docs/usage.html#query-parameters
        :return: Result after execution, using psycopg2's cursor.fetchall()
        """
        log.debug('Preparing query')
        log.debug(query)
        try:
            log.debug('Establishing database connection for query execution')
            with self._create_connection() as con:
                try:
                    log.debug('Executing query')
                    with con.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                        cur.execute(query, kwargs)

                        try:
                            log.debug('Query executed')
                            return [dict(r) for r in cur.fetchall()]
                        except Exception as e:
                            log.debug('No result after query: {}'.format(str(e)))
                            return None

                except Exception as e:
                    err = 'Could not execute query {}: {}'.format(query, str(e))
                    log.warning(err)
                    raise ConnectionError(err)

        except ConnectionAbortedError as e:
            err = 'Could not connect to local database: {}'.format(str(e))
            log.warning(err)
            raise ConnectionError(err)
