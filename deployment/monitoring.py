# monitoring.py
import logging
from prometheus_client import Counter, Histogram
from functools import wraps
import time

# Metrics
PROCESS_TIME = Histogram('pdf_process_duration_seconds', 'Time spent processing PDF')
ERRORS = Counter('pdf_process_errors', 'Number of processing errors')

def monitor(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            return result
        except Exception as e:
            ERRORS.inc()
            logging.error(f"Error in {func.__name__}: {str(e)}")
            raise
        finally:
            PROCESS_TIME.observe(time.time() - start_time)
    return wrapper