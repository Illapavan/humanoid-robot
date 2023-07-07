from stream_chat import StreamChat
import os
from controllers.image_controller import image_generator, image_variation, image_editor
from controllers.memory_chat_controller import memory_conversational_chat, pdf_reader
from controllers.sessions_controller import new_session
from flask import jsonify, request

# instantiate your stream client using the API key and secret
# the secret is only used server side and gives you full access to the API
server_client = StreamChat(api_key=os.environ.get('OPENAI_API_KEY'), api_secret=os.environ.get('OPENAI_API_KEY'))
def create_stream_token():
    data = request.get_json()
    id = data.get('id')
    try:
        return server_client.create_token(id)
    except Exception as e:
        error_response = {
            "error": "Internal Server Error",
            "message": str(e),
        }
        return jsonify(error_response), 500


# def stream_webhook(body):
#     if body is not None and body.get("type") == "message.new":
#         data = body.get("attachments")[0]
#         type = data.get('type')
#
#         if type == "chat":
#             return memory_conversational_chat(data)
#         elif type == "new_session":
#             return new_session()
#         elif type == "pdf_reader":
#             return pdf_reader(data)
#         elif type == "image_generator":
#             return image_generator(data)
#         elif type == "image_variation":
#             return image_variation(data)
#         elif type == 'image_editor':
#             return image_editor(data)
#         return jsonify({"message": "Invalid request type."})
