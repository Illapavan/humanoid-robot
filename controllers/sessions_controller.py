from flask import jsonify, request
from utils.session_util import SessionManager


session_manager = SessionManager()

def new_session():
    session_id = session_manager.create_session()
    response_data = {
        "session_id": session_id
    }

    return jsonify(response_data)


def get_chat_session():
    data = request.get_json()
    session_id = data.get("session_id")
    print(session_id)
    info = session_manager.get_session_info(session_id)
    response_data = {
        "session_info": info
    }

    return jsonify(info)

