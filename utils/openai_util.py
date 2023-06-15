import openai
import os

class ChatOpenAI:
    def __init__(self, temperature=0.8, max_tokens=50):
        self.api_key = os.environ.get('OPENAI_API_KEY')
        self.temperature = temperature
        self.max_tokens = max_tokens

    def generate_response(self, conversation, question):
        openai.api_key = os.environ.get('OPENAI_API_KEY')
        prompt = self._format_conversation(conversation)
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=prompt,
            max_tokens=self.max_tokens,
            temperature=self.temperature,
        )
        answer = response.choices[0].text.strip()
        return answer

    def _format_conversation(self, conversation):
        formatted_conversation = ""
        for message in conversation:
            role = message["role"]
            content = message["content"]
            formatted_conversation += f"{role}: {content}\n"
        return formatted_conversation