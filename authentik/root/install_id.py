"""install ID"""
from functools import lru_cache

from django.db import connection


@lru_cache
def get_install_id() -> str:
    """Get install ID of this instance. The method is cached as the install ID is
    not expected to change"""
    with connection.cursor() as cursor:
        cursor.execute("SELECT id FROM authentik_install_id LIMIT 1;")
        return cursor.fetchone()[0]
