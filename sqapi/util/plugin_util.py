#! /usr/bin/env python3
import importlib
import os


def load_blueprints(plugin_name, bp_dir):
    if not bp_dir:
        print('No blueprints directory was defined, no API exposed')
        return []

    # detect_plugins(bp_dir)
    full_path = os.path.join('.'.join(['plugins', plugin_name, bp_dir]))

    bp_dir = verify_directory(full_path.replace('.', os.sep))
    if not bp_dir:
        print('Blueprints directory was not an existing directory, no API exposed')
        return []

    blueprints = [
        importlib.import_module('.'.join([full_path, p.strip('.py')]))
        for p in os.listdir(bp_dir) if not p.startswith('__')
    ]

    return blueprints


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
