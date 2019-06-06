#! /usr/bin/env python3
import importlib
import os


def load_blueprints(bp_dir):
    if not bp_dir:
        print('No blueprints directory was defined, no API exposed')
        return []

    bp_dir = verify_directory(bp_dir)
    if not bp_dir:
        print('Blueprints directory was not an existing directory, no API exposed')
        return []

    # detect_plugins(bp_dir)
    plugin = importlib.import_module(plugin_name, __package__)
    to_imp = {plugin_name.__name__.split('.')[2]: plugin}

    return [script_dir]


def verify_directory(directory):
    # Verify if canonical path
    if os.path.exists(directory) and os.path.isdir(directory):
        return directory

    # Verify if relative path
    script_dir = os.path.dirname(__file__)
    concat_path = os.path.join(script_dir, directory)
    if os.path.exists(concat_path) and os.path.isdir(directory):
        return concat_path

    return None
