import os
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

load_dotenv()

# Ensure the DATABASE_URL is not None
DATABASE_URL = os.getenv('DATABASE_URL')
if DATABASE_URL is None:
    raise ValueError("DATABASE_URL is not set in the environment variables")

# 1. Create the engine
engine = create_async_engine(DATABASE_URL, echo=False)

# 2. Use async_sessionmaker instead of sessionmaker
AsyncSessionLocal = async_sessionmaker(
    bind=engine, 
    class_=AsyncSession, 
    expire_on_commit=False
)

class Base(DeclarativeBase):
    pass

# 3. This will now correctly support 'async with'
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session