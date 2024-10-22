import psycopg2
import os

def create_connection():
    conn = psycopg2.connect(
        dbname=os.environ.get('POSTGRES_DB'),
        user=os.environ.get('POSTGRES_USER'),
        password=os.environ.get('POSTGRES_PASSWORD'),
        host='localhost',
        port='5432'
    )
    return conn

def view_data():
    conn = create_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM transporter_account_information;")
    rows = cur.fetchall()

    for row in rows:
        print(row)

    cur.close()
    conn.close()

view_data()
