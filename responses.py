import psutil
import os
import logging
from fastapi import FastAPI, Request  # <-- Added Request import

# Helper function to get memory usage (in MB)
def get_memory_usage():
    process = psutil.Process(os.getpid())
    return process.memory_info().rss / 1024 / 1024  # in MB

# Middleware to log memory usage before and after request handling
async def log_memory_usage(request: Request, call_next):
    before_memory = get_memory_usage()
    logging.info(f"Memory before request: {before_memory:.2f} MB")

    response = await call_next(request)

    after_memory = get_memory_usage()
    memory_used = after_memory - before_memory
    logging.info(f"Memory after request: {after_memory:.2f} MB")
    logging.info(f"Memory used during request: {memory_used:.2f} MB")

    return response
