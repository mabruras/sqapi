import json

from flask import Response


def ok(data):
    return _create_response(data, 200)


def no_content(data):
    print(data)
    data = {'error': 'Could not find any data', 'details': data}

    return _create_response(data, 204)


def invalid_request(err):
    print(err)
    data = {'error': 'The request was not complete', 'details': err}

    return _create_response(data, 400)


def server_failure(err):
    print(err)
    data = {'error': 'Something went wrong, we\'ve logged the issue, and will look into it', 'details': err}

    return _create_response(data, 500)


def not_impl(err):
    print(err)
    data = {'error': 'Not implemented', 'details': err}

    return _create_response(data, 501)


def _create_response(data, code):
    print(f'Final response status code: {code}')
    print(f'Final response data: {data}')
    return Response(
        response=json.dumps(data),
        mimetype='application/json',
        status=code,
    )
