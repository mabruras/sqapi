#! /usr/bin/env python3
import logging
import os
import tempfile

log = logging.getLogger(__name__)


def download_to_disk(config, object_ref):
    log.debug('Moving file from {} to temporary file'.format(object_ref))

    fd, path = tempfile.mkstemp(os.path.splitext(object_ref)[-1])
    os.write(fd, open(object_ref, 'rb').read())
    os.close(fd)

    return path
