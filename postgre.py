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

def view_all_tables():
    conn = create_connection()
    cur = conn.cursor()

    # SQL query to get all tables
    query = """
    SELECT table_name 
    FROM information_schema.tables 
    WHERE table_schema = 'public';
    """
    
    cur.execute(query)
    tables = cur.fetchall()

    # Print the table names
    print("Tables in the database:")
    for table in tables:
        print(table[0])  # table[0] contains the table name

    cur.close()
    conn.close()


# Call the function to view all tables
view_all_tables()

def view_table_columns(table_name):
    conn = create_connection()
    cur = conn.cursor()

    # SQL query to get all columns for the specified table
    query = """
    SELECT column_name, data_type
    FROM information_schema.columns
    WHERE table_name = %s;
    """
    
    cur.execute(query, (table_name,))
    columns = cur.fetchall()

    # Print the column names and their data types
    print(f"Columns in the table '{table_name}':")
    for column in columns:
        print(f"Column: {column[0]}, Data Type: {column[1]}")

    cur.close()
    conn.close()

