import mysql.connector
import os
# Database connection details
config = {
    'user': os.environ.get("SQL_USER", "user"),
    'password': os.environ.get("SQL_PASSWORD", "password"),
    'host': os.environ.get("SQL_HOST", "localhost"),
    'database': os.environ.get("SQL_DATABASE"),
}

# Path to your schema dump file
schema_dump_file = 'schema.sql'

# Establish a connection to the database
try:
    connection = mysql.connector.connect(**config)
    cursor = connection.cursor()
    print("Connected to the database.")
    # Read the schema dump file
    with open(schema_dump_file, 'r') as file:
        schema_sql = file.read()
    print("Schema dump file read successfully.")
    # Execute the schema SQL
    for result in cursor.execute(schema_sql, multi=True):
        if result.with_rows:
            print("Rows produced by statement '{}':".format(result.statement))
            print(result.fetchall())
        else:
            print("Number of rows affected by statement '{}': {}".format(result.statement, result.rowcount))

    # Commit the transaction
    connection.commit()
    print("Transaction committed.")
    

except mysql.connector.Error as err:
    print(f"Error: {err}")
finally:
    if connection.is_connected():
        cursor.close()
        connection.close()
        print("Connection closed.")
