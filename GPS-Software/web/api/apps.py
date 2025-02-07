from django.apps import AppConfig
from sys import argv
import threading

class ApiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'api'

    def ready(self):
        
        if not 'runserver' in argv: return True
        import api.signals
        
        # from .tasks import start_scheduler
        # start_scheduler()
        from .tcp_server import start_tcp_server
        if "runserver" in argv:
            threading.Thread(target=start_tcp_server, daemon=True).start()