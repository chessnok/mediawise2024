import psycopg2

def get_db_connection():
    return psycopg2.connect(
        host="db",
        database="mediawise",
        user="mediawise",
        password="mediawise"
    )
