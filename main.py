import json
import logging
import traceback
logger = logging.getLogger()
logger.setLevel("INFO")

from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

from canopy.knowledge_base import KnowledgeBase
from canopy.tokenizer import Tokenizer
from canopy.context_engine import ContextEngine
from canopy.chat_engine import ChatEngine
from canopy.models.data_models import UserMessage


# Query Canopy and Pinecone
def ask_canopy_rag(event, context):
    try:
        # Initialize Canopy
        Tokenizer.initialize()
        kb = KnowledgeBase(index_name="canopy--citi-wealth-outlook-2024")
        kb.connect()
        context_engine = ContextEngine(kb)
        chat_engine = ChatEngine(context_engine)

        res = ""
        request_body = json.loads(event['body'])

        logger.info("### REQUEST_BODY")
        logger.info(request_body)

        if 'query' in request_body:
            res = chat_engine.chat(messages=[UserMessage(content=request.query)], stream=False)      
            res = res.choices[0].message.content
        return res

    except Exception as exc:
        logger.error(traceback.format_exc())
        return ""