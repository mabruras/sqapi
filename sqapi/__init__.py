import logging.config
import os

from flask import Flask
from flask_cors import CORS

from sqapi.api import edge
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

        self.app = Flask(__name__)
        self.config = Config(CONFIG_FILE)

        self.processors = []
        log.info('Searching for available and active plugins')
        for plugin_name, plugin in detector.detect_plugins().items():
            if not self.active_plugin(plugin_name):
                log.debug('Plugin {} is not listed as active'.format(plugin_name))
                continue
            log.debug('Registering a processor for plugin {}'.format(plugin_name))
            processor = Processor(self.config, plugin_name, plugin)
            self.processors.append(processor)

        log.info('{} plugin processors created'.format(len(self.processors)))
        log.info('Initialization done')

    def start(self):
        for p in self.processors:
            log.debug('Starting processor for plugin {}'.format(p.name))
            if self.sqapi_type == 'loader':
                p.start_loader()
            elif self.sqapi_type == 'api':
                self.start_api()
            else:
                p.start_loader()
                self.start_api()
            log.info('Processor started for plugin {}'.format(p.name))

    def start_api(self):
        CORS(self.app)
        self.app.url_map.strict_slashes = False
        self.app.config['CORS_HEADERS'] = 'Content-Type,Authorization,X-Requested-With,Content-Length,Accept,Origin'

        self.register_blueprints()
        self.app.run(host='0.0.0.0')

    def register_blueprints(self):
        log.info('Registering blueprints for {} plugins'.format(len(self.processors)))
        self.app.register_blueprint(edge.bp)

        for p in self.processors:
            log.debug('Registering {} blueprints for plugin {}'.format(len(p.blueprints), p.name))
            self.app.config[p.name] = p.config
            self.app.database = dict({p.name: p.database})

            for module in p.blueprints:
                try:
                    log.debug('Registering blueprint {} for plugin {}'.format(module.bp.name, p.name))
                    self.app.register_blueprint(module.bp)
                except Exception as e:
                    log.warning('Failed when registering blueprint {} for plugin {}: {}'.format(module, p.name, str(e)))

    def active_plugin(self, plugin_name):
        active_plugins = self.config.active_plugins

        return not active_plugins or plugin_name in active_plugins