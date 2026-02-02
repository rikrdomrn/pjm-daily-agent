# test_db.py
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

try:
    print(f"Connecting to {os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}...")
    
    conn = psycopg2.connect(
        host=os.getenv('DB_HOST'),
        port=os.getenv('DB_PORT', 5432),
        database=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD')
    )
    
    cur = conn.cursor()
    
    # List all tables
    cur.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public'
    """)
    
    tables = cur.fetchall()
    print("\n✅ Connected successfully!")
    print(f"\nAvailable tables in {os.getenv('DB_NAME')}:")
    for table in tables:
        print(f"  - {table[0]}")
    
    conn.close()
    
except Exception as e:
    print(f"❌ Connection failed: {e}")