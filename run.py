import sqlite3

# Replace 'your_database.db' with your actual database file
db_path = 'bank.db'
table_name = 'admins'  # Replace with your table name

def print_table_data(db_path, table_name):
    # Connect to the database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Execute SELECT query
        cursor.execute(f"SELECT * FROM {table_name}")
        rows = cursor.fetchall()

        # Get column names
        column_names = [description[0] for description in cursor.description]

        # Print column names
        print(" | ".join(column_names))
        print("-" * 50)

        # Print rows
        for row in rows:
            print(" | ".join(str(item) for item in row))

    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
    finally:
        conn.close()

# Call the function
print_table_data(db_path, table_name)
