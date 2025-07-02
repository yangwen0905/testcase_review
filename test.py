if __name__ == "__main__":
    import os

    # 获取当前脚本所在目录
    current_dir = os.path.dirname(os.path.abspath(__file__))
    json_file_path = os.path.join(current_dir, "testcases.json")

    # 打印结果
    print(json_file_path)