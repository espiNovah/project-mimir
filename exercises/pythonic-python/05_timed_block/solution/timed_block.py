import time
from contextlib import contextmanager


@contextmanager
def timed_block(label: str, log: list):
    """Time the code inside a `with` block.

    When the block ends, append (label, seconds_elapsed) to log, even if the block
    raised an exception. Exceptions must still reach the caller.
    """
    start = time.perf_counter()
    try:
        yield
    finally:
        # finally runs whether the block finished normally or raised.
        log.append((label, time.perf_counter() - start))
