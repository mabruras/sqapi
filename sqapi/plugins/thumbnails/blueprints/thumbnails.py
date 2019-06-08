#! /usr/bin/env python3

from flask import Blueprint, current_app, send_from_directory
from flask_cors import cross_origin

bp = Blueprint(__name__, __name__, url_prefix='/thumbnails')


@bp.route('/<uuid_ref>', methods=['GET'])
@cross_origin()
def index(uuid_ref):
    # TODO: Validate uuid_ref against thumbnails db to fetch thumb_location
    thumb_dir = get_config().custom.get('thumb_dir', {})

    return send_from_directory(directory=thumb_dir, filename=uuid_ref)


def get_config():
    return current_app.config.get('thumbnails')
