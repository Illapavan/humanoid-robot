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


def image_editor():
    body = request.get_json()
    image_url = body.get("image")
    current_image = requests.get(image_url)    

    # variation here 

    variation_response = openai.Image.create_variation(
    image=current_image,  
    n=2,
    size="1024x1024",
    response_format="url",
    )
    print(variation_response)




