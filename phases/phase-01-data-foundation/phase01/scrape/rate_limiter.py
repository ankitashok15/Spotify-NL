import logging
import time

logger = logging.getLogger(__name__)


class RateLimiter:
    def __init__(self, delay_seconds: float = 2.0, max_retries: int = 5):
        self.delay_seconds = delay_seconds
        self.max_retries = max_retries

    def wait(self) -> None:
        time.sleep(self.delay_seconds)

    def run_with_retry(self, fn, *args, **kwargs):
        last_error = None
        for attempt in range(self.max_retries):
            try:
                return fn(*args, **kwargs)
            except Exception as exc:
                last_error = exc
                wait = min(30 * (2**attempt), 120)
                logger.warning("Request failed (attempt %s/%s): %s — retry in %ss", attempt + 1, self.max_retries, exc, wait)
                time.sleep(wait)
        raise last_error
