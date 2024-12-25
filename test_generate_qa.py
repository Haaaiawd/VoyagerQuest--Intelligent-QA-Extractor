import unittest
from generate_qa import read_txt_file, split_text, call_spark_api, generate_qa_pairs
import config

class TestGenerateQA(unittest.TestCase):

    def test_read_txt_file(self):
        text = read_txt_file('sample.txt')
        self.assertTrue(len(text) > 0)

    def test_split_text(self):
        text = "a" * 5000
        chunks = split_text(text)
        self.assertEqual(len(chunks), 3)
        self.assertEqual(len(chunks[0]), 2000)
        self.assertEqual(len(chunks[1]), 2000)
        self.assertEqual(len(chunks[2]), 1000)

    def test_call_spark_api(self):
        response = call_spark_api("这是一个测试文本。", config.API_KEY)
        self.assertTrue(len(response) > 0)

    def test_generate_qa_pairs(self):
        generate_qa_pairs('sample.txt', 'qa_pairs.json')
        with open('qa_pairs.json', 'r', encoding='utf-8') as file:
            qa_pairs = json.load(file)
        self.assertTrue(len(qa_pairs) > 0)

if __name__ == "__main__":
    unittest.main()
