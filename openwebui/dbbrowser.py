import sqlite3
import sys

# Ensure UTF-8 encoding for Python 2.7
reload(sys)
sys.setdefaultencoding('utf-8')


#SQL_DB="./vector_db/chroma.sqlite3"
SQL_DB="./webui.db"

# Connect to the SQLite database
try:
    conn = sqlite3.connect(SQL_DB)
    cursor = conn.cursor()

    # Check if the connection is valid
    cursor.execute("SELECT sqlite_version();")
    print("SQLite version:", cursor.fetchone()[0])

    # Query to get all table names, including hidden or alternative schema tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()

    if tables:
        print("Tables in the database:")
        for table in tables:
            print(table[0])
    else:
        print("No tables found in the database.")

except sqlite3.Error as e:
    print("Error connecting to the database:", e)

finally:
    # Close the connection
    if conn:
        conn.close()


# now print contents of config table
try:
    conn = sqlite3.connect(SQL_DB)
    cursor = conn.cursor()

    # Get the names of all tables in the database
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()

    if tables:
        for table in tables:
            table_name = table[0]
            print("\nContents of the '{}' table:".format(table_name))

            # Query to select all data from the current table
            cursor.execute("SELECT * FROM '{}';".format(table_name))
            rows = cursor.fetchall()

            if rows:
                # Get column names for better display
                column_names = [description[0] for description in cursor.description]
                print("\t".join(column_names))  # Print column headers

                # Print each row in the table
                for row in rows:
                    print("\t".join(map(lambda x: unicode(x), row)))
            else:
                print("The '{}' table is empty.".format(table_name))
    else:
        print("No tables found in the database.")

except sqlite3.Error as e:
    print("Error connecting to the database:", e)

finally:
    # Close the connection
    if conn:
        conn.close()


# Connect to the database
#conn = sqlite3.connect('webui.db')
#cursor = conn.cursor()

# Execute a query
#cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
#print(cursor.fetchall())  # List all tables

# Close the connection
#conn.close()

