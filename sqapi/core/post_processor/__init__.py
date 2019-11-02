import logging

from sqapi.core.message import Message
from sqapi.util import detector

log = logging.getLogger(__name__)


class PostProcessor:
    def __init__(self, config):
        self.executor = detector.detect_post_processor(config.get('post_processing'))

    def post_plugin(self, messsage: Message, plugin, success):
        try:
            self.executor.plugin(messsage, plugin, success)
        except Exception as e:
            log.warning('Could not execute post plugin: {}'.format(str(e)))

    def post_execution(self, message: Message, success):
        try:
            self.executor.execution(message, success)
        except Exception as e:
            log.warning('Could not execute post execution: {}'.format(str(e)))
