import psycopg2

def connect_to_db():
    try:
        # Connection parameters
        conn = psycopg2.connect(
            host="ep-royal-thunder-45099107.us-east-1.postgres.vercel-storage.com",
            database="verceldb",
            user="default",
            password="QhYas0zXyE7A",
            port="5432"
        )

        # Create a cursor object
        cur = conn.cursor()

        # Execute a query
        cur.execute("SELECT version();")

        # Fetch and print the result of the query
        db_version = cur.fetchone()
        print("Database version:", db_version)

        # Close the cursor and connection
        cur.close()
        conn.close()

    except (Exception, psycopg2.DatabaseError) as error:
        print("Error while connecting to PostgreSQL", error)

if __name__ == '__main__':
    connect_to_db()

