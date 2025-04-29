# lambda/index.py
import json
import urllib.request

FASTAPI_URL = "https://6c4b-34-143-214-180.ngrok-free.app/"

def lambda_handler(event, context):
    try:
        print("Received event:", json.dumps(event))
        
        # リクエストボディの解析
    　　body = json.loads(event.get('body', '{}'))
   　　 message = body.get('message', '')
        
        # FastAPIに送る形式
        request_payload = {
  "prompt": message,
  "max_new_tokens": 512,
  "do_sample": True,
  "temperature": 0.7,
  "top_p": 0.9
}
    
        # POST リクエストを作成
        req = urllib.request.Request(
            url=FASTAPI_URL,
            data=json.dumps(request_payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST"
        )

        # FastAPI に送信しレスポンスを取得
        with urllib.request.urlopen(req) as res:
            response_data = json.loads(res.read().decode("utf-8"))

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
