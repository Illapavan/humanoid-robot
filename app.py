from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from controllers.memory_chat_controller import memory_conversational_chat, pdf_reader
from controllers.sessions_controller import new_session, flush
from controllers.image_controller import image_generator, image_variation, image_editor
from controllers.upload_controller import upload_file
from utils.stream import create_stream_token, revoke_stream_token, stream_webhook
from controllers.calendar_controller import queryOnCalendar, createCalendarevent, getCalendarSlots


app = Flask(__name__)
cors = CORS(app)

# app.route('/api/v1/memory-conversational-chat', methods=["POST"])(memory_conversational_chat)
# app.route('/api/v1/new-session', methods=["POST"])(new_session)
# app.route('/api/v1/pdf-reader', methods=["POST"])(pdf_reader)
# app.route('/api/v1/generate-image-from-text', methods=["POST"])(image_generator)
# app.route('/api/v1/generate-image-variation', methods=["POST"])(image_variation)
# app.route('/api/v1/image-editor', methods=["POST"])(image_editor)
# app.route('/api/v1/virtual-questioning', methods = ["POST"])(virtual_questioning)

app.route('/api/v1/upload', methods=["POST"])(upload_file)
app.route('/api/v1/user/token', methods=["POST"])(create_stream_token)
app.route('/api/v1/user/token/delete', methods=["POST"])(revoke_stream_token)
app.route('/api/v1/webhook', methods=["POST"])(stream_webhook)
app.route('/api/v1/queryOnCalendarEvents', methods=["POST"])(queryOnCalendar)
app.route('/api/v1/createCalendarEvent', methods=['POST'])(createCalendarevent)
app.route('/api/v1/getCalendarSlots', methods=["POST"])(getCalendarSlots)
app.route('/api/v1/flush', methods=["GET"])(flush)

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
    return jsonify({"message": "Invalid request type."})

@app.route('/.well-known/pki-validation/F9324EF74D7B474B4289563768901F62.txt', methods = ["GET"])
def httpAuthenticate():
    return send_from_directory('static', "F9324EF74D7B474B4289563768901F62.txt")


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)