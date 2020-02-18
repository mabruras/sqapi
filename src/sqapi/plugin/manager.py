import copy
import logging
import os

from sqapi.configuration import detector
from sqapi.configuration.util import Config
from sqapi.processing.processor import Processor

log = logging.getLogger(__name__)

SINGLE_PLUGIN = os.environ.get('PLUGIN', None)


class PluginManager:
    def __init__(self, config: Config):
        self.config = config

        self.plugins = []
        self.failed_plugins = []
        self.unloaded_plugins = []
        self.register_plugins()

        self.accepted_types = set()
        for plugin in self.plugins:
            supported_types = plugin.config.msg_broker.get('supported_mime') or ['*']
            log.debug('Plugin {} accepts mime types: {}'.format(plugin.name, supported_types))
            self.accepted_types.update(supported_types)

    def register_plugins(self):
        log.debug('Searching for available and active plugins')
        detected_plugins = detector.detect_plugins().items()
        for plugin_name, plugin in detected_plugins:
            if not self.active_plugin(plugin_name):
                log.debug('Plugin {} is not listed as active'.format(plugin_name))
                continue

            try:
                log.debug('Registering a processor for plugin {}'.format(plugin_name))
                processor = Processor(copy.deepcopy(self.config), plugin_name, plugin)
                self.plugins.append(processor)

            except Exception as e:
                err = 'Could not register plugin {} ({}): {}'.format(plugin_name, plugin, str(e))
                log.warning(err)
                self.failed_plugins.append({
                    'name': plugin_name,
                    'error': err
                })

        self.unloaded_plugins = [
            {'name': name} for name, _ in detected_plugins
            if name not in [
                p.get('name') for p in self.failed_plugins
            ] and name not in [
                p.name for p in self.plugins
            ]
        ]

        log.info('{}/{} registered plugins'.format(len(self.plugins), len(detected_plugins)))
        log.debug('Registered: {}'.format(self.plugins))

        log.info('{}/{} unloaded plugins'.format(len(self.unloaded_plugins), len(detected_plugins)))
        log.debug('Unloaded: {}'.format(self.unloaded_plugins))

        log.info('{}/{} failed plugins'.format(len(self.failed_plugins), len(detected_plugins)))
        log.debug('Failed: {}'.format(self.failed_plugins))

    def active_plugin(self, plugin_name):
        if SINGLE_PLUGIN:
            return SINGLE_PLUGIN == plugin_name

        return not self.config.active_plugins or plugin_name in self.config.active_plugins
