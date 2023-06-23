from flask import request, jsonify
import codecs
from io import BytesIO
import boto3
from utils.openai_util import ChatOpenAI
from utils.session_util import SessionManager
from PyPDF2 import PdfReader
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.chains.question_answering import load_qa_chain
from langchain.llms import OpenAI
from langchain.callbacks import get_openai_callback
from urllib.parse import urlparse

llm = ChatOpenAI(temperature=0.8)
session_manager = SessionManager()

def memory_conversational_chat():

    session_id = request.headers.get("session-id")
    conversation_memory = session_manager.get_conversation_memory(session_id)
    body = request.get_json()
    user_input = body.get("message")

    conversation_memory.append({"role": "user", "content": user_input})
    
    # Generate a response from the model using conversational memory
    response = llm.generate_response(conversation_memory, user_input)
    
    conversation_memory.append({"role": "model", "content": response})

    session_manager.update_conversation_memory(session_id, conversation_memory)
    
    response_data = {
        "response": response,
        "conversation": conversation_memory
    }
    
    return jsonify(response_data)

def pdf_reader():

    body = request.get_json()
    pdf_url = body.get("pdf_url")
    if pdf_url is not None:
        s3 = boto3.client("s3")
        bucket, key = parse_s3_url(pdf_url)

        obj = s3.get_object(Bucket=bucket, Key=key)
        fs = obj['Body'].read()
        pdf_reader = PdfReader(BytesIO(fs))
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
            
        # split into chunks
        text_splitter = CharacterTextSplitter(
            separator="\n",
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len
        )
        chunks = text_splitter.split_text(text)
        
        # create embeddings
        embeddings = OpenAIEmbeddings()
        knowledge_base = FAISS.from_texts(chunks, embeddings)
        
        # show user input
        user_question = body.get("question")
        if user_question:
            docs = knowledge_base.similarity_search(user_question)
            
            llm = OpenAI()
            chain = load_qa_chain(llm, chain_type="stuff")
            response = chain.run(input_documents=docs, question=user_question)
            response_data = {
            "response": response,
            }
            return jsonify(response_data)

def parse_s3_url(pdf_url):
    parsed_url = urlparse(pdf_url)
    bucket = parsed_url.netloc.split('.')[0]
    key = parsed_url.path.lstrip('/')

    return bucket, key
