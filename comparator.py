"""
比对判定模块
Comparison and Judgment Module

对比断言与搜索结果，给出验证判定
"""

import json
import os
import anthropic
from pathlib import Path
from config import CLAUDE_MODEL
from searcher import format_search_results_for_comparison


def load_prompt():
    """加载比对prompt模板"""
    prompt_path = Path(__file__).parent / "prompts" / "compare.txt"
    return prompt_path.read_text(encoding="utf-8")


def compare_claim(claim: dict) -> dict:
    """
    比对单条断言与其搜索结果
    
    Args:
        claim: 包含claim和search_results的字典
        
    Returns:
        包含判定结果的字典
    """
    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        raise ValueError("请设置 ANTHROPIC_API_KEY 环境变量")
    
    client = anthropic.Anthropic(api_key=api_key)
    
    prompt_template = load_prompt()
    
    # 格式化搜索结果
    search_results_text = format_search_results_for_comparison(
        claim.get("search_results", {})
    )
    
    # 构建prompt
    prompt = prompt_template.replace("{claim}", claim.get("claim", ""))
    prompt = prompt.replace("{search_results}", search_results_text)
    
    message = client.messages.create(
        model=CLAUDE_MODEL,
        max_tokens=1000,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    
    # 解析JSON响应
    response_text = message.content[0].text
    
    # 尝试提取JSON
    if "```json" in response_text:
        json_start = response_text.find("```json") + 7
        json_end = response_text.find("```", json_start)
        response_text = response_text[json_start:json_end].strip()
    elif "```" in response_text:
        json_start = response_text.find("```") + 3
        json_end = response_text.find("```", json_start)
        response_text = response_text[json_start:json_end].strip()
    
    try:
        verdict = json.loads(response_text)
    except json.JSONDecodeError:
        verdict = {
            "verdict": "ERROR",
            "confidence": 0,
            "reasoning": f"判定解析失败: {response_text[:200]}",
            "evidence": {"supporting": [], "contradicting": []},
            "source_quality": "unknown"
        }
    
    return verdict


def compare_all_claims(claims_with_results: list) -> list:
    """
    批量比对所有断言
    
    Args:
        claims_with_results: 包含搜索结果的断言列表
        
    Returns:
        包含判定结果的断言列表
    """
    results = []
    
    for claim in claims_with_results:
        print(f"  判定中: {claim.get('claim', '')[:50]}...")
        
        verdict = compare_claim(claim)
        
        # 合并结果
        claim_result = claim.copy()
        claim_result["verdict"] = verdict
        results.append(claim_result)
    
    return results


def get_verdict_emoji(verdict: str) -> str:
    """获取判定结果对应的emoji"""
    emoji_map = {
        "VERIFIED": "✅",
        "CONTRADICTED": "❌",
        "PARTIALLY_VERIFIED": "⚠️",
        "UNVERIFIED": "❓",
        "ERROR": "🔴"
    }
    return emoji_map.get(verdict, "❓")


def get_verdict_cn(verdict: str) -> str:
    """获取判定结果的中文"""
    cn_map = {
        "VERIFIED": "已验证",
        "CONTRADICTED": "存在矛盾",
        "PARTIALLY_VERIFIED": "部分正确",
        "UNVERIFIED": "无法验证",
        "ERROR": "判定出错"
    }
    return cn_map.get(verdict, "未知")


# 测试用
if __name__ == "__main__":
    test_claim = {
        "claim": "OpenAI于2023年11月发布GPT-4 Turbo",
        "search_results": {
            "answer": "GPT-4 Turbo was announced at OpenAI DevDay on November 6, 2023.",
            "sources": [
                {
                    "title": "OpenAI DevDay Announcements",
                    "url": "https://openai.com/blog/new-models-and-developer-products-announced-at-devday",
                    "content": "We are excited to announce GPT-4 Turbo, our latest model..."
                }
            ]
        }
    }
    
    print("正在判定...")
    result = compare_claim(test_claim)
    print(json.dumps(result, ensure_ascii=False, indent=2))
