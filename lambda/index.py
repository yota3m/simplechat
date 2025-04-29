# lambda/index.py
import json
import os
import boto3
import urllib.request
import re  # 正規表現モジュールをインポート
from botocore.exceptions import ClientErrorimport json

# Lambda コンテキストからリージョンを抽出する関数
def extract_region_from_arn(arn):
    # ARN 形式: arn:aws:lambda:region:account-id:function:function-name
    match = re.search('arn:aws:lambda:([^:]+):', arn)
    if match:
        return match.group(1)
    return "us-east-1"  # デフォルト値
    
# グローバル変数としてクライアントを初期化（初期値）
bedrock_client = None

# モデルID
MODEL_ID = os.environ.get("MODEL_ID", "us.amazon.nova-lite-v1:0")

FASTAPI_URL = "https://6c4b-34-143-214-180.ngrok-free.app/generate"

def lambda_handler(event, context):
    try:
        # コンテキストから実行リージョンを取得し、クライアントを初期化
        global bedrock_client
        if bedrock_client is None:
            region = extract_region_from_arn(context.invoked_function_arn)
            bedrock_client = boto3.client('bedrock-runtime', region_name=region)
            print(f"Initialized Bedrock client in region: {region}")
        
        print("Received event:", json.dumps(event))
        
        # Cognitoで認証されたユーザー情報を取得
        user_info = None
        if 'requestContext' in event and 'authorizer' in event['requestContext']:
            user_info = event['requestContext']['authorizer']['claims']
            print(f"Authenticated user: {user_info.get('email') or user_info.get('cognito:username')}")
        
        # リクエストボディの解析
        body = json.loads(event['body'])
        message = body['message']
        conversation_history = body.get('conversationHistory', [])
        
        print("Processing message:", message)
        print("Using model:", MODEL_ID)
        
        # FastAPIに送る形式
        request_payload = {
            "prompt": message,
            "max_new_tokens": 512,
            "do_sample": true,
            "temperature": 0.7,
            "top_p": 0.9
        }
    
        # POST リクエストを作成
        req = urllib.request.Request(
            url=FASTAPI_URL,
            data=json.dumps(request_payload).encode('utf-8'), 
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        
        # FastAPI に送信しレスポンスを取得
        with urllib.request.urlopen(req) as resp:
            response_data = json.loads(resp.read().decode("utf-8"))

        # 応答からテキストを抽出
        assistant_response = response_data.get("generated_text")

        # 成功レスポンスの返却
        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token",
                "Access-Control-Allow-Methods": "OPTIONS,POST"
            },
            "body": json.dumps({
                "success": True,
                "response": assistant_response,
            })
        }
        
    except Exception as error:
        print("Error:", str(error))
        
        return {
            "statusCode": 500,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token",
                "Access-Control-Allow-Methods": "OPTIONS,POST"
            },
            "body": json.dumps({
                "success": False,
                "error": str(error)
            })
        }
