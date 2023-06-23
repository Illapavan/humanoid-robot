from flask import Flask
from flask_cors import CORS
from controllers.memory_chat_controller import memory_conversational_chat, pdf_reader
from controllers.sessions_controller import new_session
from controllers.image_controller import image_generator, image_variation, image_editor

app = Flask(__name__)
cors = CORS(app)

app.route('/api/v1/memory-conversational-chat', methods=["POST"])(memory_conversational_chat)
app.route('/api/v1/new-session', methods=["POST"])(new_session)
app.route('/api/v1/pdf-reader', methods=["POST"])(pdf_reader)
app.route('/api/v1/generate-image-from-text', methods=["POST"])(image_generator)
app.route('/api/v1/generate-image-variation', methods=["POST"])(image_variation)
app.route('/api/v1/image-editor', methods=["POST"])(image_editor)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)