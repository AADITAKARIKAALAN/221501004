#Logging Middleware
import time
from functools import wraps
from flask import request, g

class LoggingMiddleware:
    def __init__(self, app=None):
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app):
        app.before_request(self.before_request)
        app.after_request(self.after_request)
    
    def before_request(self):
        g.start_time = time.time()
        g.request_id = str(int(time.time() * 1000))
        print(f"[REQUEST] {request.method} {request.path}")
    
    def after_request(self, response):
        duration = int((time.time() - getattr(g, 'start_time', time.time())) * 1000)
        print(f"[RESPONSE] {request.method} {request.path} - Status: {response.status_code} - Duration: {duration}ms")
        return response

def log_function(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        function_name = func.__name__
        print(f"[FUNCTION] {function_name} started")
        
        try:
            result = func(*args, **kwargs)
            duration = (time.time() - start_time) * 1000
            print(f"[FUNCTION] {function_name} completed in {duration:.2f}ms")
            return result
        except Exception as e:
            duration = (time.time() - start_time) * 1000
            print(f"[FUNCTION] {function_name} failed after {duration:.2f}ms with error: {str(e)}")
            raise
    
    return wrapper
