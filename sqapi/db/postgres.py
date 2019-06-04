#! /usr/bin/env python3
import os
import time

import psycopg2

DB_TYPE = 'postgres'


class Postgres:
    def __init__(self, config):
        self.cfg = config
        self.cfg_con = config.get('connection')
        db_type = config.get('type', 'UNKNOWN')

        if not db_type == DB_TYPE:
            err = 'Attempt to establish connection with a Postgres DB, using "{}" configuration'.format(db_type)
            raise ConnectionError(err)

        while not self.active_connection():
            print('Testing database connection again in 1 second..')
            time.sleep(1)

        print('Initialized and tested connection OK, towards the {} database'.format(db_type))

    def active_connection(self):
        try:
            self.get_connection().close()
            return True
        except Exception as e:
            print('Failed testing database connection: {}'.format(str(e)))
            return False

    def get_connection(self):
        try:
            print('Opening connection for {}'.format(self.cfg_con))
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
            err = 'Failed while opening connection to {}-database, please verify the configuration'.format(
                self.cfg.get('type')
            )
            raise ConnectionError('{}: {}'.format(err, str(e)))

    def initialize_database(self, script: str = None):

        try:
            msg_script_path = self.cfg.get('msg_script_path', './db/pg_script/messages.sql')
            print('Creates messages table if not exists')
            out = self.execute_script(msg_script_path)
            print('Result of creating messages table: {}'.format(out))

            init_script = script if script else self.cfg.get('init_script', './db/pg_script/init.sql')
            print('Executes custom initialization script')
            out = self.execute_script(init_script)
            print('Result of custom database initialization: {}'.format(out))
        except Exception as e:
            err = 'Could not execute database initialization: {}'.format(str(e))
            print(err)
            exit(1)

    def execute_script(self, script_path: str):
        if not script_path:
            err = 'Could not detect any script as argument to method'
            raise ConnectionError(err)

        if not os.path.exists(script_path):
            err = 'Initialization script path "{}" does not exists'.format(script_path)
            raise FileNotFoundError(err)

        try:
            with open(script_path, 'r') as f:
                return self.execute_query(f.read())
        except ConnectionError as e:
            err = 'Could not execute query: {}'.format(str(e))
            raise Exception(err)

    def execute_query(self, query: str, **kwargs):
        """
        Executes query towards the configured database connection

        :param query: Query to be executed
        :param kwargs: Read about how to implement variables in your queries here:
                        http://initd.org/psycopg/docs/usage.html#query-parameters
        :return: Result after execution, using psycopg2's cursor.fetchall()
        """
        try:
            with self.get_connection() as con:
                try:
                    with con.cursor() as cur:
                        cur.execute(query, kwargs)

                        try:
                            return cur.fetchall()
                        except:
                            return None
                except Exception as e:
                    err = 'Could not execute query "{}": {}'.format(query, str(e))
                    raise ConnectionAbortedError(err)
        except ConnectionError as e:
            err = 'Could not connect to local database: {}'.format(str(e))
            raise ConnectionError(err)
