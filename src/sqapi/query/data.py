#! /usr/bin/env python3
import logging

from sqapi.configuration import detector
from sqapi.messaging.message import Message

log = logging.getLogger(__name__)


def download_data(config, message: Message):
    loc = message.data_location
    if not loc:
        err = 'Could not find "data_location" in message'
        log.warning(err)
        raise AttributeError(err)

    try:
        data_store = detector.detect_data_connectors(config.data_store)

        disk_loc = data_store.download_to_disk(config, loc)

        return disk_loc
    except FileNotFoundError as e:
        err = 'Data by reference {} was not available at this moment: {}'.format(loc, str(e))
        log.warning(err)
        raise LookupError(err)


def fetch_file_from_disk(file):
    return open(file, "rb")
