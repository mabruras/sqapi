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
            if not self.active_plugin(plugin_name):
                print('Plugin "{}" is not listed as active'.format(plugin_name))
                continue
            print('Registering a processor for plugin "{}"'.format(plugin_name))
            processor = Processor(self.config, plugin_name, plugin)
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

        self.register_blueprints()
        self.app.run(host='0.0.0.0')

    def register_blueprints(self):
        self.app.register_blueprint(edge.bp)

        for p in self.processors:
            self.app.config[p.name] = p.config
            self.app.database = dict({p.name: p.database})

            for module in p.blueprints:
                try:
                    print('Registering Blueprint: {}'.format(module.bp.name))
                    self.app.register_blueprint(module.bp)
                except Exception as e:
                    print('Failed when registering blueprint {} for plugin {}: {}'.format(module, p.name, str(e)))

    def active_plugin(self, plugin_name):
        active_plugins = self.config.active_plugins

        return not active_plugins or plugin_name in active_plugins


if __name__ == '__main__':
    sqapi_type = sys.argv[1] if len(sys.argv) > 1 else None

    sqapi = SqapiApplication(sqapi_type)
    sqapi.start()
