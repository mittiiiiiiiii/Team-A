import streamlit as st
import openai
from llama_index.llms.openai import OpenAI
try:
  from llama_index import VectorStoreIndex, ServiceContext, Document, SimpleDirectoryReader
except ImportError:
  from llama_index.core import VectorStoreIndex, ServiceContext, Document, SimpleDirectoryReader

st.set_page_config(page_title="Chat with the Streamlit docs, powered by LlamaIndex", page_icon="🦙", layout="centered", initial_sidebar_state="auto", menu_items=None)
         
if "messages" not in st.session_state.keys():
    st.session_state.messages = [
        {"role": "assistant", "content": "こんにちは！動物の勝ち負けゲームの専門家です。何か質問があればどうぞ！"},
    ]

@st.cache_resource(show_spinner=False)
def load_data():
    with st.spinner(text="Loading and indexing the Streamlit docs – hang tight! This should take 1-2 minutes."):
        reader = SimpleDirectoryReader("data")
        docs = reader.load_data()
        
        llm = OpenAI(model="gpt-4", temperature=0.0, system_prompt="あなたは、日本語が達者であり、必ず日本語で質問い回答する。動物の勝ち負けゲームの専門家です。")
        index = VectorStoreIndex.from_documents(docs)
        return index
    
index = load_data()
 
if "chat_engine" not in st.session_state.keys():
        st.session_state.chat_engine = index.as_chat_engine(chat_mode="context", verbose=True)
if prompt := st.chat_input("Your question"):
    st.session_state.messages.append({"role": "user", "content": prompt})

# ユーザーからのメッセージとアシスタントからのメッセージを交互に表示
for message in st.session_state.messages: 
    with st.chat_message(message["role"]):
        st.write(message["content"])

if st.session_state.messages[-1]["role"] != "assistant":
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = st.session_state.chat_engine.chat(prompt+ "ぜひ日本語でお答えください")
            st.write(response.response)
            message = {"role": "assistant", "content": response.response}
            st.session_state.messages.append(message) 