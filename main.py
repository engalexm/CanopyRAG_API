from fastapi import FastAPI, HTTPException, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import traceback
import logging
import io
import fitz
import json
import re
import traceback

from dotenv import load_dotenv
load_dotenv()

from canopy.knowledge_base import KnowledgeBase, list_canopy_indexes
from canopy.tokenizer import Tokenizer
from canopy.context_engine import ContextEngine
from canopy.chat_engine import ChatEngine
from canopy.models.data_models import UserMessage, SystemMessage
from canopy.models.data_models import Document
from canopy.knowledge_base.record_encoder import OpenAIRecordEncoder

# Initialize logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize Canopy
Tokenizer.initialize()

# It will only load those indices once which exist at the time of app init
INDEX_NAMES = []
CHAT_ENGINES = {}

def update_index_engines():
    global INDEX_NAMES
    global CHAT_ENGINES
    INDEX_NAMES = list_canopy_indexes()
    for index_name in INDEX_NAMES:
        if index_name not in CHAT_ENGINES:
            print(f"Adding new index {index_name} to CHAT_ENGINES")
            kb = KnowledgeBase(index_name=index_name)
            kb.connect()
            context_engine = ContextEngine(kb)
            chat_engine = ChatEngine(context_engine)
            CHAT_ENGINES[index_name] = chat_engine

update_index_engines()

# Initialize FastAPI 
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_headers=['*'],
    allow_methods=['*']
)

class CanopyRAGInput(BaseModel):
    index_name: str = "canopy--citi-wealth-outlook-2024"
    query: list = [{"role": "user", "content": "What does Citi project the inflation rate to be?"}]

@app.post("/upload")
async def upload_file_to_canopy(file: UploadFile = File(...)):
    try:
        idx_name = re.sub('[^0-9a-zA-Z]+', '-', file.filename.replace('.pdf','').lower())

        if f'canopy--{idx_name}' in list_canopy_indexes():
            detail_str = f"{idx_name} already exists with {file.filename} indexed"

        else:    
            file_bytes = io.BytesIO(file.file.read())
            doc = fitz.open(stream=file_bytes)
            extracted_text = [page.get_text() for page in doc]
            data = []
            for i,page in enumerate(extracted_text):
                data.append({
                    'id': str(i), 
                    'text': page, 
                    'source': f'{file.filename}: page {i+1}', 
                    'metadata': {'title': file.filename,
                                'primary_category': 'Finance',
                                'published': 2024
                                },
                })
            documents = [Document(id=doc['id'],
                                text=doc['text'],
                                source=doc['source'],
                                metadata=doc['metadata']) for doc in data]
               
            encoder = OpenAIRecordEncoder(model_name="text-embedding-3-small")
            kb = KnowledgeBase(index_name=idx_name, record_encoder=encoder)
            kb.create_canopy_index()
            kb.connect()
            kb.upsert(documents,show_progress_bar=True)
            detail_str = f"Created new index {idx_name} and upserted {len(documents)} documents"

        return {"status": "OK", "detail": detail_str}
    
    except Exception as exc:
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=traceback.format_exc())
    


@app.post("/ask_canopy_rag")
async def ask_canopy_rag(request: CanopyRAGInput):
    try:
        logger.info(f"request.dict(): {request.dict()}")
        assert request.index_name in list_canopy_indexes(), f"request.index_name: {request.index_name} not found in list_canopy_indexes(): {list_canopy_indexes()}"
        if request.index_name not in CHAT_ENGINES:
           update_index_engines()
        chat_engine = CHAT_ENGINES[request.index_name]

        messages = []
        for item in request.query:
            if item['role'] == 'user':
                messages.append(UserMessage(content=item['content']))
            else:
                messages.append(SystemMessage(content=item['content']))

        res = chat_engine.chat(messages=messages, stream=False)
        logger.info(f"res: {res}")
        res = res.choices[0].message.content
        logger.info(f"res.choices[0].message.content: {res}")
        return res
    except Exception as exc:
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=traceback.format_exc())

@app.get("/pinecone_indices")
async def get_pinecone_indices():
    return list_canopy_indexes()

@app.post("/ask_canopy_rag")
async def ask_canopy_rag(request: CanopyRAGInput):
    try:
        logger.info(f"request.dict(): {request.dict()}")
        assert request.index_name in list_canopy_indexes(), f"request.index_name: {request.index_name} not found in list_canopy_indexes(): {list_canopy_indexes()}"
        assert request.index_name in CHAT_ENGINES, f"request.index_name: {request.index_name} not found in CHAT_ENGINES: {CHAT_ENGINES}; may need to restart the API to load from Pinecone"
        chat_engine = CHAT_ENGINES[request.index_name]

        messages = []
        for item in request.query:
            if item['role'] == 'user':
                messages.append(UserMessage(content=item['content']))
            else:
                messages.append(SystemMessage(content=item['content']))

        res = chat_engine.chat(messages=messages, stream=False)
        logger.info(f"res: {res}")
        res = res.choices[0].message.content
        logger.info(f"res.choices[0].message.content: {res}")
        return res
    except Exception as exc:
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=traceback.format_exc())