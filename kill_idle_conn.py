# core codes
from django.db import close_old_connections
from django.db import connection
close_old_connections()
with connection.cursor() as cursor:
    sql = "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE state = 'idle'"
    print(sql)
    cursor.execute(sql)
    row = cursor.fetchall()
    print(row)
