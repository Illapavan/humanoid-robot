from dotenv import load_dotenv
from datetime import date
from typing import List
from langchain.docstore.document import Document as LCDocument
from langchain import OpenAI
from langchain.chains import ConversationalRetrievalChain
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.text_splitter import CharacterTextSplitter
from langchain.memory import ConversationBufferMemory
from utils.calendar_utils import GoogleCalendarReader
from flask import jsonify, request

load_dotenv()
loader = GoogleCalendarReader()

def queryOnCalendar(data):
    documents = loader.load_data(start_date=date.today(), number_of_results=50)
    formatted_documents: List[LCDocument] = [doc.to_langchain_format() for doc in documents]
    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
    documents = text_splitter.split_documents(formatted_documents)
    embeddings = OpenAIEmbeddings()
    vector_store = Chroma.from_documents(documents, embeddings)
    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

    qa = ConversationalRetrievalChain.from_llm(OpenAI(temperature=0, model_name="gpt-4"), vector_store.as_retriever(), memory=memory)
    query = data.get("question")
    result = qa({"question": query})

    answer = result['answer']
    response_data = {
        "response" : answer
    }
    return response_data

# def getCalendarData():
#     loader = GoogleCalendarReader()
#     documents = loader.load_data(start_date=date.today(), number_of_results=50)

def createCalendarevent(data):
    response = loader.createCalendarEvent(data)
    return response

def getCalendarSlots():
    # duration = data.get('duration')
    duration = 30
    response = loader.getCalendarSlots(duration)
    return response    


