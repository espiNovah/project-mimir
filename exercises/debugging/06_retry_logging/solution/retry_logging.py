# Bugs: attempts were counted from 0, timeouts were logged at DEBUG (hidden at the usual
# INFO level), and giving up was logged as a WARNING instead of an ERROR.
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
    for attempt in range(1, attempts + 1):
        try:
            result = func()
        except TimeoutError:
            logger.warning("timeout on attempt %d of %d", attempt, attempts)
            continue
        logger.info("succeeded on attempt %d", attempt)
        return result
    logger.error("gave up after %d attempts", attempts)
    return None
