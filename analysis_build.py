import os
import requests
from typing import List, Dict, Optional


# def analyze_test_cases(df):
#     """
#     使用CodeGeeX分析测试用例数据
#     """
#     try:
#         # 构建分析提示词
#         prompt = f"""
#         作为资深测试工程师，请分析以下测试用例：
#
#         请从以下几个方面进行分析，重点检查功能逻辑：
#         1. 测试用例覆盖度分析
#         2. 测试用例设计质量评估
#         3. 逻辑漏洞（列出未覆盖场景）
#         4. 冗余检查
#         5. 改进建议
#         以表格形式回应
#
#
#         请提供结构化的分析报告。
#         """
#
#         # 调用CodeGeeX API
#         analysis_result = call_claude_3_7(prompt)
#
#         return analysis_result
#
#     except Exception as e:
#         return f"分析过程中发生错误: {str(e)}"


def call_claude_3_7(
    api_key: str,
    messages: List[Dict[str, str]],
    model: str = "claude-3-7-sonnet-latest",
    max_tokens: int = 100,
    temperature: float = 0.7,
    timeout: int = 30
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


if __name__ == "__main__":
    # 从环境变量中获取 API 密钥
    API_key = os.getenv("CLAUDE_API_KEY")
    if not API_key:
        raise ValueError("请设置环境变量 CLAUDE_API_KEY")

    # 构造输入消息
    msg = [
        {"role": "system", "content": "你是一个测试用例分析助手，能帮助我理解测试场景和逻辑。"},
        {"role": "user", "content": "这是一个测试用例：用户登录功能，输入错误密码，应该提示密码错误。"}
    ]

    # 调用 API
    ai_response = call_claude_3_7(API_key, msg)

    # 输出结果
    if ai_response:
        print("AI 分析结果：\n", ai_response)
    else:
        print("未获得有效响应。")
