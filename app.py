from flask import Flask
from controllers.memory_chat_controller import memory_conversational_chat
from controllers.sessions_controller import new_session

app = Flask(__name__)

app.route('/api/v1/memory-conversational-chat', methods=["POST"])(memory_conversational_chat)
app.route('/api/v1/new-session', methods=["POST"])(new_session)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)