from flask import Flask
from routes.memory_chat_routes import memory_conversational_chat
from routes.session_routes import new_session

app = Flask(__name__)

app.route('/api/v1/memory-conversational-chat', methods=["POST"])(memory_conversational_chat)
app.route('/api/v1/new-session', methods=["POST"])(new_session)

if __name__ == "__main__":
    app.run()