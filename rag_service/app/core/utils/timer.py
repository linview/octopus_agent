import sys
import time
from functools import wraps
from loguru import logger

logger.remove()
logger.add(sys.stdout, level="DEBUG")

def timer(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.strftime("%Y%m%d %H:%M:%S")
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        end_time = time.strftime("%Y%m%d %H:%M:%S")
        duration = (end - start) * 1000  # 转换为毫秒
        logger.info(f"{func.__name__} start at {start_time}, end at {end_time}, duration: {duration:.2f} ms")
        return result
    return wrapper 