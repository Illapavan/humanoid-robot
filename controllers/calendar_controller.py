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
from flask import jsonify

load_dotenv()

def getCalendarEvents():
    loader = GoogleCalendarReader()
    print("check 1")
    documents = loader.load_data(start_date=date.today(), number_of_results=50)
    print("check 2")
    formatted_documents: List[LCDocument] = [doc.to_langchain_format() for doc in documents]
    print(formatted_documents)
    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
    documents = text_splitter.split_documents(formatted_documents)
    embeddings = OpenAIEmbeddings()
    vector_store = Chroma.from_documents(documents, embeddings)
    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

    qa = ConversationalRetrievalChain.from_llm(OpenAI(temperature=0, model_name="gpt-4"), vector_store.as_retriever(), memory=memory)
    query = "Can i have a metting scheduled on : 2023-07-07 from 6:30 to 7:00 pm"
    result = qa({"question": query})

    answer = result['answer']
    response_data = {
        "response" : answer
    }
    return jsonify(response_data)
   
