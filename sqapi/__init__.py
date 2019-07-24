import logging.config
import os

from sqapi.core.plugin_manager import PluginManager
from sqapi.core.process_manager import ProcessManager
from sqapi.core.resource_manager import ResourceManager
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

        self.plugin_manager = PluginManager(self.config)
        self.process_manager = ProcessManager(self.config, self.plugin_manager)
        self.resource_manager = ResourceManager(self.config, self.plugin_manager)

    def start(self):
        if not self.sqapi_type or self.sqapi_type == 'loader':
            self.process_manager.start_subscribing()

        if not self.sqapi_type or self.sqapi_type == 'api':
            self.resource_manager.start_api()
