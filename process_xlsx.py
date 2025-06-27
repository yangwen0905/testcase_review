from flask import Flask, request, render_template
import pandas as pd
from werkzeug.utils import secure_filename
import os
from datetime import datetime
import requests
import json

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@app.route('/')  
def index():
    return render_template('upload.html')  #跳转上传页面

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
            else:
                return "文件保存失败！"
            
            # 使用pandas的read_excel函数读取Excel文件
            print("开始读取Excel文件...")
            df = pd.read_excel(file_path, engine='openpyxl')
            print(f"✓ Excel读取成功: {df.shape[0]}行, {df.shape[1]}列")
        
            # 将DataFrame转换为HTML表格
            table_html = df.to_html(classes='table table-striped', table_id='excel-table', escape=False)
            print("✓ HTML转换完成")

            # 调用AI分析函数
            print("开始AI分析...")
            analysis_result = analyze_test_cases(df)
            print("✓ AI分析完成")

            # 返回分析结果页面，将表格HTML和分析结果传递给模板
            return render_template('analysis_result.html', 
                     message=f"文件'{original_filename}'上传成功！", 
                     table_content=table_html,
                     analysis_result=analysis_result)

        except Exception as e:
            return f"发生错误: {e}"
        
    return "仅支持 .xlsx 文件！"

# 定义一个函数，用于判断文件名是否合法
def allowed_file(filename):
    # 判断文件名中是否包含“.”，并且文件名的后缀是否为“xlsx”
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'xlsx'}


  
def analyze_test_cases(df):
    """
    使用CodeGeeX分析测试用例数据
    """
    try:
        # 将DataFrame转换为可读的文本格式
        data_summary = prepare_data_for_analysis(df)
        
        # 构建分析提示词
        prompt = f"""
        作为资深测试工程师，请分析以下测试用例：

        数据概览：
        - 总行数：{df.shape[0]}
        - 总列数：{df.shape[1]}
        - 列名：{', '.join(df.columns.tolist())}

        
        数据内容：
        {data_summary}

        请从以下几个方面进行分析，重点检查功能逻辑：
        1. 测试用例覆盖度分析
        2. 测试用例设计质量评估
        3. 逻辑漏洞（列出未覆盖场景）
        4. 冗余检查
        5. 改进建议
        以表格形式回应

        
        请提供结构化的分析报告。
        """
        


        # 调用CodeGeeX API
        analysis_result = call_codegeex_api(prompt)
        
        return analysis_result
        
    except Exception as e:
        return f"分析过程中发生错误: {str(e)}"


def prepare_data_for_analysis(df):
    """
    准备数据用于AI分析，限制数据量避免token超限
    """
    # 获取前10行数据作为样本
    sample_data = df.head(10)
    
    # 转换为字符串格式
    data_text = sample_data.to_string(max_rows=10, max_cols=None)
    
    # 如果数据太长，进行截断
    if len(data_text) > 2000:
        data_text = data_text[:2000] + "...(数据已截断)"
    
    return data_text

def call_codegeex_api(prompt):
    """
    调用CodeGeeX API进行分析
    """
    # CodeGeeX API配置
    api_key = "API密钥"
    api_url = "http://localhost:11434/v1/chat/completions"  # 实际API地址需要确认
    headers = {
        "Content-Type": "application/json",
        # "Authorization": f"Bearer {api_key}"  # 需要替换为实际的API密钥
    }
    
    payload = {
        "model": "codegeex4",
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": 0.7,
        "max_tokens": 1000
    }
    
    try:
        response = requests.post(api_url, headers=headers, json=payload, timeout=500)
        
        if response.status_code == 200:
            result = response.json()
            # 根据实际API响应格式提取内容
            analysis_content = result.get("choices", [{}])[0].get("message", {}).get("content", "")
            return analysis_content
        else:
            return f"API调用失败，状态码: {response.status_code}"
            
    except requests.exceptions.RequestException as e:
        return f"网络请求错误: {str(e)}"
    except Exception as e:
        return f"API调用异常: {str(e)}"


if __name__ == '__main__':
    app.run(debug=True)
