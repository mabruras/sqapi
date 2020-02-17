import logging.config
import os

from sqapi.api.manager import ResourceManager
from sqapi.configuration.util import Config
from sqapi.plugin.manager import PluginManager
from sqapi.processing.manager import ProcessManager

PROJECT_DIR = os.environ.get('WRK_DIR', '.')
RESOURCE_DIR = '{pd}{sep}sqapi{sep}resources'.format(pd=PROJECT_DIR, sep=os.sep)
CONFIG_FILE = os.environ.get('CFG_FILE', '{}{}sqapi.yml'.format(RESOURCE_DIR, os.sep))
LOG_FILE = os.environ.get('LOG_FILE', '{}{}logging.conf'.format(RESOURCE_DIR, os.sep))

try:
    logging.config.fileConfig(LOG_FILE)
except KeyError:
    logging.basicConfig()

log = logging.getLogger(__name__)


class SqapiApplication:

    def __init__(self, sqapi_type=None):
        log.info('Initializing application')
        self.sqapi_type = sqapi_type  # Loader / API
        self.config = Config(CONFIG_FILE)

        self.plugin_manager = PluginManager(self.config)
        self.process_manager = ProcessManager(self.config, self.plugin_manager)
        self.resource_manager = ResourceManager(self.config, self.plugin_manager)

    def start(self):
        if not self.sqapi_type or self.sqapi_type == 'loader':
            self.process_manager.start_subscribing()

        if not self.sqapi_type or self.sqapi_type == 'api':
            self.resource_manager.start_api()
