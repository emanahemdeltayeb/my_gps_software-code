from django.apps import AppConfig
from sys import argv

class ApiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'api'

    def ready(self):
        if not 'runserver' in argv: return True
        import api.signals
        
        from .tasks import start_scheduler
        start_scheduler()