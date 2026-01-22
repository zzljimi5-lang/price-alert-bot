from http.server import BaseHTTPRequestHandler
import json
import os
from twilio.rest import Client
import sys

class Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            print(f"Received: {data}", file=sys.stderr)
            
            ticker = data.get('ticker') or data.get('symbol', 'Unknown')
            price = data.get('price') or data.get('close', 'Unknown')
            condition = data.get('condition', 'triggered')
            
            alert_message = f"请注意，{ticker}价格已{condition}，当前价格{price}美元。"
            print(f"Alert: {alert_message}", file=sys.stderr)
            
            call_sid = self.make_call(alert_message)
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = json.dumps({"success": True, "call_sid": call_sid})
            self.wfile.write(response.encode('utf-8'))
            
        except Exception as e:
            print(f"Error: {str(e)}", file=sys.stderr)
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            error_response = json.dumps({"success": False, "error": str(e)})
            self.wfile.write(error_response.encode('utf-8'))
    
    def make_call(self, message):
        account_sid = os.environ.get('TWILIO_ACCOUNT_SID')
        auth_token = os.environ.get('TWILIO_AUTH_TOKEN')
        from_phone = os.environ.get('TWILIO_PHONE_NUMBER')
        to_phone = os.environ.get('MY_PHONE_NUMBER')
        
        print(f"Calling from {from_phone} to {to_phone}", file=sys.stderr)
        
        client = Client(account_sid, auth_token)
        call = client.calls.create(
            twiml=f'<Response><Say language="zh-CN" voice="alice">{message}</Say></Response>',
            from_=from_phone,
            to=to_phone
        )
        return call.sid

def handle(request):
    return Handler()
