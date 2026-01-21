import streamlit as st
import json
import os
from datetime import datetime
from backend.engine import run_rize_insight, sync_global_publications

# --- 1. 基础配置与常量 ---
API_KEY = "pat_jGg7SBGnKdh5oSsb9WoByDhSTEuCYzreP4xQSPJjym27HE11vnFpyv7zQfweC4dp"
WORKFLOW_ID = "7597720250343424040"
DATA_FILE = "data/knowledge.json"

st.set_page_config(page_title="Read & Rise", layout="wide", page_icon="🏹")

# --- 2. 样式注入：打造“高端内参”质感 ---
st.markdown("""
<style>
    .insight-card { background: white; padding: 25px; border-radius: 15px; border-left: 5px solid #2563EB; margin-bottom: 20px; box-shadow: 0 2px 10px rgba(0,0,0,0.05); }
    .section-header { color: #1E293B; font-weight: 800; font-size: 18px; border-bottom: 2px solid #E2E8F0; padding-bottom: 8px; margin: 25px 0 15px 0; }
    .highlight-box { color: #2563EB; font-weight: bold; font-size: 1.2rem; margin: 15px 0; padding: 10px; border-radius: 8px; background: #EFF6FF; }
    .stAudio { margin-top: 10px; }
</style>
""", unsafe_allow_html=True)

# --- 3. 数据处理函数 ---
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            try:
                content = json.load(f)
                return content if isinstance(content, list) else []
            except: return []
    return []

def save_data(new_item):
    data = load_data()
    new_item['date'] = datetime.now().strftime("%Y-%m-%d %H:%M")
    data.insert(0, new_item) # 新内容排在最前面
    os.makedirs("data", exist_ok=True)
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# --- 4. 侧边栏：品牌与历史 ---
with st.sidebar:
    st.markdown("# 🏹 Read & Rise")
    st.caption("Your Daily Strategic Mentor")
    st.divider()
    
    st.subheader("📚 历史知识库")
    history = load_data()
    if history:
        for i, item in enumerate(history[:10]): # 显示最近10条
            if st.button(f"{item.get('title', '无标题')[:12]}...", key=f"hist_{i}"):
                st.session_state['current_article'] = item
    
    st.divider()
    if st.button("🗑️ 清空所有记录"):
        if os.path.exists(DATA_FILE):
            os.remove(DATA_FILE)
        st.rerun()

# --- 5. 主页面逻辑 ---
tab1, tab2 = st.tabs(["🏠 今日内参", "⚙️ 自动化同步"])

with tab1:
    # 优先显示点击历史记录的内容，否则显示最新的一条
    db = load_data()
    display_item = st.session_state.get('current_article') or (db[0] if db else None)

    if display_item:
        # 头部洞察卡片
        st.markdown(f"""
        <div class="insight-card">
            <p style="color:#64748B; font-size:0.8rem;">发布时间：{display_item.get('date')}</p>
            <h1 style="margin:0; font-size:2rem; color:#1E293B;">{display_item.get('title')}</h1>
            <div class="highlight-box">💡 认知爆点：{display_item.get('one_sentence', '正在生成洞察...')}</div>
            <p style="color:#64748B;">🧠 核心思维模型：<b>{display_item.get('model', '通用模型')}</b></p>
        </div>
        """, unsafe_allow_html=True)

        col_main, col_side = st.columns([2, 1])
        
        with col_main:
            st.markdown('<div class="section-header">【深度解析】</div>', unsafe_allow_html=True)
            st.write(display_item.get('content', '暂无内容'))
            
            st.markdown('<div class="section-header">🎧 Listen in English</div>', unsafe_allow_html=True)
            # 这里预留语音功能，暂时使用示例音频
            st.audio("https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3")

        with col_side:
            st.markdown('<div class="section-header">【给管理者的反思】</div>', unsafe_allow_html=True)
            reflection = display_item.get('reflection', '思考是一种最高级的劳动。')
            st.info(reflection)
            
            if display_item.get('url'):
                st.markdown(f"[🔗 阅读外刊原文]({display_item['url']})")
    else:
        st.info("👋 欢迎来到 Read & Rise。目前知识库为空，请点击上方 '自动化同步' 按钮获取今日全球外刊资讯。")

with tab2:
    st.header("⚙️ 内容同步引擎")
    
    c1, c2 = st.columns(2)
    
    with c1:
        st.subheader("方式 A：精准研究")
        custom_topic = st.text_input("输入您感兴趣的商业/技术主题")
        if st.button("🚀 启动专项抓取"):
            if custom_topic:
                with st.spinner(f"正在为您生成关于 '{custom_topic}' 的深度内参..."):
                    res = run_rize_insight(custom_topic, API_KEY, WORKFLOW_ID)
                    if res:
                        save_data(res)
                        st.success("同步成功！")
                        st.rerun()
            else:
                st.warning("请输入主题")

    with c2:
        st.subheader("方式 B：全球同步")
        st.write("自动从 HBR, Economist, McKinsey, MIT 抓取最新外刊并由 AI 拆解。")
        if st.button("🌐 一键同步全球外刊"):
            with st.spinner("正在爬取全球外刊库并进行深度加工..."):
                try:
                    results = sync_global_publications(API_KEY, WORKFLOW_ID)
                    if results:
                        for r in results:
                            save_data(r)
                        st.success(f"成功更新 {len(results)} 篇全球深度洞察！")
                        st.rerun()
                    else:
                        st.error("同步失败，请检查 Crawler 逻辑或 API 额度。")
                except Exception as e:
                    st.error(f"运行出错: {e}")
