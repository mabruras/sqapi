#! /usr/bin/env python3
import logging
import os

import markdown
from flask import Blueprint, current_app, url_for, send_from_directory
from flask_cors import cross_origin

from sqapi.api import responding as response

log = logging.getLogger(__name__)
bp = Blueprint(__name__, __name__, url_prefix='/')


@bp.route('/', methods=['GET'], defaults={'path': ''})
@bp.route('/<path:path>')
def index(path):
    try:
        log.debug('Path: {}'.format(path))
        if not path or path == '/':
            return render_markdown('README.md')

        if 'docs' in path and path.endswith('.md'):
            return render_markdown(path)

        return send_from_directory(os.path.join('..', os.path.dirname(path)), path.split(os.sep)[-1])
    except Exception as e:
        err = 'Could not open readme: {}'.format(str(e))
        log.warning(err)

        return response.server_failure(err)


@bp.route('/plugins', methods=['GET'])
@cross_origin()
def plugins():
    plugin_list = get_active_plugins()

    for p in plugin_list:
        for blueprint in p.get('blueprints'):
            blueprint['endpoints'] = [
                r for r in get_rules()
                if r.get('endpoint').startswith(blueprint.get('url_prefix'))
            ]

    return response.ok(plugin_list)


@bp.route("/rules")
def rules():
    out = get_rules()

    return response.ok(out)


def render_markdown(doc_file):
    with open(doc_file, 'r') as f:
        return markdown.markdown(
            f.read(), extensions=['codehilite', 'fenced_code', 'tables']
        )


def get_rules():
    out = []

    for rule in current_app.url_map.iter_rules():
        options = {}
        for arg in rule.arguments:
            options[arg] = "<{}>".format(arg)
        out.append(dict({
            'function': rule.endpoint,
            'endpoint': url_for(rule.endpoint, **options),
            'arguments': list(rule.arguments),
            'methods': list(rule.methods),
        }))

    return out


def get_database():
    return current_app.database.get('duplicates')


def get_config():
    return current_app.config.get('duplicates')


def get_active_plugins():
    return [plugin for plugin in current_app.plugins]
