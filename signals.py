import logging

from django.db import connection
from django.db.backends.signals import connection_created

# Get the logger for performance logs
logger = logging.getLogger('performance')

def log_sql_queries(sender, **kwargs):
    # Log all SQL queries executed during a request
    queries = connection.queries
    for query in queries:
        logger.info(f"Query: {query['sql']} executed in {query['time']} seconds")

# Connect the signal for query execution
connection_created.connect(log_sql_queries)