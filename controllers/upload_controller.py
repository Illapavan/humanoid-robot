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
    filename = file.name
    s3_client = boto3.client('s3')

    try:
        s3_client.upload_fileobj(file,  os.getenv("S3_BUCKET_NAME"), filename)
    except botocore.exceptions.ClientError as e:
        return jsonify({'error': str(e)})

    s3_unsigned_url = s3_client.generate_presigned_url(
        'get_object',
        Params={'Bucket': os.getenv("S3_BUCKET_NAME"), 'Key': filename},
        ExpiresIn=3600  # URL expiration time in seconds (optional)
    )

    return jsonify({'url': s3_unsigned_url})


