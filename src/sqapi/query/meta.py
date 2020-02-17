#! /usr/bin/env python3
import json
import logging

from sqapi.messaging.message import Message
from sqapi.configuration import detector

log = logging.getLogger(__name__)


def fetch_metadata(config, message: Message):
    loc = message.meta_location
    if not loc:
        err = 'Could not find "meta_location" in message'
        log.warning(err)
        raise AttributeError(err)

    try:
        meta_store = detector.detect_meta_connectors(config.meta_store)
        out = meta_store.fetch_metadata(config, loc)

        return json.loads(out)

    except FileNotFoundError as e:
        err = 'Metadata by reference {} was not available at this moment: {}'.format(loc, str(e))
        log.warning(err)
        raise LookupError(err)
