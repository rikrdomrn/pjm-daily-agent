# check_prices.py
import psycopg2
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta

load_dotenv()

conn = psycopg2.connect(
    host=os.getenv('DB_HOST'),
    port=os.getenv('DB_PORT', 5432),
    database=os.getenv('DB_NAME'),
    user=os.getenv('DB_USER'),
    password=os.getenv('DB_PASSWORD')
)

cur = conn.cursor()

# Check realtime_prices structure
print("📋 pjm_data.realtime_prices table structure:\n")
cur.execute("""
    SELECT column_name, data_type 
    FROM information_schema.columns 
    WHERE table_schema = 'pjm_data' 
    AND table_name = 'realtime_prices'
    ORDER BY ordinal_position
""")

columns = cur.fetchall()
for col, dtype in columns:
    print(f"  • {col} ({dtype})")

# Check date range
cur.execute("SELECT MIN(timestamp), MAX(timestamp) FROM pjm_data.realtime_prices")
date_range = cur.fetchone()
print(f"\nDate range: {date_range[0]} to {date_range[1]}")

# Check row count
cur.execute("SELECT COUNT(*) FROM pjm_data.realtime_prices")
count = cur.fetchone()[0]
print(f"Total rows: {count:,}")

# Sample yesterday's data
yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
cur.execute(f"""
    SELECT * FROM pjm_data.realtime_prices 
    WHERE timestamp::date = '{yesterday}'
    LIMIT 5
""")

print(f"\nSample data from {yesterday}:")
samples = cur.fetchall()
for row in samples:
    print(f"  {row}")

conn.close()