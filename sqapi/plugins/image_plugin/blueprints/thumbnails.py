#! /usr/bin/env python3

from flask import Blueprint
from flask_cors import cross_origin

from api import responding as response

bp = Blueprint(__name__, __name__, url_prefix='/thumb')


@bp.route('/', methods=['GET'])
@cross_origin()
def index():
    return response.ok('[Thumbnail-1, Thumbnail-2, Thumbnail-3]')
