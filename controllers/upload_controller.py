from flask import Flask, request, jsonify
import boto3
import botocore
from dotenv import load_dotenv
import os

load_dotenv()

def upload_file():
    if 'file' not in request.files:
        return jsonify({'error' : 'No file upload'})

    file = request.files['file']
    filename = file.filename
    s3_client = boto3.client('s3')

    try:
        s3_client.upload_fileobj(file,  os.getenv("S3_BUCKET_NAME"), filename)
    except botocore.exceptions.ClientError as e:
        return jsonify({'error': str(e)})

    s3_url = f"https://{os.getenv('S3_BUCKET_NAME')}.s3.amazonaws.com/{filename}"

    return jsonify({'url': s3_url})


