#!/usr/bin/env python3
"""
幻觉检测器 - AI输出实时Fact-Checker
Hallucination Detector - Real-time AI Output Fact-Checker

用法:
    python main.py "要检测的AI回复文本"
    python main.py -f input.txt
    echo "文本" | python main.py

作者: 晓文 + Claude
版本: 0.1.0
"""

import sys
import argparse
import json
from pathlib import Path

from extractor import extract_claims
from searcher import search_all_claims
from comparator import compare_all_claims
from reporter import generate_markdown_report, generate_json_report
from config import OUTPUT_FORMAT


def detect_hallucinations(text: str, verbose: bool = True) -> dict:
    """
    主检测流程
    
    Args:
        text: 要检测的AI生成文本
        verbose: 是否打印进度信息
        
    Returns:
        检测结果字典
    """
    if verbose:
        print("=" * 50)
        print("🔍 AI幻觉检测器 v0.1.0")
        print("=" * 50)
        print()
    
    # Step 1: 提取断言
    if verbose:
        print("📌 Step 1/3: 提取可验证的事实声明...")
    
    extraction_result = extract_claims(text)
    
    if "error" in extraction_result:
        print(f"❌ 提取失败: {extraction_result['error']}")
        return {"error": extraction_result["error"]}
    
    claims = extraction_result.get("claims", [])
    
    if not claims:
        if verbose:
            print("✨ 未发现需要验证的事实声明")
        return {
            "status": "no_claims",
            "message": "文本中没有发现可验证的事实声明（可能是纯观点或建议类内容）"
        }
    
    if verbose:
        print(f"   发现 {len(claims)} 条可验证声明")
        print()
    
    # Step 2: 搜索验证
    if verbose:
        print("🔎 Step 2/3: 搜索相关信息...")
    
    claims_with_search = search_all_claims(claims)
    
    if verbose:
        print()
    
    # Step 3: 比对判定
    if verbose:
        print("⚖️ Step 3/3: 比对判定...")
    
    final_results = compare_all_claims(claims_with_search)
    
    if verbose:
        print()
        print("✅ 检测完成!")
        print()
    
    return {
        "status": "success",
        "extraction_summary": extraction_result.get("summary", {}),
        "results": final_results,
        "original_text": text
    }


def main():
    parser = argparse.ArgumentParser(
        description="AI幻觉检测器 - 检测AI输出中的事实错误",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python main.py "根据最新数据，中国GDP增长5.2%..."
  python main.py -f response.txt
  python main.py -f response.txt -o report.md
  echo "AI回复内容" | python main.py
        """
    )
    
    parser.add_argument(
        "text",
        nargs="?",
        help="要检测的文本（也可以通过stdin输入）"
    )
    
    parser.add_argument(
        "-f", "--file",
        help="从文件读取要检测的文本"
    )
    
    parser.add_argument(
        "-o", "--output",
        help="输出报告到文件（默认输出到stdout）"
    )
    
    parser.add_argument(
        "--format",
        choices=["markdown", "json"],
        default=OUTPUT_FORMAT,
        help="输出格式（默认: markdown）"
    )
    
    parser.add_argument(
        "-q", "--quiet",
        action="store_true",
        help="静默模式，不打印进度信息"
    )
    
    args = parser.parse_args()
    
    # 获取输入文本
    if args.file:
        text = Path(args.file).read_text(encoding="utf-8")
    elif args.text:
        text = args.text
    elif not sys.stdin.isatty():
        text = sys.stdin.read()
    else:
        parser.print_help()
        print("\n❌ 错误: 请提供要检测的文本")
        sys.exit(1)
    
    if not text.strip():
        print("❌ 错误: 输入文本为空")
        sys.exit(1)
    
    # 执行检测
    result = detect_hallucinations(text, verbose=not args.quiet)
    
    if result.get("error"):
        sys.exit(1)
    
    if result.get("status") == "no_claims":
        print(result["message"])
        sys.exit(0)
    
    # 生成报告
    if args.format == "json":
        report = json.dumps(
            generate_json_report(result["results"], text),
            ensure_ascii=False,
            indent=2
        )
    else:
        report = generate_markdown_report(result["results"], text)
    
    # 输出
    if args.output:
        Path(args.output).write_text(report, encoding="utf-8")
        print(f"📄 报告已保存到: {args.output}")
    else:
        print(report)


if __name__ == "__main__":
    main()
