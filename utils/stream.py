import datetime

from stream_chat import StreamChat
import os
from controllers.image_controller import image_generator, image_variation, image_editor
from controllers.memory_chat_controller import memory_conversational_chat, pdf_reader
from controllers.sessions_controller import new_session
from flask import jsonify, request

# instantiate your stream client using the API key and secret
# the secret is only used server side and gives you full access to the API
server_client = StreamChat(api_key=os.environ.get('OPENAI_API_KEY'), api_secret=os.environ.get('OPENAI_API_KEY'))
success_response = {
    "success": "true"
}


def create_stream_token():
    data = request.get_json()
    id = data.get('id')
    try:
        token = {
            "token": server_client.create_token(id, exp=None, iat=datetime.datetime.utcnow()),
        }
        return jsonify(token), 200
    except Exception as e:
        error_response = {
            "error": "Internal Server Error",
            "message": str(e),
        }
        return jsonify(error_response), 500


def revoke_stream_token():
    data = request.get_json()
    users = data.get('users')
    try:
        server_client.revoke_users_token(users, datetime.datetime.utcnow())
        return jsonify(success_response), 200
    except Exception as e:
        error_response = {
            "error": "Internal Server Error",
            "message": str(e),
        }
        return jsonify(error_response), 500


def add_bot_to_channel(body):
    print("Adding bot")
    if body.get("cid") is None:
        return

    try:
        channels = server_client.query_channels({"cid": body.get("cid")}, limit=1)
        if channels is None or len(channels) != 1 or len(channels[0].get("members")) != 1 or channels[0].get("members")[
            0].get("name") == "bot":
            print("Invalid channel for adding bot")
            print(channels)
            return

        channel = server_client.channel(body.get("channel").get("type"), body.get("channel").get("id"))
        if channel is None:
            return
        channel.create(body.get("created_by").get("id"))
        channel.add_members(["bot1"], {"text": 'Companion has joined the channel.', "user_id": 'bot1'})
        print("Bot added")
    except Exception as e:
        print("Exception caught while adding bot to channel")
        print(e)


def send_message(channel_type, channel_id, user_id, message):
    try:
        channel = server_client.channel(channel_type, channel_id)
        if channel is None:
            return
        channel.create(user_id)
        channel.send_message({"text": message}, user_id)
    except Exception as e:
        print("Exception caught while sending bot message to channel to channel id - " + channel_id)
        print(e)


def stream_webhook():
    print("Webhook received")
    body = request.get_json()
    print(body)
    if body is None:
        return jsonify(success_response), 200

    if body.get("type") == "channel.created":
        add_bot_to_channel(body)
    elif body.get("type") == "message.new":
        data = body.get("message")
        data_type = data.get("attachments")[0].get('data_type')

        if data_type == "chat":
            response = memory_conversational_chat(data.get("attachments")[0])
            send_message(body.get("channel_type"), body.get("channel_id"), "bot1", response.get("response"))
        # elif type == "new_session":
        #
        # elif type == "pdf_reader":
        #     return pdf_reader(data)
        # elif type == "image_generator":
        #     return image_generator(data)
        # elif type == "image_variation":
        #     return image_variation(data)
        # elif type == 'image_editor':
        #     return image_editor(data)

    return jsonify(success_response), 200
