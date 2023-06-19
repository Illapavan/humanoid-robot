from flask import request, jsonify
import requests
from dotenv import load_dotenv
import os
import openai

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

def generate_dalle2_image(text_prompt):
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=text_prompt,
        temperature=0,
        max_tokens=64,
    )

    generated_image = response.choices[0].text.strip()

    image_url = extract_image_url(generated_image)

    return image_url



def image_generator():
    body = request.get_json()
    text_prompt = body.get("text_prompt")

    generated_image = generate_dalle2_image(text_prompt)
    response = {
        "generated_image": generated_image
    }

    return jsonify(response)


def extract_image_url(generated_image):
    # Parse the generated image to extract the image URL
    start_index = generated_image.find("(") + 1
    end_index = generated_image.find(")")
    image_url = generated_image[start_index:end_index]

    return image_url

