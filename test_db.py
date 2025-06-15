import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost:5435/releasebot"

async def test_connection():
    print(f"Testing connection with DATABASE_URL: {DATABASE_URL}")
    engine = create_async_engine(DATABASE_URL)
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        print("Connection successful!")
    except Exception as e:
        print(f"Connection failed: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_connection())
