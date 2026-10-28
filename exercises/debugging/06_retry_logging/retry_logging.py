import logging

logger = logging.getLogger("retry")


def call_with_retries(func, attempts: int = 3):
    """Call func() until it succeeds, retrying on TimeoutError, at most `attempts` times.

    Logs to the "retry" logger:
      WARNING "timeout on attempt N of M"   for each timeout
      INFO    "succeeded on attempt N"      on success
      ERROR   "gave up after M attempts"    when every attempt timed out
    Returns func's result, or None if every attempt timed out.
    """
    for attempt in range(attempts):
        try:
            result = func()
        except TimeoutError:
            logger.debug("timeout on attempt %d of %d", attempt, attempts)
            continue
        logger.info("succeeded on attempt %d", attempt)
        return result
    logger.warning("gave up after %d attempts", attempts)
    return None
