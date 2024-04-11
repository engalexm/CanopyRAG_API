from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import traceback
import logging

from dotenv import load_dotenv
load_dotenv()

from canopy.knowledge_base import KnowledgeBase, list_canopy_indexes
from canopy.tokenizer import Tokenizer
from canopy.context_engine import ContextEngine
from canopy.chat_engine import ChatEngine
from canopy.models.data_models import UserMessage

# Initialize logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize Canopy
Tokenizer.initialize()

# It will only load those indices once which exist at the time of app init
INDEX_NAMES = list_canopy_indexes()
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

@app.get("/pinecone_indices")
async def get_pinecone_indices():
    return list_canopy_indexes()

class CanopyRAGInput(BaseModel):
    index_name: str = "canopy--citi-wealth-outlook-2024"
    query: str

@app.post("/ask_canopy_rag")
async def ask_canopy_rag(request: CanopyRAGInput):
    try:
        logger.info(f"request.dict(): {request.dict()}")
        assert request.index_name in list_canopy_indexes(), f"request.index_name: {request.index_name} not found in list_canopy_indexes(): {list_canopy_indexes()}"
        assert request.index_name in CHAT_ENGINES, f"request.index_name: {request.index_name} not found in CHAT_ENGINES: {CHAT_ENGINES}; may need to restart the API to load from Pinecone"
        chat_engine = CHAT_ENGINES[request.index_name]
        res = chat_engine.chat(messages=[UserMessage(content=request.query)], stream=False)
        logger.info(f"res: {res}")
        res = res.choices[0].message.content
        logger.info(f"res.choices[0].message.content: {res}")
        return res
    except Exception as exc:
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=traceback.format_exc())