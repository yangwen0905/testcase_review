import os
import json
import requests
from typing import List, Dict, Optional


def analyze_test_cases(df):
    """
    使用CodeGeeX分析测试用例数据
    """
    # 构建分析提示词
    prompt = f"""
    作为资深测试工程师，请分析以下测试用例：
    请从以下几个方面进行分析，重点检查功能逻辑：
    1. 测试用例覆盖度分析
    2. 测试用例设计质量评估
    3. 逻辑漏洞（列出未覆盖场景）
    4. 冗余检查
    5. 改进建议
    以表格形式回应


    请提供结构化的分析报告。
    """
    # 从环境变量中获取 API 密钥
    API_key = "sk-u_lipvztOq2z6n5ktVJv4A"
    if not API_key:
        raise ValueError("请设置环境变量 CLAUDE_API_KEY")

    # 构造输入消息
    msg = [
        # {"role": "system", "content": "作为资深测试工程师，请分析以下测试用例"}
        {"role": "user", "content": "作为资深测试工程师，请分析以下测试用例"}
    ]

    # 调用 API
    ai_response = call_claude_3_7(API_key, msg)

    # 输出结果
    if ai_response:
        print("AI 分析结果：\n", ai_response)
        return ai_response
    else:
        print("未获得有效响应。")
        return f"未获得有效响应。"   

def analyze_test_cases_from_json(json_file_path: str):
    """
    从 JSON 文件中加载测试用例，并调用 Claude 3.7 进行分析
    """

    # 步骤一：读取 JSON 文件内容
    with open(json_file_path, 'r', encoding='utf-8') as f:
        test_cases_data = json.load(f)

    # 将 JSON 转换为字符串（便于插入 prompt）
    test_cases_str = json.dumps(test_cases_data, indent=2, ensure_ascii=False)

    # 步骤二：构建完整的 Prompt
    prompt = f"""
    作为资深测试工程师，请分析以下测试用例：
    
    请从以下几个方面进行结构化分析，重点检查功能逻辑：
    1. 测试用例覆盖度分析（是否遗漏边界场景或组合情况？）
    2. 测试用例设计质量评估（是否具备可执行性、断言明确？）
    3. 逻辑漏洞（列出未覆盖场景，如异常路径、权限控制等）
    4. 冗余检查（是否存在重复测试用例或步骤？）
    5. 改进建议（对测试用例结构、步骤顺序、预期结果等方面提出优化建议）

    以下是测试用例的 JSON 数据：
    
    {test_cases_str}
    
    请提供一份结构清晰、可操作性强的分析报告，以 Markdown 表格形式呈现。
    """

    # 步骤三：获取 API 密钥
    api_key = "sk-u_lipvztOq2z6n5ktVJv4A" # or os.getenv("CLAUDE_API_KEY") 
    if not api_key:
        raise ValueError("请设置环境变量 CLAUDE_API_KEY")

    # 步骤四：构造 messages
    messages = [
        {
            "role": "system",
            "content": "你是一个测试用例分析助手，能帮助我理解测试场景和逻辑。"
        },
        {
            "role": "user",
            "content": prompt  # 把完整的 prompt 传入 user content
        }
    ]

    # 步骤五：调用已封装的接口函数
    ai_response = call_claude_3_7(
        api_key=api_key,
        messages=messages,
        max_tokens=2048,
        temperature=0.5
    )

    # 步骤六：输出分析结果
    if ai_response:
        print("AI 分析结果：\n", ai_response)
        return ai_response
    else:
        print("未获得有效响应。")
        return "未获得有效响应。"


def call_claude_3_7(
    api_key: str,
    messages: List[Dict[str, str]],
    model: str = "claude-3-7-sonnet-latest",
    max_tokens: int = 150,
    temperature: float = 0.7,
    timeout: int = 300
) -> Optional[str]:
    """
    调用 Claude 3.7 API 并返回模型输出的文本内容

    参数:
        api_key (str): API 密钥
        messages (List[Dict[str, str]]): 对话历史，格式为 [{"role": "user/system", "content": "..."}]
        model (str): 使用的模型 ID
        max_tokens (int): 最大输出 token 数
        temperature (float): 输出随机性控制（0-1）
        timeout (int): 请求超时时间（秒）

    返回:
        Optional[str]: 模型返回的文本内容，或 None（请求失败时）
    """
    url = "https://llm-pool-common.nlp.yuntingai.com/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": model,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": temperature
    }

    try:
        response = requests.post(
            url,
            headers=headers,
            json=payload,
            timeout=timeout
        )

        if response.status_code == 200:
            data = response.json()
            # 提取模型输出内容
            if "choices" in data and len(data["choices"]) > 0:
                content = data["choices"][0].get("message", {}).get("content", "")
                return content.strip() if content else None
            else:
                print("[WARNING] 响应中未找到有效内容字段。")
                return None
        else:
            print(f"[ERROR] API 请求失败，状态码: {response.status_code}")
            print(f"响应内容: {response.text}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] 网络请求异常: {e}")
        return None
