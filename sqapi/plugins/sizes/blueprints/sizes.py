#! /usr/bin/env python3
import logging
import os

from flask import Blueprint, current_app
from flask_cors import cross_origin

from sqapi.api import responding

SELECT_ITEMS_LT_SIZE = 'select_items_lt_size.sql'
SELECT_ITEMS_GT_SIZE = 'select_items_gt_size.sql'
SELECT_ITEM_BY_UUID = 'select_item_by_uuid.sql'

log = logging.getLogger(__name__)
bp = Blueprint(__name__, __name__, url_prefix='/sizes')


@bp.route('/lt/<size>', methods=['GET'])
@cross_origin()
def get_items_less_than_size(size):
    db = get_database()
    size_dict = {'data_size': size}

    log.info('Fetching all entries with size less than: {}'.format(size_dict))
    script = get_script_path(SELECT_ITEMS_LT_SIZE)
    items = db.execute_script(script, **size_dict)

    if not items:
        log.info('No entries found with size less than: {}'.format(size))
        return responding.no_content(items)

    log.debug('Entries with size less than: {}, {}'.format(size, items))
    return responding.ok(items)


@bp.route('/gt/<size>', methods=['GET'])
@cross_origin()
def get_items_greater_than_size(size):
    db = get_database()
    size_dict = {'data_size': size}

    log.info('Fetching all entries with size greater than: {}'.format(size_dict))
    script = get_script_path(SELECT_ITEMS_GT_SIZE)
    items = db.execute_script(script, **size_dict)

    if not items:
        log.info('No entries found with size greater than: {}'.format(size))
        return responding.no_content(items)

    log.debug('Entries with size greater than: {}, {}'.format(size, items))
    return responding.ok(items)


@bp.route('/uuid/<uuid_ref>', methods=['GET'])
@cross_origin()
def get_item_with_uuid(uuid_ref):
    db = get_database()
    uuid_dict = {'uuid_ref': uuid_ref}

    log.info('Fetching entry with uuid: {}'.format(uuid_ref))
    script = get_script_path(SELECT_ITEM_BY_UUID)
    entities = db.execute_script(script, **uuid_dict)

    if not entities:
        log.info('No entries found with uuid: {}'.format(uuid_ref))
        return responding.no_content(entities)

    log.debug('Entity found: {}'.format(entities))
    return responding.ok(entities)


def get_script_path(name):
    plugin_dir = get_config().plugin.get('directory')

    return os.path.join(plugin_dir, 'scripts', name)


def get_database():
    return current_app.database.get('sizes')


def get_config():
    return current_app.config.get('sizes')
