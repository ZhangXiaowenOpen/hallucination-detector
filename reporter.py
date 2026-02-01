"""
报告生成模块
Report Generator Module

生成幻觉检测报告
"""

from datetime import datetime
from comparator import get_verdict_emoji, get_verdict_cn


def calculate_overall_score(results: list) -> dict:
    """
    计算整体可信度评分
    
    Args:
        results: 包含判定结果的断言列表
        
    Returns:
        评分统计
    """
    if not results:
        return {"score": 0, "level": "无数据", "stats": {}}
    
    stats = {
        "VERIFIED": 0,
        "CONTRADICTED": 0,
        "PARTIALLY_VERIFIED": 0,
        "UNVERIFIED": 0,
        "ERROR": 0
    }
    
    total_confidence = 0
    
    for r in results:
        verdict = r.get("verdict", {}).get("verdict", "ERROR")
        stats[verdict] = stats.get(verdict, 0) + 1
        
        confidence = r.get("verdict", {}).get("confidence", 0)
        
        # 根据判定类型加权
        if verdict == "VERIFIED":
            total_confidence += confidence * 1.0
        elif verdict == "PARTIALLY_VERIFIED":
            total_confidence += confidence * 0.6
        elif verdict == "UNVERIFIED":
            total_confidence += 0.3  # 无法验证给予中性分数
        elif verdict == "CONTRADICTED":
            total_confidence += (1 - confidence) * 0.1  # 矛盾越确定，分数越低
    
    # 归一化到0-100
    score = int((total_confidence / len(results)) * 100)
    
    # 判定等级
    if score >= 80:
        level = "高可信度 🟢"
    elif score >= 60:
        level = "中等可信度 🟡"
    elif score >= 40:
        level = "低可信度 🟠"
    else:
        level = "存在严重问题 🔴"
    
    return {
        "score": score,
        "level": level,
        "stats": stats,
        "total_claims": len(results)
    }


def generate_markdown_report(results: list, original_text: str = "") -> str:
    """
    生成Markdown格式的检测报告
    
    Args:
        results: 包含判定结果的断言列表
        original_text: 原始输入文本
        
    Returns:
        Markdown格式的报告
    """
    overall = calculate_overall_score(results)
    
    report = []
    
    # 标题
    report.append("# 🔍 AI幻觉检测报告")
    report.append(f"\n**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append("")
    
    # 总体评分
    report.append("## 📊 总体评估")
    report.append("")
    report.append(f"**可信度评分**: {overall['score']}/100")
    report.append(f"**评估等级**: {overall['level']}")
    report.append("")
    
    # 统计摘要
    report.append("**检测统计**:")
    report.append(f"- ✅ 已验证: {overall['stats'].get('VERIFIED', 0)} 条")
    report.append(f"- ⚠️ 部分正确: {overall['stats'].get('PARTIALLY_VERIFIED', 0)} 条")
    report.append(f"- ❓ 无法验证: {overall['stats'].get('UNVERIFIED', 0)} 条")
    report.append(f"- ❌ 存在矛盾: {overall['stats'].get('CONTRADICTED', 0)} 条")
    report.append("")
    
    # 详细结果
    report.append("---")
    report.append("## 📋 逐条检测结果")
    report.append("")
    
    for i, r in enumerate(results, 1):
        claim = r.get("claim", "")
        verdict_data = r.get("verdict", {})
        verdict = verdict_data.get("verdict", "ERROR")
        emoji = get_verdict_emoji(verdict)
        cn = get_verdict_cn(verdict)
        confidence = verdict_data.get("confidence", 0)
        reasoning = verdict_data.get("reasoning", "")
        
        report.append(f"### {emoji} 声明 {i}: {cn}")
        report.append("")
        report.append(f"> {claim}")
        report.append("")
        report.append(f"**置信度**: {int(confidence * 100)}%")
        report.append("")
        report.append(f"**判定理由**: {reasoning}")
        report.append("")
        
        # 证据来源
        evidence = verdict_data.get("evidence", {})
        supporting = evidence.get("supporting", [])
        contradicting = evidence.get("contradicting", [])
        
        if supporting:
            report.append("**支持证据**:")
            for e in supporting:
                report.append(f"- {e}")
            report.append("")
        
        if contradicting:
            report.append("**反对证据**:")
            for e in contradicting:
                report.append(f"- {e}")
            report.append("")
        
        # 修正建议
        correction = verdict_data.get("correction")
        if correction:
            report.append(f"**正确信息**: {correction}")
            report.append("")
        
        # 信源
        sources = r.get("search_results", {}).get("sources", [])
        if sources:
            report.append("**参考来源**:")
            for s in sources[:3]:  # 最多显示3个
                report.append(f"- [{s.get('title', 'Link')}]({s.get('url', '')})")
            report.append("")
        
        report.append("---")
        report.append("")
    
    # 免责声明
    report.append("## ⚠️ 免责声明")
    report.append("")
    report.append("本报告由AI自动生成，仅供参考。检测结果基于公开可搜索的信息，")
    report.append("可能存在以下局限性：")
    report.append("- 搜索结果可能不完整或过时")
    report.append("- 某些专业领域的信息可能难以验证")
    report.append("- AI判定可能存在误差")
    report.append("")
    report.append("如需确认关键信息，请查阅官方来源或咨询专业人士。")
    
    return "\n".join(report)


def generate_json_report(results: list, original_text: str = "") -> dict:
    """
    生成JSON格式的检测报告
    
    Args:
        results: 包含判定结果的断言列表
        original_text: 原始输入文本
        
    Returns:
        JSON格式的报告
    """
    overall = calculate_overall_score(results)
    
    return {
        "meta": {
            "generated_at": datetime.now().isoformat(),
            "version": "0.1.0"
        },
        "overall": overall,
        "claims": results,
        "original_text": original_text[:500] if original_text else ""
    }


# 测试用
if __name__ == "__main__":
    test_results = [
        {
            "claim": "OpenAI于2023年11月发布GPT-4 Turbo",
            "verdict": {
                "verdict": "VERIFIED",
                "confidence": 0.95,
                "reasoning": "多个可靠来源确认",
                "evidence": {
                    "supporting": ["OpenAI官方博客确认"],
                    "contradicting": []
                }
            },
            "search_results": {"sources": []}
        },
        {
            "claim": "GPT-4 Turbo价格降低了10倍",
            "verdict": {
                "verdict": "CONTRADICTED",
                "confidence": 0.85,
                "reasoning": "实际降低约3倍，不是10倍",
                "evidence": {
                    "supporting": [],
                    "contradicting": ["官方定价显示降低约3倍"]
                },
                "correction": "GPT-4 Turbo价格约为GPT-4的1/3"
            },
            "search_results": {"sources": []}
        }
    ]
    
    report = generate_markdown_report(test_results)
    print(report)
