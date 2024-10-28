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

def view_all_tables_with_data():
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

    # Print the table names and their data
    print("Tables in the database:")
    for table in tables:
        table_name = table[0]
        print(f"\nTable: {table_name}")
        
        # Query to get the first 5 rows of data from each table
        data_query = f"SELECT * FROM {table_name} LIMIT 5;"
        cur.execute(data_query)
        rows = cur.fetchall()

        # Print column names
        colnames = [desc[0] for desc in cur.description]
        print("Columns:", colnames)

        # Print each row in the table
        for row in rows:
            print(row)

    cur.close()
    conn.close()

# Call the function to view all tables and their data
view_all_tables_with_data()
