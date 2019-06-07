#! /usr/bin/env python3

from flask import Blueprint, current_app, send_from_directory
from flask_cors import cross_origin

bp = Blueprint(__name__, __name__, url_prefix='/thumbnails')


@bp.route('/<img_id>', methods=['GET'])
@cross_origin()
def index(img_id):
    thumb_dir = get_config('thumb_dir')

    return send_from_directory(directory=thumb_dir, filename=img_id)


def get_config(key):
    return current_app.config.custom.get('image_plugin', {}).get(key, {})
