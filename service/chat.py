from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models import Message

async def save_message(db: AsyncSession, session_id: str, role: str, content: str):
    """Saves a new message to the database."""
    msg = Message(session_id=session_id, role=role, content=content)
    db.add(msg)
    await db.commit()
    await db.refresh(msg)  # Good practice to refresh to get the generated ID/timestamp

async def get_history(db: AsyncSession, session_id: str, limit: int = 10) -> list[dict]:
    """Retrieves chat history for a specific session, ordered by time."""
    result = await db.execute(
        select(Message)
        .where(Message.session_id == session_id)
        .order_by(Message.created_at.desc())
        .limit(limit)
    )
    msgs = result.scalars().all()
    
    # Return as a list of dictionaries, reversed so oldest messages appear first
    return [{'role': m.role, 'content': m.content} for m in reversed(msgs)] 