import _thread as thread
import base64
import datetime
import hashlib
import hmac
import json
import ssl
import websocket
from urllib.parse import urlparse, quote
import time
import logging
from config import *

class SparkAPI:
    def __init__(self):
        """初始化星火大模型API"""
        self.answer = ""
        self.status = "idle"
        websocket.enableTrace(False)  # 禁用详细日志
        
    def _generate_url(self):
        """生成签名URL"""
        url = urlparse(SPARK_API_URL)
        host = url.netloc
        path = url.path
        
        # 生成时间戳（注意时区）
        now = datetime.datetime.utcnow()
        date = now.strftime('%a, %d %b %Y %H:%M:%S GMT')
        
        # 签名原文（注意换行符）
        signature_origin = f"host: {host}\ndate: {date}\nGET {path} HTTP/1.1"
        
        # 使用API_SECRET进行hmac-sha256签名
        signature_sha = hmac.new(
            SPARK_API_SECRET.encode('utf-8'),
            signature_origin.encode('utf-8'),
            digestmod=hashlib.sha256
        ).digest()
        
        signature_sha_base64 = base64.b64encode(signature_sha).decode('utf-8')
        
        # 组装authorization_origin（注意格式）
        authorization_origin = (
            f'api_key="{SPARK_API_KEY}", '
            f'algorithm="hmac-sha256", '
            f'headers="host date request-line", '
            f'signature="{signature_sha_base64}"'
        )
        
        # 对authorization进行base64编码
        authorization = base64.b64encode(authorization_origin.encode('utf-8')).decode('utf-8')
        
        # URL编码处理
        date = quote(date)
        host = quote(host)
        
        # 拼接最终URL
        url = f"wss://{url.netloc}{url.path}?authorization={authorization}&date={date}&host={host}"
        logging.debug(f"Generated URL: {url}")
        return url

    def _on_message(self, ws, message):
        try:
            data = json.loads(message)
            code = data["header"]["code"]
            if code != 0:
                error_msg = data.get("header", {}).get("message", "未知错误")
                logging.error(f"讯飞API返回错误: code={code}, message={error_msg}")
                self.status = "error"
                self.answer = f"API调用失败: {error_msg}"
                ws.close()
            else:
                choices = data["payload"]["choices"]
                status = choices["status"]
                content = choices["text"][0]["content"]
                self.answer += content
                if status == 2:
                    self.status = "done"
                    ws.close()
        except Exception as e:
            logging.error(f"处理消息时出错: {str(e)}")
            self.status = "error"
            self.answer = f"处理响应失败: {str(e)}"
            ws.close()

    def _on_error(self, ws, error):
        logging.error(f"WebSocket错误: {str(error)}")
        self.status = "error"
        self.answer = f"连接错误: {str(error)}"

    def _on_close(self, ws, close_status_code, close_msg):
        logging.info(f"WebSocket连接关闭: status_code={close_status_code}, msg={close_msg}")
        if self.status == "running":
            self.status = "error"
            self.answer = "连接意外关闭"

    def _on_open(self, ws):
        def run(*args):
            try:
                data = json.dumps(self.request_data)
                ws.send(data)
            except Exception as e:
                logging.error(f"发送消息时出错: {str(e)}")
                self.status = "error"
                self.answer = f"发送请求失败: {str(e)}"
                ws.close()
        thread.start_new_thread(run, ())

    def chat(self, messages):
        """发送聊天请求"""
        self.answer = ""
        self.status = "running"
        
        # 修改请求数据格式
        message_text = messages[0]["content"] if messages else ""
        self.request_data = {
            "header": {
                "app_id": SPARK_APP_ID,
                "uid": "12345"
            },
            "parameter": {
                "chat": {
                    "domain": "4.0Ultra", # 4.0Ultra 是星火大模型
                    "temperature": TEMPERATURE,
                    "max_tokens": 2048,
                    "top_k": 4
                }
            },
            "payload": {
                "message": {
                    "text": [
                        {
                            "role": "user",
                            "content": message_text
                        }
                    ]
                }
            }
        }
        
        try:
            # 创建WebSocket连接
            url = self._generate_url()
            logging.info(f"Connecting to: {url}")
            logging.info(f"Request data: {json.dumps(self.request_data, ensure_ascii=False)}")
            
            ws = websocket.WebSocketApp(
                url,
                on_message=self._on_message,
                on_error=self._on_error,
                on_close=self._on_close,
                on_open=self._on_open
            )
            
            # 启动WebSocket连接
            ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})
            
            # 等待响应
            timeout = 30  # 30秒超时
            start_time = time.time()
            while self.status == "running":
                if time.time() - start_time > timeout:
                    self.status = "error"
                    self.answer = "请求超时"
                    break
                time.sleep(0.1)
            
            if self.status == "error" and not self.answer:
                self.answer = "请求失败，请检查网络连接和API配置"
            
            return self.answer
            
        except Exception as e:
            logging.error(f"创建连接时出错: {str(e)}")
            return f"连接失败: {str(e)}"
