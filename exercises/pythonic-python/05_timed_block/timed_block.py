import time
from contextlib import contextmanager


@contextmanager
def timed_block(label: str, log: list):
    """Time the code inside a `with` block.

    When the block ends, append (label, seconds_elapsed) to log, even if the block
    raised an exception. Exceptions must still reach the caller.
    """
    raise NotImplementedError("Write this context manager")
    yield  # keeps this a generator so @contextmanager accepts it
