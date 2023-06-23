from flask import Flask
from controllers.memory_chat_controller import memory_conversational_chat
from controllers.sessions_controller import new_session
from controllers.image_controller import image_generator, image_variation, image_editor

app = Flask(__name__)

app.route('/api/v1/memory-conversational-chat', methods=["POST"])(memory_conversational_chat)
app.route('/api/v1/new-session', methods=["POST"])(new_session)
app.route('/api/v1/generate-image-from-text', methods=["POST"])(image_generator)
app.route('/api/v1/generate-image-variation', methods=["POST"])(image_variation)
app.route('/api/v1/image-editor', methods=["POST"])(image_editor)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)