import json
import urllib.request

FASTAPI_URL = "https://6c4b-34-143-214-180.ngrok-free.app/generate"

def lambda_handler(event, context):
    try:
        # リクエストボディの解析
        body = json.loads(event["body"])
        message = body["message"]
        
        # FastAPIに送る形式
        request_payload = {
            "prompt": message,
            "max_new_tokens": 512,
            "do_sample": True,
            "temperature": 0.7,
            "top_p": 0.9
        }
    
        # JSONにシリアライズしてからエンコード
        request_data = json.dumps(request_payload).encode("utf-8")
    
        # POST リクエストを作成
        req = urllib.request.Request(
            url=FASTAPI_URL,
            data=request_data,
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        
        # FastAPI に送信しレスポンスを取得
        with urllib.request.urlopen(req) as resp:
            response_data = json.loads(resp.read().decode("utf-8"))

        # 応答からテキストを抽出
        assistant_response = response_data["generated_text"]

        # レスポンス返却
        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({
                "success": True,
                "response": assistant_response
            })
        }

    except Exception as e:
        # エラーハンドリング
        return {
            "statusCode": 500,
            "body": json.dumps({"success": False, "error": str(e)})
        }
