from flask import jsonify, request
from utils.session_util import SessionManager


session_manager = SessionManager()

def new_session():
    session_id = session_manager.create_session()
    response_data = {
        "session_id": session_id
    }

    return jsonify(response_data)


def getSessionInfo():
    data = request.get_json()
    session_id = data.get("session_id")
    response = session_manager.getSessionStorage(session_id)
    response_data = {
        "response": response
    }
    return jsonify(response)