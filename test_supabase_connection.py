import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

url = os.getenv("DATABASE_URL")
print(f"🔗 DATABASE_URL = {url}")

try:
    engine = create_engine(url, future=True)
    with engine.connect() as conn:
        result = conn.execute(text("SELECT version();"))
        print("✅ Connexion réussie à Supabase PostgreSQL")
        print("📊 Version:", result.scalar())
except Exception as e:
    print("❌ Erreur de connexion:", e)
