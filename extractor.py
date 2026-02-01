"""
断言提取模块
Claim Extractor Module

从AI生成的文本中提取可验证的事实声明
"""

import json
import os
import anthropic
from pathlib import Path
from config import CLAUDE_MODEL, MAX_CLAIMS_TO_EXTRACT


def load_prompt():
    """加载提取prompt模板"""
    prompt_path = Path(__file__).parent / "prompts" / "extract.txt"
    return prompt_path.read_text(encoding="utf-8")


def extract_claims(text: str) -> dict:
    """
    从文本中提取可验证的事实声明
    
    Args:
        text: AI生成的文本
        
    Returns:
        包含claims列表的字典
    """
    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        raise ValueError("请设置 ANTHROPIC_API_KEY 环境变量")
    
    client = anthropic.Anthropic(api_key=api_key)
    
    prompt_template = load_prompt()
    prompt = prompt_template.replace("{text}", text)
    
    message = client.messages.create(
        model=CLAUDE_MODEL,
        max_tokens=2000,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    
    # 解析JSON响应
    response_text = message.content[0].text
    
    # 尝试提取JSON（处理可能的markdown代码块）
    if "```json" in response_text:
        json_start = response_text.find("```json") + 7
        json_end = response_text.find("```", json_start)
        response_text = response_text[json_start:json_end].strip()
    elif "```" in response_text:
        json_start = response_text.find("```") + 3
        json_end = response_text.find("```", json_start)
        response_text = response_text[json_start:json_end].strip()
    
    try:
        result = json.loads(response_text)
    except json.JSONDecodeError as e:
        # 如果解析失败，返回原始响应供调试
        return {
            "error": f"JSON解析失败: {str(e)}",
            "raw_response": response_text,
            "claims": []
        }
    
    # 限制提取数量
    if "claims" in result and len(result["claims"]) > MAX_CLAIMS_TO_EXTRACT:
        # 优先保留 high verifiability 的声明
        high_priority = [c for c in result["claims"] if c.get("verifiability") == "high"]
        others = [c for c in result["claims"] if c.get("verifiability") != "high"]
        result["claims"] = (high_priority + others)[:MAX_CLAIMS_TO_EXTRACT]
    
    return result


# 测试用
if __name__ == "__main__":
    test_text = """
    根据最新数据，中国2024年GDP增长率达到5.2%，超过了政府设定的5%目标。
    深圳市在人工智能领域的投资超过100亿元，已经建成超过50个AI创新中心。
    专家建议投资者应该关注新能源和AI两个赛道。
    """
    
    print("正在提取断言...")
    result = extract_claims(test_text)
    print(json.dumps(result, ensure_ascii=False, indent=2))
