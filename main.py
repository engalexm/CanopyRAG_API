from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
import logging

from dotenv import load_dotenv
load_dotenv()

from canopy.knowledge_base import KnowledgeBase
from canopy.tokenizer import Tokenizer
from canopy.context_engine import ContextEngine
from canopy.chat_engine import ChatEngine
from canopy.models.data_models import UserMessage

# Initialize Canopy
Tokenizer.initialize()

INDEX_NAME = "wealth-outlook"
kb = KnowledgeBase(index_name=INDEX_NAME)
kb.connect()

context_engine = ContextEngine(kb)
chat_engine = ChatEngine(context_engine)

# Initialize FastAPI 
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_headers=['*'],
    allow_methods=['*']
)

@app.post("/")
async def ask_canopy_rag(query_str: str):
    logging.info(f"query_str: {query_str}")
    res = chat_engine.chat(messages=[UserMessage(content=query_str)], stream=False)
    res = res.choices[0].message.content
    logging.info(f"res: {res}")
    return res
