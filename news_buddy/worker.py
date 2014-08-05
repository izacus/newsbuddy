#!/usr/bin/env python
"""
This is a RQ worker used for async task processing
"""

import sys
import settings
from rq import Connection, Queue, Worker


if settings.SENTRY_CONNECTION_STRING is not None:
    from raven import Client
    from raven.handlers.logging import SentryHandler
    from raven.conf import setup_logging
    logging.basicConfig(level=logging.WARN)
    client = Client(settings.SENTRY_CONNECTION_STRING)
    handler = SentryHandler(client)
    setup_logging(handler)

# Memory profiling
class ThreadWorker(Worker):
    """
    Note that this is an ugly hack that violates pretty much everything RQ stands for. Read at your own risk.
    """

    def execute_job(self, job):
        self.perform_job(job)

with Connection():
    qs = map(Queue, sys.argv[1:]) or [Queue()]
    w = ThreadWorker(qs)
    w.work()
