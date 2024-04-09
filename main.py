import streamlit as st
import os

from dotenv import load_dotenv
load_dotenv()

from canopy.knowledge_base import KnowledgeBase
from canopy.tokenizer import Tokenizer
from canopy.context_engine import ContextEngine
from canopy.chat_engine import ChatEngine
from canopy.models.data_models import UserMessage, SystemMessage

Tokenizer.initialize()
INDEX_NAME = "wealth-outlook"

kb = KnowledgeBase(index_name=INDEX_NAME)
kb.connect()

context_engine = ContextEngine(kb)
chat_engine = ChatEngine(context_engine,allow_model_params_override=True)

st.title("Canopy RAG for 2024 Wealth Outlook")

st.file_uploader(label="Upload your files")
st.markdown("Chat with your document below")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("What is up?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        messages = []
        for m in st.session_state.messages:
            if m['role'] == 'user':
                messages.append(UserMessage(content=m['content']))
            else:
                messages.append(SystemMessage(content=m['content']))
        
        res = chat_engine.chat(
            #messages=[UserMessage(content=st.session_state.messages[-1]['content'])],
            messages=messages,
            stream=False, 
            model_params={'model':'gpt-4-0125-preview'})
        print(res)
        response = st.write(res.choices[0].message.content)
        #stream = client.chat.completions.create(
        #    model=st.session_state["openai_model"],
        #    messages=[
        #        {"role": m["role"], "content": m["content"]}
        #        for m in st.session_state.messages
        #    ],
        #   stream=True,
        #)
        #response = st.write_stream(stream)
        
    st.session_state.messages.append({"role": "assistant", "content": res.choices[0].message.content})