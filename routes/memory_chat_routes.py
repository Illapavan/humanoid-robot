from flask import request, jsonify
from utils.chat_openai import ChatOpenAI
from utils.session_manager import SessionManager

llm = ChatOpenAI(temperature=0.8)
session_manager = SessionManager()

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