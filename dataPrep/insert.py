import os
from pathlib import Path
import pandas as pd
from psycopg2 import connect, sql
from psycopg2.extras import execute_values
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Define the base directory and Excel file path
BASE_DIR = Path(__file__).resolve().parent
excel_file = os.path.join(BASE_DIR, "basePlot.xlsx")

# Database connection details
schema_name = "taksasi"
table_name = "gis_plot"

try:
    conn = connect(
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port="5432"
    )
    print("Connection established successfully!")
except Exception as e:
    print(f"Error connecting to the database: {e}")
    exit()

# Check if the table exists in the schema
try:
    with conn.cursor() as cur:
        cur.execute(
            sql.SQL("""
                SELECT EXISTS (
                    SELECT 1
                    FROM information_schema.tables
                    WHERE table_schema = %s AND table_name = %s
                )
            """),
            (schema_name, table_name)
        )
        if cur.fetchone()[0]:
            print("Table found!")
        else:
            print(f"Table '{schema_name}.{table_name}' does not exist.")
            conn.close()
            exit()
except Exception as e:
    print(f"Error checking the table: {e}")
    conn.close()
    exit()

# Read the Excel file
try:
    df = pd.read_excel(excel_file)
    print("Excel file loaded successfully!")
except Exception as e:
    print(f"Error loading Excel file: {e}")
    conn.close()
    exit()

# Format the 'plant_date' column
try:
    df['plant_date'] = pd.to_datetime(df['plant_date'], format='%d/%m/%Y', errors='coerce')
    df['plant_date'] = df['plant_date'].apply(
        lambda x: x.strftime('%Y/%m/%d') if pd.notnull(x) else None
    )
    print("Date conversion successful!")
except Exception as e:
    print(f"Error formatting 'plant_date': {e}")
    conn.close()
    exit()

# Ensure DataFrame schema matches the table
df.columns = ['plot_id', 'petani', 'var', 'mt', 'plant_date', 'status', 'kategori', 'kategori_grup', 'luas', 'desa', 'wilayah']
columns = df.columns.tolist()

# Preview the tuples
data_tuples = list(df.itertuples(index=False, name=None))
print("\nPreview of tuples to insert:")
for row in data_tuples[:5]:  # Limit preview to 5 rows
    print(row)

# Dry-run SQL query
insert_query = sql.SQL("""
    INSERT INTO {}.{} ({}) VALUES %s
""").format(
    sql.Identifier(schema_name),
    sql.Identifier(table_name),
    sql.SQL(', ').join(map(sql.Identifier, columns))
)
print("\nGenerated SQL Query:")
print(insert_query.as_string(conn))

# Insert data into the database
try:
    with conn.cursor() as cur:
        execute_values(
            cur,
            insert_query,
            data_tuples
        )
        conn.commit()
        print("\nAll data inserted successfully!")
except Exception as e:
    print(f"Error inserting data: {e}")
finally:
    conn.close()
    
