#!/usr/bin/env python
import logging
import sys

import pip

log = logging.getLogger(__name__)


def install_packages(config):
    log.debug('Config: {}'.format(config))
    for module in config.keys() or {}:
        pm = config.get(module) or {}
        if type(pm) is dict:
            log.debug('(module: {}), pm ({}) type: {}'.format(module, pm, type(pm)))
            for action in pm.keys() or {}:
                log.debug('action config type: {}'.format(type(pm.get(action))))
                for package in pm.get(action):
                    log.debug('Module: "{}", Action: "{}", Package: "{}"'.format(module, action, package))
                    execute_module_action(module, action, package)


def execute_module_action(module, action, package):
    try:
        if (module == 'pip3' or module == 'pip') and hasattr(pip, 'main'):
            pip.main([action, package])
        else:
            import subprocess
            subprocess.call([sys.executable, '-m', module, action, package])
    except Exception as e:
        err = '{} action ({}) for package ({}) failed: {}'.format(module, action, package, str(e))
        log.warning(err)
        raise e
