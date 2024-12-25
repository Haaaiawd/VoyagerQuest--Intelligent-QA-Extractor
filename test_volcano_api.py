import os
import unittest
import dotenv
from spark_llm import SparkAPI
from config import SPARK_API_KEY

# 加载环境变量
dotenv.load_dotenv(".env")

# 初始化 Spark 客户端
client = SparkAPI()

class TestSparkAPI(unittest.TestCase):

    def test_call_spark_api(self):
        prompt = "你是豆包，是由字节跳动开发的 AI 人工智能助手"
        response = client.chat(messages=[{"role": "user", "content": "这是一个测试文本。"}])
        self.assertTrue(len(response) > 0)

if __name__ == "__main__":
    unittest.main()
