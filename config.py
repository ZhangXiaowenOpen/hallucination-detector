"""
幻觉检测器配置文件
Hallucination Detector Configuration

使用前请设置环境变量：
export ANTHROPIC_API_KEY="your-key-here"
export TAVILY_API_KEY="your-key-here"

或者直接在下方填入（不推荐提交到git）
"""

import os

# Claude API配置
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
CLAUDE_MODEL = "claude-sonnet-4-20250514"  # 可换成更便宜的模型

# Tavily搜索API配置
# 免费注册: https://tavily.com/ (1000次/月免费)
TAVILY_API_KEY = os.environ.get("TAVILY_API_KEY", "")

# 检测参数
MAX_CLAIMS_TO_EXTRACT = 5      # 最多提取几条断言
SEARCH_RESULTS_PER_CLAIM = 5   # 每条断言搜索几个结果
SEARCH_DEPTH = "basic"          # "basic" 或 "advanced"

# 输出配置
OUTPUT_FORMAT = "markdown"      # "markdown" 或 "json"
LANGUAGE = "zh"                 # "zh" 中文 / "en" 英文
