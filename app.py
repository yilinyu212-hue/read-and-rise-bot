import streamlit as st
import pandas as pd
import json
import os

# 1. 页面配置与导航
st.set_page_config(page_title="Read & Rise | AI Business Coach", layout="wide")

# 侧边栏导航
with st.sidebar:
    st.image("https://via.placeholder.com/150?text=Read+%26+Rise", width=100) # 建议放你的Logo
    st.title("Navigation")
    page = st.radio("前往 (Go to):", ["🚀 今日内参", "🧠 思维模型", "📚 跨界书单"])
    st.divider()
    st.info("💡 **Coach Tip:**\nReading in English is the best way to master global leadership language.")

# 2. 模拟双语数据展示函数 (让内容更丰富)
def display_bilingual_content(title_en, title_cn, content):
    with st.container():
        st.markdown(f"### {title_en} | {title_cn}")
        col_en, col_cn = st.columns(2)
        with col_en:
            st.markdown("#### 🇬🇧 English Insight")
            st.caption("Key takeaways for global communication")
            # 这里放置 AI 生成的英文摘要
            st.write(content.get('en', 'Content loading...'))
        with col_cn:
            st.markdown("#### 🇨🇳 教练解读")
            st.caption("针对中国企业家的实战建议")
            # 这里放置 AI 生成的中文深度拆解
            st.write(content.get('cn', '内容解析中...'))
        st.divider()

# --- 页面逻辑分流 ---

if page == "🚀 今日内参":
    st.markdown('<p style="font-size:3rem; font-weight:800; color:#10416F;">Hi, Leaders!</p>', unsafe_allow_html=True)
    
    # 增加搜索功能：提升交互期待感
    search_query = st.text_input("🔍 搜索全球讯息 (Search Global Insights):", placeholder="输入关键词，如 AI, Strategy...")
    
    # 这里放置你之前的雷达图和文章列表
    # ... (代码同上，但在展示时调用 display_bilingual_content)

elif page == "🧠 思维模型":
    st.header("🧠 商业思维模型库 (Mental Models)")
    st.write("掌握全球通用的决策语言。")
    
    # 示例卡片
    with st.expander("The First Principle | 第一性原理"):
        st.markdown("""
        - **Definition**: Breaking down complex problems into basic elements and reassembling them from the ground up.
        - **实战应用**: 剥离行业噪音，回归商业本质。
        - **English Phrasing**: "Let's strip away the assumptions and look at the core value."
        """)

elif page == "📚 跨界书单":
    st.header("📚 领导者书单 (Leader's Library)")
    # 展示书籍和案例
