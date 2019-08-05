import copy
import logging
import os

from sqapi.core.processor import Processor
from sqapi.util import detector
from sqapi.util.cfg_util import Config

log = logging.getLogger(__name__)

SINGLE_PLUGIN = os.environ.get('PLUGIN', None)


class PluginManager:
    def __init__(self, config: Config):
        self.config = config

        self.plugins = []
        self.failed_plugins = {}
        self.register_plugins()

        self.accepted_types = set()
        for plugin in self.plugins:
            supported_types = plugin.config.msg_broker.get('supported_mime') or ['*']
            log.debug('Plugin {} accepts data types: {}'.format(plugin.name, supported_types))
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
                self.failed_plugins.update({
                    plugin_name: err
                })

        unloaded_plugins = [
            n for n, _ in detected_plugins
            if n not in self.failed_plugins and n not in [p.name for p in self.plugins]
        ]

        log.info('{}/{} registered plugins'.format(len(self.plugins), len(detected_plugins)))
        log.debug('Registered: {}'.format(self.plugins))

        log.info('{}/{} unloaded plugins'.format(len(unloaded_plugins), len(detected_plugins)))
        log.debug('Unloaded: {}'.format(unloaded_plugins))

        log.info('{}/{} failed plugins'.format(len(self.failed_plugins), len(detected_plugins)))
        log.debug('Failed: {}'.format(self.failed_plugins))

    def active_plugin(self, plugin_name):
        if SINGLE_PLUGIN:
            return SINGLE_PLUGIN == plugin_name

        return not self.config.active_plugins or plugin_name in self.config.active_plugins
