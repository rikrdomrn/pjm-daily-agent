# explore_db.py
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

conn = psycopg2.connect(
    host=os.getenv('DB_HOST'),
    port=os.getenv('DB_PORT', 5432),
    database=os.getenv('DB_NAME'),
    user=os.getenv('DB_USER'),
    password=os.getenv('DB_PASSWORD')
)

cur = conn.cursor()

# List all tables in pjm_data schema
print("📊 Tables in pjm_data schema:\n")
cur.execute("""
    SELECT table_name 
    FROM information_schema.tables 
    WHERE table_schema = 'pjm_data'
    ORDER BY table_name
""")

tables = cur.fetchall()
for table in tables:
    print(f"  📄 {table[0]}")

print("\n" + "="*70)

# For each table, show structure and sample data
for table in tables:
    table_name = table[0]
    print(f"\n📋 Table: pjm_data.{table_name}")
    print("-" * 70)
    
    # Show columns
    cur.execute(f"""
        SELECT column_name, data_type 
        FROM information_schema.columns 
        WHERE table_schema = 'pjm_data'
        AND table_name = '{table_name}'
        ORDER BY ordinal_position
    """)
    
    columns = cur.fetchall()
    print("Columns:")
    for col, dtype in columns:
        print(f"  • {col} ({dtype})")
    
    # Show row count
    cur.execute(f"SELECT COUNT(*) FROM pjm_data.{table_name}")
    count = cur.fetchone()[0]
    print(f"\nTotal rows: {count:,}")
    
    # Show sample data (first 3 rows)
    if count > 0:
        cur.execute(f"SELECT * FROM pjm_data.{table_name} LIMIT 3")
        samples = cur.fetchall()
        print(f"\nSample data (first 3 rows):")
        for i, row in enumerate(samples, 1):
            print(f"  Row {i}: {row}")

conn.close()