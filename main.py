from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import logging

from dotenv import load_dotenv
load_dotenv()

from canopy.knowledge_base import KnowledgeBase
from canopy.tokenizer import Tokenizer
from canopy.context_engine import ContextEngine
from canopy.chat_engine import ChatEngine
from canopy.models.data_models import UserMessage

# Initialize logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize Canopy
Tokenizer.initialize()

INDEX_NAMES = ["wealth-outlook"]
CHAT_ENGINES = {}
for index_name in INDEX_NAMES:
    kb = KnowledgeBase(index_name=index_name)
    kb.connect()
    context_engine = ContextEngine(kb)
    chat_engine = ChatEngine(context_engine)
    CHAT_ENGINES[index_name] = chat_engine

# Initialize FastAPI 
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_headers=['*'],
    allow_methods=['*']
)

class CanopyRAGInput(BaseModel):
    index_name: str
    query: str

@app.post("/ask_canopy_rag")
async def ask_canopy_rag(request: CanopyRAGInput):
    logger.info(f"request.dict(): {request.dict()}")
    chat_engine = CHAT_ENGINES[request.index_name]
    res = chat_engine.chat(messages=[UserMessage(content=request.query)], stream=False)
    logger.info(f"res: {res}")
    res = res.choices[0].message.content
    logger.info(f"res.choices[0].message.content: {res}")
    return res
