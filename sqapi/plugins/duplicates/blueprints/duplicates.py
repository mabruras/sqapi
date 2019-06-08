#! /usr/bin/env python3

from flask import Blueprint, current_app, send_from_directory
from flask_cors import cross_origin

from api import responding

bp = Blueprint(__name__, __name__, url_prefix='/duplicates')


@bp.route('/sha/<sha_256>', methods=['GET'])
@cross_origin()
def index(sha_256):
    db = get_database()
    sha_dict = {'sha_256': sha_256}
    duplicates = db.execute_script('scripts/select_dup_by_sha256.sql', **sha_dict)

    if not duplicates:
        return responding.no_content(duplicates)

    return responding.ok(duplicates)


@bp.route('/uuid/<uuid_ref>', methods=['GET'])
@cross_origin()
def index(uuid_ref):
    db = get_database()
    uuid_dict = {'uuid_ref': uuid_ref}
    duplicates = db.execute_script('scripts/select_dup_by_uuidref.sql', **uuid_dict)

    if not duplicates:
        return responding.no_content(duplicates)

    return responding.ok(duplicates)


def get_database():
    return current_app.database.get('duplicates')
