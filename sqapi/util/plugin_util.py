#! /usr/bin/env python3
import importlib
import logging
import os

from sqapi.util import detector

log = logging.getLogger(__name__)


def load_blueprints(plugin_name, bp_dir):
    log.debug('Loading blueprints from {}, for plugin {}'.format(bp_dir, plugin_name))

    if not bp_dir:
        log.warning('No blueprints directory was defined, no API exposed')
        return []

    full_path = os.path.join('.'.join(['sqapi', 'plugins', plugin_name, bp_dir]))

    if not _verify_directory(full_path.replace('.', os.sep)):
        log.warning('Blueprints directory was not an existing directory, no API exposed')
        return []

    plugin_dict = detector.detect_modules(full_path)
    return [
        importlib.import_module(plugin_dict.get(blueprints))
        for blueprints in plugin_dict
    ]


def _verify_directory(directory):
    log.debug('Verifying directory: {}'.format(directory))

    # Verify if canonical path
    if os.path.exists(directory) and os.path.isdir(directory):
        log.debug('Directory exists')
        return directory

    # Verify if relative path
    log.debug('Could not verify directory, verifying if relative to current')
    script_dir = os.path.dirname(__file__)
    concat_path = os.path.join(script_dir, directory)

    if os.path.exists(concat_path) and os.path.isdir(directory):
        log.debug('Relative path exists and is a directory')
        return concat_path

    log.warning('Could not verify existence of directory {}'.format(directory))
    return None
