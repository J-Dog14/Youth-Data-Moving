import sqlite3
import os
import re

# Path to the folder containing your txt files
folder_path = 'D:/Youth Data Moving/Output Files/'
db_path = 'D:/Youth Data Moving/Output Files/movement_database.db'

# Delete the database file if it exists to start fresh
if os.path.exists(db_path):
    os.remove(db_path)
    print(f"Deleted existing database at {db_path}")

# Connect to the SQLite database (or create it if it doesn't exist)
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Define the table schemas for "small," "norm," and "large"
table_schemas = {
    'small': '''CREATE TABLE IF NOT EXISTS small (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT,
                    trial_name TEXT,
                    Pron_at_FP REAL,
                    Pron_at_MW REAL,
                    Pron_at_Rel REAL,
                    Max_Pro REAL,
                    Time_to_Max_Pro REAL
                )''',
    'norm': '''CREATE TABLE IF NOT EXISTS norm (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT,
                    trial_name TEXT,
                    Pron_at_FP REAL,
                    Pron_at_MW REAL,
                    Pron_at_Rel REAL,
                    Max_Pro REAL,
                    Time_to_Max_Pro REAL
                )''',
    'large': '''CREATE TABLE IF NOT EXISTS large (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT,
                    trial_name TEXT,
                    Pron_at_FP REAL,
                    Pron_at_MW REAL,
                    Pron_at_Rel REAL,
                    Max_Pro REAL,
                    Time_to_Max_Pro REAL
                )'''
}

# Create the tables in the database (if they don't exist)
for schema in table_schemas.values():
    cursor.execute(schema)


# Function to extract the client's name from the first line of the file
def extract_name(line):
    match = re.search(r'Data\\(.*?)[_\\]', line)
    if match:
        return match.group(1)
    return None


# Function to insert data into the appropriate table
def insert_data_into_table(table_name, name, trial_name, variables):
    # Skip the first value (the extra "1")
    variables = variables[1:]

    print(f"Inserting data for {name} into {table_name}, Trial: {trial_name}, Variables: {variables}")

    cursor.execute(f"""INSERT INTO {table_name} 
                       (name, trial_name, Pron_at_FP, Pron_at_MW, Pron_at_Rel, Max_Pro, Time_to_Max_Pro) 
                       VALUES (?, ?, ?, ?, ?, ?, ?)""",
                   (name, trial_name, *variables))


# Loop through the txt files in the folder
for file_name in os.listdir(folder_path):
    if file_name.endswith('.txt'):
        trial_name = os.path.splitext(file_name)[0]

        # Determine which table the file belongs to
        if 'small' in trial_name.lower():
            table_name = 'small'
        elif 'norm' in trial_name.lower():
            table_name = 'norm'
        elif 'large' in trial_name.lower():
            table_name = 'large'
        else:
            continue  # Skip files that don't match the table naming pattern

        # Load the data from the txt file
        file_path = os.path.join(folder_path, file_name)
        try:
            with open(file_path, 'r') as f:
                # Extract the name from the first line
                first_line = f.readline().strip()
                name = extract_name(first_line)

                # Print the extracted name to verify
                print(f"File: {file_name}, Extracted Name: {name}")

                if not name:
                    print(f"Name extraction failed for {file_name}, skipping.")
                    continue

                # Read all lines until we find the line with the actual numeric data
                for line_num, line in enumerate(f):
                    line = line.strip()

                    # Print the line contents and line number to debug
                    print(f"Line {line_num} of {file_name}: {line}")

                    # Skip non-numeric lines and find the correct line (Line 4 in this case)
                    if line_num == 4:
                        variables = [float(value) for value in line.split()]

                        # Print the detected variables to verify before inserting
                        print(f"Processing file: {file_name}, Variables: {variables}")

                        # Insert the data into the appropriate table
                        insert_data_into_table(table_name, name, trial_name, variables)
                        break  # Only process the first valid line of numeric data

        except Exception as e:
            print(f"Unexpected error with file {file_name}: {e}")

# Commit the changes and close the connection
conn.commit()
conn.close()

print("Data successfully inserted into the database.")
