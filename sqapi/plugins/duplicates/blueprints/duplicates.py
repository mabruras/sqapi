#! /usr/bin/env python3
import os

from flask import Blueprint, current_app
from flask_cors import cross_origin

from api import responding

SELECT_DUP_BY_SHA = 'select_dup_by_sha256.sql'
SELECT_DUP_BY_UUID = 'select_dup_by_uuidref.sql'

bp = Blueprint(__name__, __name__, url_prefix='/duplicates')


@bp.route('/sha/<sha_256>', methods=['GET'])
@cross_origin()
def get_duplicates_by_sha(sha_256):
    db = get_database()
    sha_dict = {'sha_256': sha_256}

    script = get_script_path(SELECT_DUP_BY_SHA)
    duplicates = db.execute_script(script, **sha_dict)

    if not duplicates:
        return responding.no_content(duplicates)

    return responding.ok(duplicates)


@bp.route('/uuid/<uuid_ref>', methods=['GET'])
@cross_origin()
def get_sha_for_uuid(uuid_ref):
    db = get_database()
    uuid_dict = {'uuid_ref': uuid_ref}

    script = get_script_path(SELECT_DUP_BY_UUID)
    duplicates = db.execute_script(script, **uuid_dict)

    if not duplicates:
        return responding.no_content(duplicates)

    return responding.ok(duplicates)


def get_script_path(name):
    plugin_dir = get_config().plugin.get('directory')

    return os.path.join(plugin_dir, 'scripts', name)


def get_database():
    return current_app.database.get('duplicates')


def get_config():
    return current_app.config.get('duplicates')
