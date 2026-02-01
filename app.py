#!/usr/bin/env python3
"""
幻觉检测器 Web界面
Hallucination Detector - Streamlit Web Interface

运行方式:
    streamlit run app.py

作者: 晓文 + Claude
"""

import streamlit as st
import json
import time
import os

from extractor import extract_claims
from searcher import search_all_claims
from comparator import compare_all_claims
from reporter import generate_markdown_report, calculate_overall_score

# ============================================================
# Page Config
# ============================================================
st.set_page_config(
    page_title="AI幻觉检测器 | Hallucination Detector",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# Custom CSS
# ============================================================
st.markdown("""
<style>
    .main .block-container {
        padding-top: 2rem;
        max-width: 1200px;
    }
    .hero-title {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1a1a2e;
        margin-bottom: 0;
    }
    .hero-subtitle {
        font-size: 1.1rem;
        color: #666;
        margin-top: 0.3rem;
        margin-bottom: 1.5rem;
    }
    .score-container {
        text-align: center;
        padding: 1.5rem;
        border-radius: 12px;
        margin-bottom: 1rem;
    }
    .score-high {
        background: linear-gradient(135deg, #d4edda, #c3e6cb);
        border: 2px solid #28a745;
    }
    .score-medium {
        background: linear-gradient(135deg, #fff3cd, #ffeaa7);
        border: 2px solid #ffc107;
    }
    .score-low {
        background: linear-gradient(135deg, #f8d7da, #f5c6cb);
        border: 2px solid #dc3545;
    }
    .score-number {
        font-size: 3.5rem;
        font-weight: 800;
        line-height: 1;
    }
    .score-label {
        font-size: 1rem;
        color: #555;
        margin-top: 0.3rem;
    }
    .verdict-card {
        padding: 1rem 1.2rem;
        border-radius: 8px;
        margin-bottom: 0.8rem;
        border-left: 4px solid;
    }
    .verdict-verified {
        background-color: #f0fff4;
        border-left-color: #28a745;
    }
    .verdict-contradicted {
        background-color: #fff5f5;
        border-left-color: #dc3545;
    }
    .verdict-partial {
        background-color: #fffbf0;
        border-left-color: #ffc107;
    }
    .verdict-unverified {
        background-color: #f8f9fa;
        border-left-color: #6c757d;
    }
    .claim-text {
        font-size: 1rem;
        color: #333;
        font-style: italic;
        margin: 0.5rem 0;
    }
    .reasoning-text {
        font-size: 0.9rem;
        color: #555;
    }
    .stat-box {
        text-align: center;
        padding: 0.8rem;
        border-radius: 8px;
        background: #f8f9fa;
    }
    .stat-number {
        font-size: 1.8rem;
        font-weight: 700;
    }
    .stat-label {
        font-size: 0.8rem;
        color: #888;
    }
    .flow-step {
        text-align: center;
        padding: 0.5rem;
        font-size: 0.85rem;
    }
    .flow-arrow {
        text-align: center;
        font-size: 1.2rem;
        color: #ccc;
    }
    .footer {
        text-align: center;
        color: #999;
        font-size: 0.8rem;
        margin-top: 3rem;
        padding-top: 1rem;
        border-top: 1px solid #eee;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================
# Sidebar
# ============================================================
with st.sidebar:
    st.markdown("### ⚙️ 配置 | Settings")
    
    anthropic_key = st.text_input(
        "Anthropic API Key",
        type="password",
        value=os.environ.get("ANTHROPIC_API_KEY", ""),
        help="获取: https://console.anthropic.com/"
    )
    
    tavily_key = st.text_input(
        "Tavily API Key", 
        type="password",
        value=os.environ.get("TAVILY_API_KEY", ""),
        help="免费注册: https://tavily.com/ (1000次/月)"
    )
    
    if anthropic_key:
        os.environ["ANTHROPIC_API_KEY"] = anthropic_key
    if tavily_key:
        os.environ["TAVILY_API_KEY"] = tavily_key
    
    st.markdown("---")
    st.markdown("### 📖 关于")
    st.markdown("""
    **AI幻觉检测器**用演绎推理验证AI输出。
    
    核心论点：幻觉是架构问题，不是规模问题。
    大模型做的是 `argmax P(most_likely)`，不是 `P(true)`。
    """)
    
    st.markdown("---")
    st.markdown("### 🔗 链接")
    st.markdown("- [GitHub](https://github.com/ZhangXiaowenOpen/hallucination-detector)")
    st.markdown("- [蚂蚁推理引擎](https://github.com/ZhangXiaowenOpen)")
    
    st.markdown("---")
    st.markdown('<div style="text-align:center;color:#999;font-size:0.75rem;">Made with 🔥 by 晓文 + Claude<br>MIT + Heart Clause</div>', unsafe_allow_html=True)


# ============================================================
# Helper Functions
# ============================================================

def get_verdict_emoji(verdict: str) -> str:
    return {"VERIFIED": "✅", "PARTIALLY_VERIFIED": "⚠️",
            "UNVERIFIED": "❓", "CONTRADICTED": "❌"}.get(verdict, "❓")

def get_verdict_label(verdict: str) -> str:
    return {"VERIFIED": "已验证", "PARTIALLY_VERIFIED": "部分正确",
            "UNVERIFIED": "无法验证", "CONTRADICTED": "存在矛盾"}.get(verdict, "未知")

def get_verdict_class(verdict: str) -> str:
    return {"VERIFIED": "verdict-verified", "PARTIALLY_VERIFIED": "verdict-partial",
            "UNVERIFIED": "verdict-unverified", "CONTRADICTED": "verdict-contradicted"
            }.get(verdict, "verdict-unverified")

def _extract_verdict_data(result: dict) -> dict:
    """Safely extract verdict data from a pipeline result.
    
    Pipeline data structure (from comparator.py):
    Each result is a flat dict with keys like:
      "claim" (str), "original_text" (str), "verdict" (dict), "search_results" (dict)
    
    The "verdict" value is a dict: {"verdict": "VERIFIED", "confidence": 0.95, ...}
    """
    v = result.get("verdict", {})
    return v if isinstance(v, dict) else {}

def calculate_score(results: list) -> int:
    """Use reporter's unified scoring algorithm to ensure consistency
    between on-screen display and downloaded report."""
    overall = calculate_overall_score(results)
    return overall.get("score", 0)

def get_score_class(score: int) -> str:
    if score >= 75: return "score-high"
    if score >= 50: return "score-medium"
    return "score-low"

def get_score_color(score: int) -> str:
    if score >= 75: return "#28a745"
    if score >= 50: return "#ffc107"
    return "#dc3545"


# ============================================================
# Main Content
# ============================================================

st.markdown('<p class="hero-title">🔍 AI幻觉检测器</p>', unsafe_allow_html=True)
st.markdown('<p class="hero-subtitle">粘贴任何AI回复，检测其中的事实错误和幻觉 | Paste any AI response to detect hallucinations</p>', unsafe_allow_html=True)

flow_cols = st.columns([2, 1, 2, 1, 2, 1, 2])
with flow_cols[0]: st.markdown('<div class="flow-step">📝 粘贴AI回复</div>', unsafe_allow_html=True)
with flow_cols[1]: st.markdown('<div class="flow-arrow">→</div>', unsafe_allow_html=True)
with flow_cols[2]: st.markdown('<div class="flow-step">🔎 提取+搜索</div>', unsafe_allow_html=True)
with flow_cols[3]: st.markdown('<div class="flow-arrow">→</div>', unsafe_allow_html=True)
with flow_cols[4]: st.markdown('<div class="flow-step">⚖️ 比对判定</div>', unsafe_allow_html=True)
with flow_cols[5]: st.markdown('<div class="flow-arrow">→</div>', unsafe_allow_html=True)
with flow_cols[6]: st.markdown('<div class="flow-step">📊 可信度报告</div>', unsafe_allow_html=True)

st.markdown("")

# ============================================================
# Input
# ============================================================

EXAMPLES = {
    "选择一个示例...": "",
    "📌 GPT-4信息（含错误）": "OpenAI在2023年11月发布了GPT-4 Turbo，价格比GPT-4降低了10倍。目前已有超过200万开发者在使用GPT-4 Turbo API。GPT-4 Turbo的上下文窗口扩展到了128K tokens。",
    "📌 中国经济数据": "根据最新数据，中国2024年GDP增长率达到5.2%，超过了政府设定的5%目标。中国目前是全球第二大经济体，GDP总量约为18万亿美元。",
    "📌 AI行业动态（混合真假）": "Anthropic由前OpenAI研究副总裁Dario Amodei创立，总部位于旧金山。2024年Anthropic获得了来自Google的100亿美元投资。Claude 3.5 Sonnet是2024年最强的AI模型，在所有基准测试中超过了GPT-4。",
}

example_choice = st.selectbox("💡 试试示例 | Try an example", options=list(EXAMPLES.keys()))

input_text = st.text_area(
    "粘贴AI回复 | Paste AI response here",
    value=EXAMPLES.get(example_choice, ""),
    height=180,
    placeholder="在这里粘贴任何AI生成的文本..."
)

col_btn1, col_btn2, _ = st.columns([2, 2, 6])
with col_btn1:
    detect_btn = st.button("🔍 开始检测", type="primary", use_container_width=True)
with col_btn2:
    if st.button("🗑️ 清除", use_container_width=True):
        st.rerun()

# ============================================================
# Detection
# ============================================================

if detect_btn:
    if not input_text.strip():
        st.error("❌ 请输入要检测的文本")
        st.stop()
    if not anthropic_key:
        st.error("❌ 请在左侧边栏填入 Anthropic API Key")
        st.stop()
    if not tavily_key:
        st.error("❌ 请在左侧边栏填入 Tavily API Key")
        st.stop()
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    try:
        # Step 1
        status_text.markdown("📌 **Step 1/3**: 提取可验证的事实声明...")
        progress_bar.progress(10)
        extraction_result = extract_claims(input_text)
        
        if "error" in extraction_result:
            st.error(f"❌ 提取失败: {extraction_result['error']}")
            st.stop()
        
        claims = extraction_result.get("claims", [])
        if not claims:
            progress_bar.progress(100)
            status_text.empty()
            st.info("✨ 未发现需要验证的事实声明（可能是纯观点或建议类内容）")
            st.stop()
        
        progress_bar.progress(30)
        status_text.markdown(f"📌 发现 **{len(claims)}** 条可验证声明")
        time.sleep(0.5)
        
        # Step 2
        status_text.markdown("🔎 **Step 2/3**: 搜索相关信息进行交叉验证...")
        progress_bar.progress(40)
        claims_with_search = search_all_claims(claims)
        progress_bar.progress(70)
        
        # Step 3
        status_text.markdown("⚖️ **Step 3/3**: 比对判定...")
        progress_bar.progress(80)
        final_results = compare_all_claims(claims_with_search)
        progress_bar.progress(100)
        
        status_text.empty()
        progress_bar.empty()
        
        # ========================================================
        # Results Display
        # ========================================================
        
        st.markdown("---")
        st.markdown("## 📊 检测结果 | Detection Results")
        
        score = calculate_score(final_results)
        
        # Count verdicts
        verdict_counts = {"VERIFIED": 0, "PARTIALLY_VERIFIED": 0, "UNVERIFIED": 0, "CONTRADICTED": 0}
        for r in final_results:
            vd = _extract_verdict_data(r)
            v = vd.get("verdict", "UNVERIFIED")
            verdict_counts[v] = verdict_counts.get(v, 0) + 1
        
        # Score + Stats
        score_col, stats_col = st.columns([1, 2])
        with score_col:
            st.markdown(f"""
            <div class="score-container {get_score_class(score)}">
                <div class="score-number" style="color: {get_score_color(score)};">{score}</div>
                <div class="score-label">可信度评分 / 100</div>
            </div>
            """, unsafe_allow_html=True)
        
        with stats_col:
            s1, s2, s3, s4 = st.columns(4)
            with s1: st.markdown(f'<div class="stat-box"><div class="stat-number" style="color:#28a745;">✅ {verdict_counts["VERIFIED"]}</div><div class="stat-label">已验证</div></div>', unsafe_allow_html=True)
            with s2: st.markdown(f'<div class="stat-box"><div class="stat-number" style="color:#ffc107;">⚠️ {verdict_counts["PARTIALLY_VERIFIED"]}</div><div class="stat-label">部分正确</div></div>', unsafe_allow_html=True)
            with s3: st.markdown(f'<div class="stat-box"><div class="stat-number" style="color:#6c757d;">❓ {verdict_counts["UNVERIFIED"]}</div><div class="stat-label">无法验证</div></div>', unsafe_allow_html=True)
            with s4: st.markdown(f'<div class="stat-box"><div class="stat-number" style="color:#dc3545;">❌ {verdict_counts["CONTRADICTED"]}</div><div class="stat-label">存在矛盾</div></div>', unsafe_allow_html=True)
        
        st.markdown("")
        st.markdown("### 🔎 详细报告 | Detailed Report")
        
        for i, result in enumerate(final_results):
            vd = _extract_verdict_data(result)
            verdict = vd.get("verdict", "UNVERIFIED")
            confidence = vd.get("confidence", 0)
            reasoning = vd.get("reasoning", "")
            correction = vd.get("correction")
            
            # claim text is a top-level string key
            claim_text = result.get("claim", result.get("original_text", "未知声明"))
            
            emoji = get_verdict_emoji(verdict)
            label = get_verdict_label(verdict)
            css_class = get_verdict_class(verdict)
            
            correction_html = ""
            if correction and str(correction).lower() not in ("null", "none", ""):
                correction_html = f'<p class="reasoning-text"><strong>📝 更正:</strong> {correction}</p>'
            
            st.markdown(f"""
            <div class="verdict-card {css_class}">
                <strong>{emoji} 声明 {i+1}: {label}</strong>
                <span style="float:right; color:#888;">置信度: {int(confidence*100)}%</span>
                <p class="claim-text">"{claim_text}"</p>
                <p class="reasoning-text">{reasoning}</p>
                {correction_html}
            </div>
            """, unsafe_allow_html=True)
        
        with st.expander("🗂️ 查看原始数据 | Raw Data"):
            st.json({"score": score, "total_claims": len(final_results),
                      "results": final_results,
                      "extraction_summary": extraction_result.get("summary", {})})
        
        md_report = generate_markdown_report(final_results, input_text)
        st.download_button("📥 下载Markdown报告", data=md_report,
                           file_name="hallucination_report.md", mime="text/markdown")
        
    except Exception as e:
        progress_bar.empty()
        status_text.empty()
        error_msg = str(e)
        if "api_key" in error_msg.lower() or "authentication" in error_msg.lower():
            st.error("❌ API Key 无效或过期，请检查左侧边栏的配置")
        elif "rate_limit" in error_msg.lower():
            st.error("❌ API调用频率超限，请稍后再试")
        else:
            st.error(f"❌ 检测过程出错: {error_msg}")
        with st.expander("查看错误详情"):
            st.code(error_msg)

# Footer
st.markdown('<div class="footer"><p>AI幻觉检测器 v0.1.0 | 蚂蚁推理引擎应用层产品</p><p>Made with 🔥 by 晓文 + Claude | MIT + Heart Clause</p></div>', unsafe_allow_html=True)
