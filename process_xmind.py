import json
from flask import Flask, request, render_template
import os
from datetime import datetime

from testcases_build import transform_type_to_json, convert
from analysis_build import analyze_test_cases_from_json
import shutil
from pathlib import Path
import logging


app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@app.route('/')
def index():
    return render_template('upload.html')  # 跳转上传页面


@app.route('/upload', methods=['POST'])
def upload_file():
    if 'test_cases' not in request.files:
        return "未选择文件!"
    file = request.files['test_cases']

    if file.filename == '':
        return "文件名无效！"

    if file and allowed_file(file.filename):  # 检查文件类型
        original_filename = file.filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_{original_filename}"
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

        try:
            file.save(file_path)

            # 检查文件是否成功保存
            if os.path.exists(file_path):
                file_size = os.path.getsize(file_path)
                print(f"文件保存成功: {file_path}, 大小: {file_size} 字节")

                # 调用transform_type函数将XMind类型转换为JSON类型
                json_filename = transform_type_to_json(file_path)
                print(f"开始转成测试用例模型！")
                convert(json_filename, "testcases.json")
                print(f"testcases 文件保存成功！")

            else:
                return "文件保存失败！"

            print("📋 开始处理测试用例...")
            
            # 获取当前脚本所在目录
            current_dir = os.path.dirname(os.path.abspath(__file__))
            json_file_path = os.path.join(current_dir, "testcases.json")
            print("📋 测试用例...")
            
            # 调用AI分析函数
            print("开始AI分析...")
            analysis_result = analyze_test_cases_from_json(json_file_path)
            print("✓ AI分析完成")

            
            
            try:
                # ✅ 将 JSON 字符串转为 Python 字典
                analysis_data = json.loads(analysis_result)
                
            except json.JSONDecodeError as e:
                analysis_data = {"modules": [], "summary": "JSON 解析失败: " + str(e)}

            # for module in analysis_data["modules"]:
            #     if module["type"] == "table":
            #         for i, row in enumerate(module["rows"]):
            #             module["rows"][i] = [cell.replace("\n", " ") for cell in row]
            for module in analysis_data["modules"]:
                if module["type"] == "table":
                    module["columns"] = module.get("columns", [])
                    module["rows"] = module.get("rows", [])
                    # 额外校验：确保 rows 是列表
                    if not isinstance(module["rows"], list):
                        module["rows"] = [module["rows"]]
            first_module = analysis_data["modules"][0]
            print("表格列:", first_module["columns"])
            print("表格行:", first_module["rows"])

            # for module in analysis_data["modules"]:
            #     if module["title"] == "冗余测试用例分析":
            #         print("冗余类型建议:")
            #         for row in module["rows"]:
            #             print(f"{row[0]}: {row[2]}")


                        # 返回分析结果页面
            return render_template('analysis_result.html',
                                  analysis_data=analysis_data)
        except Exception as e:
            print(f"[FATAL] 服务异常: {e}")
            return f"发生错误: {e}", 500

    return "仅支持 .mm, .xmind 文件！"


"""清除upload文件夹中的所有文件和子文件夹"""


def clear_upload_folder(upload_path: str = "uploads") -> None:
    print("🧹 清理upload文件夹...")
    try:
        if os.path.exists(upload_path):
            # 遍历文件夹中的所有内容
            for filename in os.listdir(upload_path):
                file_path = os.path.join(upload_path, filename)

                if os.path.isfile(file_path):
                    # 删除文件
                    os.remove(file_path)
                    print(f"🗑️  删除文件: {filename}")
                elif os.path.isdir(file_path):
                    # 删除文件夹及其内容
                    shutil.rmtree(file_path)
                    print(f"📁 删除文件夹: {filename}")

            print(f"✅ upload文件夹清理完成！")
        else:
            # 如果文件夹不存在，创建它
            os.makedirs(upload_path)
            print(f"📁 创建upload文件夹: {upload_path}")

    except Exception as e:
        print(f"❌ 清理upload文件夹时出错: {e}")


# 定义一个函数，用于判断文件名是否合法
def allowed_file(filename):
    # 判断文件名中是否包含“.”，并且文件名的后缀是否为'mm', 'xmind'
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'mm', 'xmind'}


if __name__ == '__main__':
    clear_upload_folder()
    app.run(debug=True)
