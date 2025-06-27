import requests
from google import genai


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


def call_gemini_api():
    """
    调用Gemini API进行分析
    """

    client = genai.Client(api_key="AIzaSyAKCQEreTKY8bew6cX3IN01wFOsosuDJUI")
    response = client.models.generate_content(
        model="gemini-2.0-flash", contents="Explain how AI works in a few words"
        )
    analysis_content = response.text()
    return analysis_content

if __name__ == "__main__":
    try:
        result = call_gemini_api()
        print("\n生成结果:")
        print(result)
    except Exception as e:
        print(f"错误: {e}")