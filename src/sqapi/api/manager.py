import logging
import time

from flask import Flask
from flask_cors import CORS

from sqapi.api import edge
from sqapi.configuration.util import Config
from sqapi.plugin.manager import PluginManager

log = logging.getLogger(__name__)


class ResourceManager:
    def __init__(self, config: Config, plugin_manager: PluginManager):
        self.config = config
        self.app = Flask(__name__)
        self.app.start_time = time.time()
        self.plugin_manager = plugin_manager

    def start_api(self):
        CORS(self.app)
        self.app.url_map.strict_slashes = False
        self.app.config['CORS_HEADERS'] = 'Content-Type,Authorization,X-Requested-With,Content-Length,Accept,Origin'

        self.register_blueprints()
        self.app.run(host='0.0.0.0')

    def register_blueprints(self):
        log.info('Registering blueprints for {} plugins'.format(len(self.plugin_manager.plugins)))
        self.app.register_blueprint(edge.bp)

        self.app.plugins = []
        self.app.database = dict()
        for p in self.plugin_manager.plugins:
            log.debug('Registering {} blueprints for plugin {}'.format(len(p.blueprints), p.name))
            log.debug('Processor configuration: {}'.format(p.config))

            self.app.config[p.name] = p.config
            self.app.database.update(({p.name: p.database}))
            self.append_plugin_blueprints(p)
            self.register_plugin_blueprints(p)
            log.debug('Processor information: {}'.format(p.__dict__))

        self.app.plugins.extend([{
            'name': p.get('name'),
            'status': 'failed',
            'error': p.get('error')
        } for p in self.plugin_manager.failed_plugins])

        self.app.plugins.extend([{
            'name': p.get('name'),
            'status': 'unloaded'
        } for p in self.plugin_manager.unloaded_plugins])

    def append_plugin_blueprints(self, p):
        self.app.plugins.append({
            'name': p.name,
            'status': 'active',
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
