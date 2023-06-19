import redis
import uuid
import json

class SessionManager:
    def __init__(self):
        self.redis_client = redis.Redis(host="redis", port=6379, db=0)

    def create_session(self):
        session_id = str(uuid.uuid4())
        self.redis_client.set(session_id, "")
        return session_id

    def get_conversation_memory(self, session_id):
        conversation_memory = self.redis_client.get(session_id)
        if conversation_memory:
            return json.loads(conversation_memory)
        else:
            return []

    def update_conversation_memory(self, session_id, conversation_memory):
        self.redis_client.set(session_id, json.dumps(conversation_memory))
