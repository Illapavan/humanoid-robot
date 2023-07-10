import datetime
import uuid

from stream_chat import StreamChat
import os
from controllers.image_controller import image_generator, image_variation, image_editor
from controllers.memory_chat_controller import memory_conversational_chat, pdf_reader
from controllers.sessions_controller import new_session
from flask import jsonify, request

# instantiate your stream client using the API key and secret
# the secret is only used server side and gives you full access to the API
server_client = StreamChat(api_key=os.environ.get('STREAM_API_KEY'), api_secret=os.environ.get('STREAM_API_SECRET_ID'))
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
        channelObject = server_client.query_channels({"cid": body.get("cid")}, limit=1)
        if channelObject is None or channelObject.get("channels") is None or len(channelObject.get("channels")) != 1 or \
                len(channelObject.get("channels")[0].get("members")) != 0:
            print("Invalid channel for adding bot")
            print(channelObject)
            return

        bot_id = "bot" + str(uuid.uuid4())
        server_client.upsert_user({
            "id": bot_id,
            "name": "Companion Bot #" + bot_id,
        })
        channel = server_client.channel(body.get("channel").get("type"), body.get("channel").get("id"))
        if channel is None:
            return
        channel.create(body.get("channel").get("created_by").get("id"))
        channel.add_members([bot_id], {"text": 'Companion has joined the channel.', "user_id": bot_id})
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
        print("Exception caught while sending bot message to channel with id - " + channel_id)
        print(e)

def message_handler(body):
    data = body.get("message").get("attachments")[0]
    data_type = data.get('data_type')
    channel_type = body.get("channel_type")
    channel_id = body.get("channel_id")

    try:
        if body.get("user") is None or "client" not in body.get("user").get("id") or len(body.get("members")) == 0:
            return

        bot_member_id = next((member for member in body.get("members") if "bot" in member.get("user_id")), None)
        if bot_member_id is None:
            return

        if data_type == "chat":
            response = memory_conversational_chat(data)
            send_message(channel_type, channel_id, bot_member_id, response.get("response"))
        elif data_type == "pdf_reader":
            response = pdf_reader(data)
            send_message(channel_type, channel_id, bot_member_id, response.get("response"))
        elif data_type == "image_generator":
            response = image_generator(data)
            send_message(channel_type, channel_id, bot_member_id, response.get("response"))
        elif data_type == "image_variation":
            response = image_variation(data)
            send_message(channel_type, channel_id, bot_member_id, response.get("response"))
        elif data_type == 'image_editor':
            response = image_editor(data)
            send_message(channel_type, channel_id, bot_member_id, response.get("response"))
    except Exception as e:
        print("Exception caught while generating bot message to channel")
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
        message_handler(body)

    return jsonify(success_response), 200
