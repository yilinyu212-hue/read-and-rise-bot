import streamlit as st
import json
import os

# 配置：AI Business Coach 风格
st.set_page_config(page_title="Read & Rise | AI Business Coach", layout="wide", page_icon="🧘")

# 注入 CSS：更具设计感和专业度
st.markdown("""
    <style>
    .coach-card {
        background-color: #ffffff;
        padding: 30px;
        border-radius: 12px;
        border-left: 6px solid #10416F;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        margin-bottom: 30px;
    }
    .model-badge {
        background-color: #e3f2fd;
        color: #0d47a1;
        padding: 4px 12px;
        border-radius: 4px;
        font-weight: bold;
        font-size: 0.85rem;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🏹 Read & Rise: AI Business Coach")
st.markdown("#### *全球内参 × 思维模型 × 跨界实战*")

# 数据加载
if os.path.exists("data.json"):
    with open("data.json", "r", encoding="utf-8") as f:
        articles = json.load(f)
    
    for art in articles:
        # 使用教练卡片布局
        st.markdown(f'''
            <div class="coach-card">
                <p style="color:#0d47a1; font-weight:700; margin-bottom:5px;">{art.get('source', 'GLOBAL INSIGHT')}</p>
                <h2 style="margin-top:0;">{art.get('title')}</h2>
                <p style="color:gray; font-size:0.8rem;">Coach Intelligence Sync: {art.get('date', 'Today')}</p>
            </div>
        ''', unsafe_allow_html=True)
        
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown(art.get('content'))
        
        with col2:
            st.info("💡 **Coach Tip**\n\n将此洞察作为下一次高管周会的讨论议题。")
            st.link_button("🌐 阅读原文", art.get('link'))
            st.divider()
            st.markdown("### 📚 延伸学习")
            st.caption("关联书籍、实战课件及更多思维模型已同步至您的飞书知识库。")
