from django.core.management.base import BaseCommand
from api.tcp_server import start_tcp_server

class Command(BaseCommand):
    help = "Start the JT/T 808 TCP server"

    def handle(self, *args, **kwargs):
        start_tcp_server()