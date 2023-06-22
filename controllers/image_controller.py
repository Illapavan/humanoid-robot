from flask import request, jsonify
import requests
from dotenv import load_dotenv
import os
import openai

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

def generate_dalle2_image(text_prompt):
    response = openai.Image.create(prompt=text_prompt, n=3, size="256x256")
    return response["data"]




def image_generator():
    body = request.get_json()
    text_prompt = body.get("text_prompt")

    generated_image = generate_dalle2_image(text_prompt)
    response = {
        "generated_image": generated_image
    }

    return jsonify(response)



