from flask import Flask, request
from flask_cors import CORS
from controllers.memory_chat_controller import memory_conversational_chat, pdf_reader
from controllers.sessions_controller import new_session
from controllers.image_controller import image_generator, image_variation, image_editor

app = Flask(__name__)
cors = CORS(app)

# app.route('/api/v1/memory-conversational-chat', methods=["POST"])(memory_conversational_chat)
# app.route('/api/v1/new-session', methods=["POST"])(new_session)
# app.route('/api/v1/pdf-reader', methods=["POST"])(pdf_reader)
# app.route('/api/v1/generate-image-from-text', methods=["POST"])(image_generator)
# app.route('/api/v1/generate-image-variation', methods=["POST"])(image_variation)
# app.route('/api/v1/image-editor', methods=["POST"])(image_editor)

@app.route('/api/v1/assistant', methods = ["POST"])
def handle_assistant():
    data = request.get_json()
    type = data.get('type')

    if type == "chat":
        return memory_conversational_chat(data)
    elif type == "new_session":
        return new_session()    
    elif type == "pdf_reader":
        return pdf_reader(data) 
    elif type == "image_generator":
        return image_generator(data)    
    elif type == "image_variation":
        return image_variation(data)
    elif type == 'image_editor':
        return image_editor(data)
        
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)