#!/usr/bin/env python
import logging
import sys

import pip

log = logging.getLogger(__name__)


def install_packages(packages):
    for pkg in packages.get('pip', []):
        log.debug('Installing PIP package "{}"'.format(pkg))
        install_pip_package(pkg)


def install_pip_package(pkg_name):
    try:
        if hasattr(pip, 'main'):
            pip.main(['install', pkg_name])
        else:
            import subprocess
            subprocess.call([sys.executable, '-m', 'pip', 'install', pkg_name])
    except Exception as e:
        err = 'PIP package installation failed: {}'.format(str(e))
        log.warning(err)
        raise e
