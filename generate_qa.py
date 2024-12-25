import os
import json
import sys
import logging
from spark_llm import SparkAPI
from config import *

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 初始化 Spark 客户端
client = SparkAPI()

def read_txt_file(file_path):
    """读取文本文件"""
    try:
        logger.info(f"Reading input file: {file_path}")
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except Exception as e:
        logger.error(f"Error reading file {file_path}: {e}")
        raise

def split_text(text, chunk_size=2000):
    """将文本分割成指定大小的块"""
    logger.info(f"Splitting text into chunks of {chunk_size} characters each.")
    return [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]

def call_spark_api(text_chunk):
    """调用星火API生成QA对"""
    prompt = (
        "你是一个信息抽取能手，你需要把我给你的内容做成QA对，模拟人和大模型的对话。你必须严格按照以下JSON格式返回：\n"
        "[\n"
        "    {\n"
        "        \"instruction\": \"问题1\",\n"
        "        \"output\": \"答案1\",\n"
        "        \"system\": \"你是精通梅花易数大师，面对用户的需求，首先分析应该采用的起卦方法，其次根据计算得出相应的卦象，最后根据卦象分析输出对用户的预测和建议\"\n"
        "    }\n"
        "]\n\n"
        "要求：\n"
        "1. 全部使用中文回复\n"
        "2. 内容分类：\n"
        "   - 起卦方法：求卦人信息、数字处理规则、解卦结合\n"
        "   - 卦象分析：卦象特点、象征意义、方位/数字/时间属性\n"
        "   - 体用关系和断卦逻辑：分类处理、关系分析、外应考量、应验期\n"
        "3. 格式要求：\n"
        "   - JSON数组格式\n"
        "   - 每个QA对包含instruction(问题)、output(答案)、system(角色设定)\n"
        "4. 其他要求：\n"
        "   - 基于上下文理解修复可能的错误\n"
        "   - 不遗漏任何一个符合提取内容的QA对，如果字数到上限可简化Q和A来保证不遗漏应当被提取的QA对\n"
        "   - 不提及作者信息和前言后传\n"
        "   - 重点关注卜卦流程\n"
    )
    
    try:
        logger.info(f"Calling Spark API with text chunk: {text_chunk[:50]}...")
        response = client.chat(messages=[{"role": "user", "content": f"{prompt}\n\n{text_chunk}"}])
        
        # 验证返回的JSON格式
        try:
            qa_list = json.loads(response)
            if not isinstance(qa_list, list):
                raise ValueError("返回结果必须是JSON数组")
            
            # 验证每个QA对的格式
            for qa in qa_list:
                if not all(k in qa for k in ("instruction", "output", "system")):
                    raise ValueError("QA对缺少必要字段")
                if qa["system"] != "你是一个占卜和算命解释专家，你需要遵循文本标准来帮我解决相关问题":
                    qa["system"] = "你是一个占卜和算命解释专家，你需要遵循文本标准来帮我解决相关问题"
            
            # 重新序列化为字符串
            response = json.dumps(qa_list, ensure_ascii=False)
            
        except json.JSONDecodeError:
            logger.error("API返回的不是有效的JSON格式")
            raise
        
        logger.info(f"Received and validated response: {response[:100]}...")
        return response
    except Exception as e:
        logger.error(f"API call failed: {e}")
        raise

def save_text_chunks(chunks, output_folder):
    """保存文本切片到文件"""
    chunks_folder = os.path.join(output_folder, 'text_chunks')
    os.makedirs(chunks_folder, exist_ok=True)
    
    chunk_files = []
    for i, chunk in enumerate(chunks):
        try:
            chunk_file = os.path.join(chunks_folder, f'chunk_{i + 1}.txt')
            with open(chunk_file, 'w', encoding='utf-8') as f:
                f.write(chunk)
            chunk_files.append(chunk_file)
        except Exception as e:
            logger.error(f"Error saving chunk {i + 1}: {e}")
    return chunk_files

def generate_qa_pairs(input_file, output_folder, start_index=0):
    """
    生成QA对，可以指定开始处理的切片索引
    """
    try:
        # 读取和切割文本
        text = read_txt_file(input_file)
        text_chunks = split_text(text)
        total_chunks = len(text_chunks)
        
        # 保存文本切片
        logger.info("Saving text chunks...")
        save_text_chunks(text_chunks, output_folder)
        
        # 处理每个文本块
        for i, chunk_text in enumerate(text_chunks[start_index:], start=start_index):
            logger.info(f"Processing chunk {i + 1}/{total_chunks}...")
            
            # 调用API生成QA对
            qa_pair = call_spark_api(chunk_text)
            
            # 解析返回的JSON字符串并保存
            try:
                qa_list = json.loads(qa_pair) if isinstance(qa_pair, str) else qa_pair
                output_file = os.path.join(output_folder, f'success{i + 1}.json')
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(qa_list, f, ensure_ascii=False, indent=4)
                logger.info(f"Chunk {i + 1}/{total_chunks} saved to '{output_file}'")
            except json.JSONDecodeError as e:
                logger.error(f"Error processing chunk {i + 1}: {e}")
                logger.error(f"Raw response: {qa_pair}")
                continue

    except Exception as e:
        logger.error(f"Generation failed: {e}")
        raise

if __name__ == "__main__":
    if len(sys.argv) != 3 and len(sys.argv) != 4:
        print("Usage: python generate_qa.py <input_file> <output_folder> [<start_index>]")
        sys.exit(1)

    try:
        input_file = sys.argv[1]
        output_folder = sys.argv[2]
        start_index = int(sys.argv[3]) if len(sys.argv) == 4 else 0
        generate_qa_pairs(input_file, output_folder, start_index)
        logger.info("QA pairs generation completed successfully.")
    except Exception as e:
        logger.error(f"Program failed: {e}")
        sys.exit(1)
