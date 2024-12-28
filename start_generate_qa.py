import os
from generate_qa import generate_qa_pairs

def main():
    # 在这里填写输入文件路径和输出文件夹路径
    input_file = r"G:\see\梅花易数白话解 (（宋）邵雍著；刘光本，荣益译) (Z-Library).txt"
    output_folder = r'G:\see\output4'
    start_index = 0  # 从n + 1个切片开始

    if not os.path.isfile(input_file):
        print(f"Error: Input file '{input_file}' does not exist.")
        return

    if not os.path.isdir(output_folder):
        print(f"Error: Output folder '{output_folder}' does not exist.")
        return

    generate_qa_pairs(input_file, output_folder, start_index)
    print(f"QA pairs have been successfully generated and saved to '{output_folder}'.")

if __name__ == "__main__":
    main()
