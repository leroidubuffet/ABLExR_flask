import sqlite3

# Connect to the SQLite database
conn = sqlite3.connect('sqlite/training.db')
cursor = conn.cursor()

# Get the table names
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
table_names = cursor.fetchall()

# Iterate over the table names and fetch their content
for table in table_names:
    table_name = table[0]
    print(f"Table: {table_name}")
    cursor.execute(f"SELECT * FROM {table_name};")
    table_content = cursor.fetchall()
    for row in table_content:
        print(row)

# Close the cursor and the database connection
cursor.close()
conn.close()
