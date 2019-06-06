#! /usr/bin/env python
import os
import sys

from flask import Flask
from flask_cors import CORS

from api import edge
from core.processor import Processor
from util import detector
from util.cfg_util import Config

PROJECT_DIR = os.environ.get('WRK_DIR', '.')
CONFIG_DIR = '{}{}conf'.format(PROJECT_DIR, os.sep)
CONFIG_FILE = os.environ.get('CFG_FILE', '{}{}sqapi.yml'.format(CONFIG_DIR, os.sep))


class SqapiApplication:

    def __init__(self, sqapi_type=None):
        self.sqapi_type = sqapi_type  # Loader / API

        self.app = Flask(__name__)
        self.config = Config(CONFIG_FILE)

        self.processors = []
        for plugin_name, plugin in detector.detect_plugins('plugins').items():
            processor = Processor(self.config, plugin_name, plugin)
            # TODO: prepare processor
            self.processors.append(processor)

    def start(self):
        for p in self.processors:
            if sqapi_type == 'loader':
                p.start_loader()
            elif sqapi_type == 'api':
                self.start_api()
            else:
                p.start_loader()
                self.start_api()

    def start_api(self):
        CORS(self.app)
        self.app.url_map.strict_slashes = False
        self.app.config['CORS_HEADERS'] = 'Content-Type,Authorization,X-Requested-With,Content-Length,Accept,Origin'
        # TODO: how to refer to DB in blueprint..?
        # app.config['database'] = database
        self.app.config['cfg'] = self.config

        self.register_blueprints()
        self.app.run(host='0.0.0.0')

    def register_blueprints(self):
        self.app.register_blueprint(edge.bp)

        for p in self.processors:
            for bp in p.blueprints:
                self.app.register_blueprint(bp)


if __name__ == '__main__':
    sqapi_type = sys.argv[1] if len(sys.argv) > 1 else None

    sqapi = SqapiApplication(sqapi_type)
    sqapi.start()
