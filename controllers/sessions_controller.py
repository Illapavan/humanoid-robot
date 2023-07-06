from flask import jsonify
from utils.session_util import SessionManager


session_manager = SessionManager()

def new_session():
    session_id = session_manager.create_session()
    response_data = {
        "session_id": session_id
    }

    return jsonify(response_data)