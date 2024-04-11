import json
import traceback

from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

from canopy.knowledge_base import KnowledgeBase
from canopy.tokenizer import Tokenizer
from canopy.context_engine import ContextEngine
from canopy.chat_engine import ChatEngine
from canopy.models.data_models import UserMessage

# Initialize Canopy
Tokenizer.initialize()
kb = KnowledgeBase(index_name="canopy--citi-wealth-outlook-2024")
kb.connect()
context_engine = ContextEngine(kb)
chat_engine = ChatEngine(context_engine)

# Query Canopy and Pinecone
def ask_canopy_rag(event, context):
    try:
        res = ""

        if 'query' in event:
            res = chat_engine.chat(messages=[UserMessage(content=event["query"])], stream=False)      
            res = res.choices[0].message.content

        return {
            "statusCode": 200,
            "body": json.dumps({
                "result": res,
                "event": event
            })
        }

    except Exception as exc:
        print(traceback.format_exc())
        return traceback.format_exc()
        return {
            "statusCode": 500,
            "body": json.dumps({
                "result": traceback.format_exc()
            })
        }
