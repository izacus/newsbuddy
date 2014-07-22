#!/usr/bin/env python
"""
This is a RQ worker used for async task processing
"""

import sys
from rq import Connection, Queue, Worker

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