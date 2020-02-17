import json
import logging
import uuid
from datetime import date

from flask import Response

log = logging.getLogger(__name__)


def ok(data):
    return _create_response(data, 200)


def no_content(data):
    log.debug(data)
    data = {'error': 'Could not find any content', 'details': data}

    return _create_response(data, 204)


def invalid_request(err):
    log.warning(err)
    data = {
        'error': 'The request was not complete',
        'reference': str(uuid.uuid4()),
        'details': err,
    }
    log.warning(data)

    return _create_response(data, 400)


def server_failure(err):
    log.warning(err)
    data = {
        'error': 'Something went wrong, we\'ve logged the issue, and will look into it',
        'reference': str(uuid.uuid4()),
        'details': err,
    }
    log.warning(data)

    return _create_response(data, 500)


def not_impl(err):
    log.warning(err)
    data = {'error': 'Not implemented', 'details': err}

    return _create_response(data, 501)


def _create_response(data, code):
    log.debug(f'Final response status code: {code}')
    log.debug(f'Final response content: {content}')
    return Response(
        response=json.dumps(data, cls=DateEncoder),
        mimetype='application/json',
        status=code,
    )


class DateEncoder(json.JSONEncoder):

    def default(self, obj):
        if isinstance(obj, date):
            return str(obj)
        return json.JSONEncoder.default(self, obj)
