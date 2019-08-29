#! /usr/bin/env python
import logging
import sys

import urllib3

import sqapi

log = logging.getLogger(__name__)

if __name__ == '__main__':
    sqapi_type = sys.argv[1] if len(sys.argv) > 1 else None

    try:
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

        sqapi = sqapi.SqapiApplication(sqapi_type)
        sqapi.start()
    except Exception as e:
        log.error('Could not start sqAPI application')
        log.error(str(e))
        exit(1)
