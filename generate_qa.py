import os
import json
import sys
from spark_llm import SparkAPI
from config import *
# 加载环境变量
# 初始化 Spark 客户端
client = SparkAPI()

def read_txt_file(file_path):
    print(f"Reading input file: {file_path}")
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

def split_text(text, chunk_size=2000):
    print(f"Splitting text into chunks of {chunk_size} characters each.")
    return [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]

def call_spark_api(text_chunk):
    prompt = (
        "你是一个信息抽取能手，你需要把我给你的内容做成QA对，模拟人和大模型的对话，你的回复要满足下列要求：\n"
        "全部使用中文回复\n"
        "你会将内容识别为起卦方法，卦象分析，体用关系及断卦逻辑，对起卦方法的提问核心在从求卦人信息、具体数字处理规则，解卦结合等方面生成问题和答案，着重体现报数法的核心流程,对卦象分析的提问核心在基于X卦的卦象特点，其在各类象征意义上的体现以及方位、数字、时间等属性，对体用关系及断卦逻辑的提问核心在依据断卦的步骤顺序，从卦的分类处理、体用关系分析、外应考量、应验期确定等环节，完整呈现断卦方法的逻辑架构\n"
        "提取重点注重在卜卦的流程上\n"
        "根据内容的分类与系统返回QA对，不漏掉任何一条符合起卦方法，卦象分析，体用关系和断卦逻辑的内容，假如字数超过可以发送的最大值，可以对A和Q进行简化\n"
        "system字段统一设置为：你是精通梅花易数的大师，你首先使用起卦方法，然后经过计算得到卦象，最后使用卦象分析为用户进行预测\n"
        "我给你的材料可能有错误，你要在基于上下文理解的基础上帮忙修复\n"
        "不要提到任何作者信息和前言后传，你只需要提取能够构建起卜卦体系的问答\n"
        "回复格式示例：[\n"
        "    {\n"
        "        \"instruction\": \"问题1\",\n"
        "        \"output\": \"答案1\",\n"
        "        \"system\": \"你是精通梅花易数的大师，你首先使用起卦方法，然后经过计算得到卦象，最后使用卦象分析为用户进行预测\"\n"
        "    }\n"
        "]"
    )
    print(f"Calling Spark API with text chunk: {text_chunk[:50]}...")  # 只显示前50个字符
    response = client.chat(messages=[{"role": "user", "content": text_chunk}])
    full_text = response
    print(f"Received response: {full_text[:50]}...")  # 只显示前50个字符
    return full_text

def save_text_chunks(chunks, output_folder):
    """保存文本切片到文件"""
    chunks_folder = os.path.join(output_folder, 'text_chunks')
    if not os.path.exists(chunks_folder):
        os.makedirs(chunks_folder)
    
    chunk_files = []
    for i, chunk in enumerate(chunks):
        chunk_file = os.path.join(chunks_folder, f'chunk_{i + 1}.txt')
        with open(chunk_file, 'w', encoding='utf-8') as f:
            f.write(chunk)
        chunk_files.append(chunk_file)
        full_text += text
    print(f"Received response: {full_text[:50]}...")  # 只显示前50个字符
    return full_text

def save_text_chunks(chunks, output_folder):
    """保存文本切片到文件"""
    chunks_folder = os.path.join(output_folder, 'text_chunks')
    if not os.path.exists(chunks_folder):
        os.makedirs(chunks_folder)
    
    chunk_files = []
    for i, chunk in enumerate(chunks):
        chunk_file = os.path.join(chunks_folder, f'chunk_{i + 1}.txt')
        with open(chunk_file, 'w', encoding='utf-8') as f:
            f.write(chunk)
        chunk_files.append(chunk_file)
    return chunk_files

def generate_qa_pairs(input_file, output_folder, start_index=0):
    """
    生成QA对，可以指定开始处理的切片索引
    :param input_file: 输入文件路径
    :param output_folder: 输出文件夹路径
    :param start_index: 开始处理的切片索引（从0开始）
    """
    # 读取和切割文本
    text = read_txt_file(input_file)
    text_chunks = split_text(text)
    total_chunks = len(text_chunks)
    
    # 保存文本切片
    print("Saving text chunks...")
    save_text_chunks(text_chunks, output_folder)
    
    # 处理每个文本块，从指定索引开始
    for i, chunk_text in enumerate(text_chunks[start_index:], start=start_index):
        print(f"Processing chunk {i + 1}/{total_chunks}...")
        
        # 调用API生成QA对
        qa_pair = call_spark_api(chunk_text)
        
        # 解析返回的JSON字符串并保存
        try:
            qa_list = json.loads(qa_pair) if isinstance(qa_pair, str) else qa_pair
            output_file = os.path.join(output_folder, f'success{i + 1}.json')
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(qa_list, f, ensure_ascii=False, indent=4)
            print(f"Chunk {i + 1}/{total_chunks} processed and saved to '{output_file}'.")
        except json.JSONDecodeError as e:
            print(f"Error processing chunk {i + 1}: {e}")
            print(f"Raw response: {qa_pair}")
            continue

    print("QA pairs generation completed.")

if __name__ == "__main__":
    if len(sys.argv) != 3 and len(sys.argv) != 4:
        print("Usage: python generate_qa.py <input_file> <output_folder> [<start_index>]")
        sys.exit(1)

    input_file = sys.argv[1]
    output_folder = sys.argv[2]
    start_index = int(sys.argv[3]) if len(sys.argv) == 4 else 0
    generate_qa_pairs(input_file, output_folder, start_index)
