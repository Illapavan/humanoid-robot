from flask import Flask, request, jsonify
import os
from langchain.chat_models import ChatOpenAI
from chat_openai import ChatOpenAI
from session_manager import SessionManager
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)
session_manager = SessionManager()
# loading the env key

llm = ChatOpenAI(temperature=0.8)

@app.route('/api/v1/memory-conversational-chat', methods=["POST"])
def memory_conversational_chat():

    session_id = request.headers.get("session_id")
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
    

def new_session():
    session_id = session_manager.create_session()
    response_data = {
        "session_id" : session_id
    }

    return jsonify(response_data)



if __name__ == "__main__":
    app.run()