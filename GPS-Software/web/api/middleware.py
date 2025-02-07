import logging
import time

# Middleware to log request details (method, path, status code, processing time).
# Get the logger for requests
logger = logging.getLogger('django.server')

class RequestLoggingMiddleware:
    """
    Middleware to log request details (method, path, status code, processing time).
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Start timer
        start_time = time.time()

        # Get response
        response = self.get_response(request)

        # Calculate request processing time
        duration = time.time() - start_time
        method = request.method
        path = request.path
        status_code = response.status_code

        # Log request details
        logger.info(f"Request: {method} {path} | Status: {status_code} | Time: {duration:.4f}s")

        return response

# Middleware to log performance logs.   
# Get the logger you defined for performance logs
logger = logging.getLogger('performance')

class RequestTimingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start_time = time.time()  # Record the start time
        response = self.get_response(request)  # Process the request
        end_time = time.time()  # Record the end time

        # Calculate the time taken to process the request
        elapsed_time = end_time - start_time

        # Log the performance data
        logger.info(f"Request to {request.path} took {elapsed_time:.4f} seconds")

        return response