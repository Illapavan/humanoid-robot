from flask import request, jsonify, abort
import requests
from dotenv import load_dotenv
from PIL import Image 
import os
import io
import openai
# from transformers import pipeline
from io import BytesIO

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

def generate_dalle2_image(text_prompt):
    response = openai.Image.create(prompt=text_prompt, n=3, size="1024x1024")
    return response["data"]


def image_generator(body):
    # body = request.get_json()
    text_prompt = body.get("text_prompt")
    if text_prompt is None:
        abort(400, "Bad Request: Input can't be empty")   

    try: 
        generated_image = generate_dalle2_image(text_prompt)
        response = {
            "generated_image": generated_image
        }

        return jsonify(response)
    except Exception as e:
        abort(500, f"Internal Server Error: Failed to generate image ({str(e)})")    


def image_variation(body):
    try:
        # body = request.get_json()
        image_url = body.get("image_url")
        if image_url is None:
            abort(400, "Bad Request: Input can't be empty")

        try:
            image_response = requests.get(image_url)
            image_response.raise_for_status()
        except requests.exceptions.RequestException as e:
            abort(400, f"Bad Request: Failed to fetch the image ({str(e)})")

        image_content = image_response.content
        try:
            image = Image.open(io.BytesIO(image_content))
            image = image.convert("RGB")

            max_size = (1024, 1024)
            if image.size[0] > max_size[0] or image.size[1] > max_size[1]:
                image.thumbnail(max_size)

            image_byte_array = io.BytesIO()
            image.save(image_byte_array, format="PNG")
            image_content_resized = image_byte_array.getvalue()

            try:
                variation_response = openai.Image.create_variation(
                    image=image_content_resized,
                    n=2,
                    size="1024x1024",
                    response_format="url"
                )
                updated_image_url = variation_response["data"][0]
                return jsonify(updated_image_url)
            except openai.Error as e:
                abort(500, f"Internal Server Error: Failed to process image variation ({str(e)})")
        except IOError as e:
            abort(400, f"Bad Request: Failed to open or process the image ({str(e)})")
    except Exception as e:
        abort(500, f"Internal Server Error: {str(e)}")
    

def generate_mask(width, height):
    mask = Image.new("RGBA", (width, height), (0, 0, 0, 1))  # Create an opaque image mask

    for x in range(width):
        for y in range(height//2, height):  # Only loop over the bottom half of the mask
            mask.putpixel((x, y), (0, 0, 0, 0))

    masked_image_data = io.BytesIO()
    mask.save(masked_image_data, format="PNG")

    return masked_image_data.getvalue()


def image_editor(body):
    # body = request.get_json()
    image_url = body.get("image_url")
    text = body.get("text")

    if image_url is None or text is None:
        abort(400, "Bad Request - image_url or text is missing")

    response = requests.get(image_url)
    image_data = response.content
    if len(image_data) > 4 * 1024 * 1024:
        # Reduce the image size if it exceeds 4MB
        image = Image.open(io.BytesIO(image_data))
        image.thumbnail((1024, 1024))  # Resize the image to fit within the specified dimensions
        image_data = io.BytesIO()
        image.save(image_data, format="PNG")
        image_data.seek(0)
    image = Image.open(io.BytesIO(response.content))
    with Image.open(BytesIO(image_data)) as img:
        width, height = img.size


    available_sizes = ['256x256', '512x512', '1024x1024']
    closest_size = min(available_sizes, key=lambda s: abs(width - int(s.split('x')[0])) + abs(height - int(s.split('x')[1])))
    closest_width, closest_height = map(int, closest_size.split('x'))
    get_mask = generate_mask(closest_width, closest_height)

    if width != closest_width or height != closest_height:
        # Resize the image to the closest available size
        image = image.resize((closest_width, closest_height), Image.ANTIALIAS)
        image_data = io.BytesIO()
        image.save(image_data, format="PNG")
        image_data.seek(0)

    edit_response = openai.Image.create_edit(
        image=image_data,
        mask=get_mask,
        prompt=text,
        n=1,
        size=f"{closest_width}x{closest_height}",  # Use the closest available size
        response_format="url"
    )

    updated_image_url = edit_response["data"][0]
    return jsonify(updated_image_url)

     
# def virtual_questioning(data):
#     # data = request.get_json()
#     url = data.get("image_url")
#     question = data.get("question")

#     if url is None or question is None:
#         abort(400, "Bad : Request - image_url or question is missing")

#     image = Image.open(requests.get(url, stream=True).raw)
#     vqa_pipeline = pipeline("visual-question-answering")
#     responseData = vqa_pipeline(image, question, top_k=1)
#     response = responseData[0]['answer']
#     response = {
#         "response" : response
#     }
#     return jsonify(response)
