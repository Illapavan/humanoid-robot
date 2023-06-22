import redis
import uuid
import json
from langchain.memory.chat_message_histories import RedisChatMessageHistory

class SessionManager:
    def __init__(self):
        self.redis_client = redis.Redis(host="localhost", port=6379, db=0)

    def create_session(self):
        session_id = str(uuid.uuid4())
        self.redis_client.set(session_id, "")
        return session_id

    def get_conversation_memory(self, session_id):
        message_history_data = self.redis_client.get(session_id)
        if message_history_data is not None:
            message_history_data = message_history_data.decode("utf-8")  # Decode bytes to str
            message_history = RedisChatMessageHistory(message_history_data)
            return message_history
        else:
            return RedisChatMessageHistory(session_id=session_id)


