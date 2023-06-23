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

    data = request.get_json()
    pdf = data.get("pdf")
    if pdf is not None:
        s3 = boto3.client("s3")
        obj = s3.get_object(Bucket="metropoc", Key="Setup+Docker+in+Windows.pdf")
        print(obj)
        fs = obj['Body'].read()
        pdf_reader = PdfReader(BytesIO(fs))
        # pdf_reader = PdfReader(pdf)
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
        user_question = data.get("question")
        if user_question:
            docs = knowledge_base.similarity_search(user_question)
            
            llm = OpenAI()
            chain = load_qa_chain(llm, chain_type="stuff")
            with get_openai_callback() as cb:
                response = chain.run(input_documents=docs, question=user_question)
                print(cb)
            print(response)
    