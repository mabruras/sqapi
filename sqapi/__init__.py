import logging.config
import os
import threading

from flask import Flask
from flask_cors import CORS

from sqapi.api import edge
from sqapi.core.process_manager import ProcessManager
from sqapi.core.processor import Processor
from sqapi.util import detector
from sqapi.util.cfg_util import Config

PROJECT_DIR = os.environ.get('WRK_DIR', '.')
CONFIG_DIR = '{pd}{sep}sqapi{sep}conf'.format(pd=PROJECT_DIR, sep=os.sep)
CONFIG_FILE = os.environ.get('CFG_FILE', '{}{}sqapi.yml'.format(CONFIG_DIR, os.sep))
LOG_FILE = os.environ.get('LOG_FILE', '{}{}logging.conf'.format(CONFIG_DIR, os.sep))

logging.config.fileConfig(LOG_FILE)
log = logging.getLogger(__name__)


class SqapiApplication:

    def __init__(self, sqapi_type=None):
        log.info('Initializing application')
        self.sqapi_type = sqapi_type  # Loader / API
        self.config = Config(CONFIG_FILE)

        # TODO: Extract Flask server and API setup to wrapper module
        self.app = Flask(__name__)
        self.pm = ProcessManager(self.config)

    def start(self):
        if not self.sqapi_type or self.sqapi_type == 'loader':
            self.pm.start_subscribing()

        if not self.sqapi_type or self.sqapi_type == 'api':
            self.start_api()

    def start_api(self):
        CORS(self.app)
        self.app.url_map.strict_slashes = False
        self.app.config['CORS_HEADERS'] = 'Content-Type,Authorization,X-Requested-With,Content-Length,Accept,Origin'

        self.register_blueprints()
        self.app.run(host='0.0.0.0')

    def register_blueprints(self):
        log.info('Registering blueprints for {} plugins'.format(len(self.plugins)))
        self.app.register_blueprint(edge.bp)

        self.app.plugins = []
        self.app.database = dict()
        for p in self.plugins:
            log.debug('Registering {} blueprints for plugin {}'.format(len(p.blueprints), p.name))
            log.debug('Processor configuration: {}'.format(p.config))
            log.debug('Processor database: {}'.format(p.database))

            self.app.config[p.name] = p.config
            self.app.database.update(({p.name: p.database}))
            self.append_plugin_blueprints(p)
            self.register_plugin_blueprints(p)
            log.debug('Processor information: {}'.format(p.__dict__))

    def append_plugin_blueprints(self, p):
        self.app.plugins.append({
            'name': p.name,
            'blueprints': [{
                'package': module.bp.name,
                'url_prefix': module.bp.url_prefix,
                'url_values_defaults': module.bp.url_values_defaults
            } for module in p.blueprints
            ],
        })

    def register_plugin_blueprints(self, p):
        for module in p.blueprints:
            try:
                log.debug('Registering blueprint {} for plugin {}'.format(module.bp.name, p.name))
                self.app.register_blueprint(module.bp)
            except Exception as e:
                log.warning('Failed when registering blueprint {} for plugin {}: {}'.format(module, p.name, str(e)))
