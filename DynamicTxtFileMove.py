import sqlite3
import os
import re

# Paths
folder_path = 'D:/Youth Data Moving/Output Files/'
db_path = 'D:/Youth Data Moving/Output Files/movement_database.db'

# Connect to SQLite database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()


def extract_name_and_table(file_path):
    """Extracts the client name and table name from the first line of the file."""
    with open(file_path, 'r') as file:
        first_line = file.readline().strip()
        match_name = re.search(r'Data\\(.*?),', first_line)
        match_table = re.search(r'\b(small|norm|large|pitch)\b', first_line.lower())

        name = match_name.group(1) if match_name else None
        table_name = match_table.group(1) if match_table else None

        return name, table_name

def create_table_dynamically(table_name, column_names):
    """Ensures the table exists and dynamically adds missing columns."""
    # Check if the table exists by fetching its schema
    cursor.execute(f"PRAGMA table_info({table_name})")
    existing_columns = {row[1] for row in cursor.fetchall()}  # Extract column names
    print(f"Existing columns in {table_name}: {existing_columns}")

    # Remove duplicates from column_names
    column_names = list(dict.fromkeys(column_names))  # Deduplicate while preserving order

    if not existing_columns:
        # Table doesn't exist, create it with all columns
        columns_sql = ', '.join([f'"{col}" REAL' for col in column_names])
        create_table_sql = f'''
            CREATE TABLE {table_name} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                trial_name TEXT,
                {columns_sql}
            )
        '''
        print(f"Creating table {table_name} with columns: {column_names}")
        cursor.execute(create_table_sql)
    else:
        # Table exists; dynamically add only missing columns
        for col in column_names:
            if col not in existing_columns:
                alter_table_sql = f'ALTER TABLE {table_name} ADD COLUMN "{col}" REAL'
                print(f"Adding missing column {col} to table {table_name}")
                cursor.execute(alter_table_sql)

def insert_data_dynamically(table_name, name, trial_name, column_names, values):
    """Inserts data dynamically into the specified table."""
    placeholders = ', '.join(['?' for _ in values])
    columns_sql = ', '.join([f'"{col}"' for col in column_names])
    insert_sql = f'''
        INSERT INTO {table_name} (name, trial_name, {columns_sql})
        VALUES (?, ?, {placeholders})
    '''
    cursor.execute(insert_sql, (name, trial_name, *values))
    print(f"Inserted data into {table_name}: {values}")


def process_txt_file(file_path):
    """Processes a single txt file."""
    with open(file_path, 'r') as file:
        lines = file.readlines()

        # Extract name and table name
        name, table_name = extract_name_and_table(file_path)
        if not name or not table_name:
            print(f"Name or table determination failed for {file_path}")
            return

        # Extract column names from the second line
        column_names = [col.strip() for col in lines[1].strip().split()]

        # Deduplicate column names
        column_names = list(dict.fromkeys(column_names))

        # Create the table dynamically
        create_table_dynamically(table_name, column_names)

        # Parse the sixth line (data row)
        data_line = lines[5].strip()
        values = [float(val) for val in data_line.split()]

        # Ensure the number of values matches the number of columns
        if len(values) != len(column_names):
            print(f"Mismatch in columns and values for {file_path}:")
            print(f"Columns: {len(column_names)}, Values: {len(values)}")
            return  # Skip this file and log the issue

        # Insert the data into the table
        trial_name = os.path.splitext(os.path.basename(file_path))[0]
        insert_data_dynamically(table_name, name, trial_name, column_names, values)

# Loop through txt files in the folder
for file_name in os.listdir(folder_path):
    if file_name.endswith('.txt'):
        file_path = os.path.join(folder_path, file_name)
        process_txt_file(file_path)

# Commit and close
conn.commit()
conn.close()

print("Data successfully processed and inserted.")
