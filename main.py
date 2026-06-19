from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from contextlib import asynccontextmanager

from database import engine, Base, get_db
import models
from service.oylan import send_message
from service.chat import save_message, get_history

# Use lifespan for startup tasks
@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield

app = FastAPI(lifespan=lifespan)

class ChatRequest(BaseModel):
    message: str
    session_id: str = 'default'

@app.get('/')
def root():
    return {'message': 'Oylan assistant is running!'}

@app.get('/health')
def health():
    return {'status': 'ok'}

@app.post('/chat')
async def chat(req: ChatRequest, db: AsyncSession = Depends(get_db)):
    if not req.message.strip():
        raise HTTPException(400, detail='Message cannot be empty')
    
    try:
        # 1. Fetch existing history
        history = await get_history(db, req.session_id)
        
        # 2. Get reply from AI
        reply = await send_message(req.message, history)
        
        # 3. Save both user message and AI reply to DB
        await save_message(db, req.session_id, 'user', req.message)
        await save_message(db, req.session_id, 'assistant', reply)
        
        return {'reply': reply, 'session_id': req.session_id}
    except Exception as e:
        raise HTTPException(500, detail=str(e))

@app.get('/history/{session_id}')
async def history(session_id: str, db: AsyncSession = Depends(get_db)):
    msgs = await get_history(db, session_id, limit=50)
    return {'session_id': session_id, 'messages': msgs}