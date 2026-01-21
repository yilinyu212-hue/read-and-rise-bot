import streamlit as st
import json
import os
from datetime import datetime
# 确保 backend 文件夹下有 __init__.py 文件，否则这里会报错
from backend.engine import run_rize_insight, sync_global_publications

# --- 1. 配置区域 ---
API_KEY = "pat_jGg7SBGnKdh5oSsb9WoByDhSTEuCYzreP4xQSPJjym27HE11vnFpyv7zQfweC4dp"
WORKFLOW_ID = "7597720250343424040"
DATA_FILE = "data/knowledge.json"

st.set_page_config(page_title="Read & Rise", layout="wide", page_icon="🏹")

# --- 2. 样式美化 ---
st.markdown("""
<style>
    .insight-card { background: white; padding: 25px; border-radius: 15px; border-left: 5px solid #2563EB; margin-bottom: 20px; box-shadow: 0 2px 10px rgba(0,0,0,0.05); }
    .section-header { color: #1E293B; font-weight: 800; font-size: 18px; border-bottom: 2px solid #E2E8F0; padding-bottom: 8px; margin: 25px 0 15px 0; }
    .highlight-box { color: #2563EB; font-weight: bold; font-size: 1.1rem; margin: 15px 0; padding: 12px; border-radius: 8px; background: #EFF6FF; border: 1px solid #DBEAFE; }
</style>
""", unsafe_allow_html=True)

# --- 3. 数据函数 ---
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            try: return json.load(f)
            except: return []
    return []

def save_all_data(items):
    data = load_data()
    for item in reversed(items): # 保持时间顺序
        item['date'] = datetime.now().strftime("%Y-%m-%d %H:%M")
        data.insert(0, item)
    os.makedirs("data", exist_ok=True)
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# --- 4. 侧边栏 ---
with st.sidebar:
    st.title("🏹 Read & Rise")
    st.caption("Read Daily, Rise Strategic")
    st.divider()
    st.subheader("📚 历史库")
    db = load_data()
    for i, item in enumerate(db[:8]):
        if st.button(f"{item.get('title')[:15]}...", key=f"side_{i}"):
            st.session_state['selected_article'] = item

# --- 5. 主界面逻辑 ---
tab1, tab2 = st.tabs(["🏠 今日内参", "⚙️ 自动化同步"])

with tab1:
    article = st.session_state.get('selected_article') or (db[0] if db else None)
    
    if article:
        st.markdown(f"""
        <div class="insight-card">
            <h1 style="color:#1E293B;">{article.get('title')}</h1>
            <div class="highlight-box">💡 认知爆点：{article.get('one_sentence', '正在萃取洞察...')}</div>
            <p style="color:#64748B;">🧠 思维模型：<b>{article.get('model', '通用管理模型')}</b></p>
        </div>
        """, unsafe_allow_html=True)
        
        col_l, col_r = st.columns([2, 1])
        with col_l:
            st.markdown('<div class="section-header">【深度解析】</div>', unsafe_allow_html=True)
            st.write(article.get('content'))
            st.markdown('<div class="section-header">🎧 Listen in English</div>', unsafe_allow_html=True)
            st.audio("https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3")
        with col_r:
            st.markdown('<div class="section-header">【管理反思】</div>', unsafe_allow_html=True)
            st.info(article.get('reflection', '思考是管理者的核心工作。'))
    else:
        st.info("尚未同步内容，请切换到同步页面。")

with tab2:
    st.header("⚙️ 内容生产引擎")
    c1, c2 = st.columns(2)
    
    with c1:
        st.subheader("方式 A：精准研究")
        topic = st.text_input("输入研究主题")
        if st.button("🚀 专项同步"):
            with st.spinner("AI 正在解析..."):
                res = run_rize_insight(topic, API_KEY, WORKFLOW_ID)
                if res:
                    save_all_data([res])
                    st.success("同步成功！")
                    st.rerun()

    with c2:
        st.subheader("方式 B：全球同步")
        st.write("一键抓取 HBR / Economist / McKinsey / MIT")
        # --- 重点：这就是你找的按钮 ---
        if st.button("🌐 一键同步全球外刊"):
            with st.spinner("正在爬取全球顶级外刊并进行 AI 拆解..."):
                try:
                    results = sync_global_publications(API_KEY, WORKFLOW_ID)
                    if results:
                        save_all_data(results)
                        st.success(f"同步完成！已入库 {len(results)} 篇。")
                        st.rerun()
                except Exception as e:
                    st.error(f"同步出错: {e}")
