"""
搜索验证模块
Search Verification Module

使用Tavily API搜索验证事实声明
"""

import os
import requests
from config import SEARCH_RESULTS_PER_CLAIM, SEARCH_DEPTH


TAVILY_SEARCH_URL = "https://api.tavily.com/search"


def search_claim(query: str, include_domains: list = None) -> dict:
    """
    搜索单条声明的相关信息
    
    Args:
        query: 搜索关键词
        include_domains: 可选，限定搜索域名列表
        
    Returns:
        搜索结果字典
    """
    api_key = os.environ.get("TAVILY_API_KEY", "")
    if not api_key:
        raise ValueError("请设置 TAVILY_API_KEY 环境变量\n免费注册: https://tavily.com/")
    
    payload = {
        "api_key": api_key,
        "query": query,
        "search_depth": SEARCH_DEPTH,
        "max_results": SEARCH_RESULTS_PER_CLAIM,
        "include_answer": True,  # Tavily会生成一个总结答案
        "include_raw_content": False,  # 不需要原始HTML
    }
    
    if include_domains:
        payload["include_domains"] = include_domains
    
    try:
        response = requests.post(TAVILY_SEARCH_URL, json=payload, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {
            "error": f"搜索请求失败: {str(e)}",
            "results": []
        }


def search_all_claims(claims: list) -> list:
    """
    批量搜索所有断言
    
    Args:
        claims: 断言列表，每个断言需包含 search_query 字段
        
    Returns:
        包含搜索结果的断言列表
    """
    results = []
    
    for claim in claims:
        query = claim.get("search_query", claim.get("claim", ""))
        
        print(f"  搜索中: {query[:50]}...")
        
        search_result = search_claim(query)
        
        # 将搜索结果附加到断言上
        claim_with_results = claim.copy()
        claim_with_results["search_results"] = {
            "query": query,
            "answer": search_result.get("answer", ""),
            "sources": []
        }
        
        # 提取关键信息
        for result in search_result.get("results", []):
            claim_with_results["search_results"]["sources"].append({
                "title": result.get("title", ""),
                "url": result.get("url", ""),
                "content": result.get("content", "")[:500],  # 截断过长内容
                "score": result.get("score", 0)
            })
        
        results.append(claim_with_results)
    
    return results


def format_search_results_for_comparison(search_results: dict) -> str:
    """
    将搜索结果格式化为比对prompt的输入格式
    
    Args:
        search_results: 搜索结果字典
        
    Returns:
        格式化的字符串
    """
    output = []
    
    if search_results.get("answer"):
        output.append(f"[Tavily总结] {search_results['answer']}\n")
    
    for i, source in enumerate(search_results.get("sources", []), 1):
        output.append(f"[来源{i}] {source['title']}")
        output.append(f"URL: {source['url']}")
        output.append(f"内容: {source['content']}")
        output.append("")
    
    return "\n".join(output) if output else "未找到相关搜索结果"


# 测试用
if __name__ == "__main__":
    test_claims = [
        {
            "claim": "OpenAI于2023年11月发布GPT-4 Turbo",
            "search_query": "OpenAI GPT-4 Turbo release date 2023"
        }
    ]
    
    print("正在搜索...")
    results = search_all_claims(test_claims)
    
    for r in results:
        print(f"\n断言: {r['claim']}")
        print(f"搜索结果数: {len(r['search_results']['sources'])}")
        if r['search_results']['answer']:
            print(f"Tavily答案: {r['search_results']['answer'][:200]}...")
