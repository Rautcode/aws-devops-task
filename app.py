import boto3
import psycopg2
import json
import os

# AWS Configurations
S3_BUCKET = os.getenv('S3_BUCKET', 's3-data-storage-devops')
RDS_HOST = os.getenv('RDS_HOST', 'rds-endpoint')
RDS_DB = os.getenv('RDS_DB', 'devopsdb')
RDS_USER = os.getenv('RDS_USER', 'admin')
RDS_PASSWORD = os.getenv('RDS_PASSWORD', 'DevOps@1234')
GLUE_DB = os.getenv('GLUE_DB', 'devops_glue_db')

# AWS Clients
s3 = boto3.client('s3')
glue = boto3.client('glue')

def read_s3_file(bucket, key):
    """Reads a JSON file from S3 or retrieves metadata for media files."""
    response = s3.get_object(Bucket=bucket, Key=key)
    
    # Determine if file is JSON or media
    if key.endswith(".json"):
        return json.loads(response['Body'].read().decode('utf-8')), "json"
    
    return {
        "file_name": key,
        "file_size": response['ContentLength'],
        "content_type": response['ContentType'],
        "s3_url": f"s3://{bucket}/{key}"
    }, "media"

def push_to_rds(data, file_type):
    """Stores JSON data or media metadata into RDS."""
    try:
        conn = psycopg2.connect(host=RDS_HOST, database=RDS_DB, user=RDS_USER, password=RDS_PASSWORD)
        cur = conn.cursor()
        
        if file_type == "json":
            cur.execute("INSERT INTO logs (data) VALUES (%s)", (json.dumps(data),))
        else:
            cur.execute(
                "INSERT INTO media_files (file_name, file_size, content_type, s3_url) VALUES (%s, %s, %s, %s)",
                (data["file_name"], data["file_size"], data["content_type"], data["s3_url"])
            )
        
        conn.commit()
        cur.close()
        conn.close()
        return True
    except Exception as e:
        print("RDS Insertion Failed:", e)
        return False

def push_to_glue(data):
    """Stores data in S3 for Glue processing."""
    glue_key = f'glue_data/{data["file_name"] if "file_name" in data else "data"}.json'
    s3.put_object(Bucket=S3_BUCKET, Key=glue_key, Body=json.dumps(data))
    return {"status": "Data pushed to Glue via S3"}

def lambda_handler(event, context):
    """AWS Lambda function triggered by S3 uploads."""
    key = event['Records'][0]['s3']['object']['key']
    
    data, file_type = read_s3_file(S3_BUCKET, key)
    
    # Try inserting into RDS, fallback to Glue if it fails
    if not push_to_rds(data, file_type):
        push_to_glue(data)
    
    return {"statusCode": 200, "body": "File processed successfully"}
