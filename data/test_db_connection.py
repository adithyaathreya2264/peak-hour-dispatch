"""
Simple script to test database connection
"""
import sys
import os

# Add backend to path
backend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'backend')
sys.path.insert(0, backend_dir)

from app.core.config import settings
from sqlalchemy import create_engine, text

print("=" * 60)
print(" Database Connection Test")
print("=" * 60)
print(f"\nTesting connection to database...")
print(f"Environment: {settings.ENVIRONMENT}")

# Mask password in URL for display
url_parts = settings.DATABASE_URL.split('@')
if len(url_parts) > 1:
    masked_url = url_parts[0].split(':')[:-1] + ['*****@'] + [url_parts[1]]
    print(f"Database URL: ...{':'.join(masked_url)}")
else:
    print(f"Database URL: {settings.DATABASE_URL[:50]}...")

try:
    engine = create_engine(settings.DATABASE_URL)
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1"))
        print("\n✅ Database connection successful!")
        print(f"Result: {result.scalar()}")
except Exception as e:
    print(f"\n❌ Database connection failed!")
    print(f"Error: {str(e)}")
    print("\nPlease check:")
    print("1. Your .env file has the correct DATABASE_URL")
    print("2. The Supabase project is active")
    print("3. The password in the URL is correct")
    print("4. Your firewall/network allows the connection")
