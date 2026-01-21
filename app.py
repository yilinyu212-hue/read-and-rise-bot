cat << 'EOF' > app.py
import streamlit as st
from backend.engine import run_rize_insight
import json, os

st.set_page_config(page_title="Read & Rise", layout="wide", page_icon="🏹")

# 模拟样式
st.markdown("""
<style>
    .insight-card { background: white; padding: 25px; border-radius: 15px; border-left: 5px solid #2563EB; margin-bottom: 20px; box-shadow: 0 2px 10px rgba(0,0,0,0.05); }
    .section-header { color: #1E293B; font-weight: 800; font-size: 18px; border-bottom: 2px solid #E2E8F0; padding-bottom: 8px; margin: 25px 0 15px 0; }
</style>
""", unsafe_allow_html=True)

def load_data():
    if os.path.exists("data/knowledge.json"):
        with open("data/knowledge.json", "r") as f: return json.load(f)
    return []

# --- 侧边栏 ---
with st.sidebar:
    st.title("🏹 Read & Rise")
    st.caption("Your daily strategic mentor")
    if st.button("🗑️ 清空历史记录"):
        with open("data/knowledge.json", "w") as f: json.dump([], f)
        st.rerun()

# --- 主页面 ---
tab1, tab2 = st.tabs(["🏠 今日内参", "⚙️ 后台同步"])

with tab1:
    db = load_data()
    if db:
        today = db[0]
        st.markdown(f"""
        <div class="insight-card">
            <h1 style="margin:0; font-size:28px;">{today.get('title')}</h1>
            <p style="color:#2563EB; font-weight:bold; margin:10px 0;">💡 认知爆点：{today.get('one_sentence', '认知升级中...')}</p>
            <p style="color:#64748B; font-size:14px;">🧠 核心思维模型：{today.get('model')}</p>
        </div>
        """, unsafe_allow_html=True)

        c1, c2 = st.columns([2, 1])
        with c1:
            st.markdown('<div class="section-header">【深度解析】</div>', unsafe_allow_html=True)
            st.write(today.get('content'))
            st.markdown('<div class="section-header">🎧 Listen in English</div>', unsafe_allow_html=True)
            st.audio("[https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3](https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3)") 
        with c2:
            st.markdown('<div class="section-header">【给管理者的反思】</div>', unsafe_allow_html=True)
            st.info(today.get('reflection', '思考是一种最高级的劳动。'))
    else:
        st.warning("请前往后台同步。")

with tab2:
    topic = st.text_input("输入今日研究主题")
    if st.button("🚀 启动全球抓取"):
        with st.spinner("Mentor Rize 正在调取全球数据库..."):
            res = run_rize_insight(topic, "pat_jGg7SBGnKdh5oSsb9WoByDhSTEuCYzreP4xQSPJjym27HE11vnFpyv7zQfweC4dp", "7597720250343424040")
            if res:
                data = load_data()
                res['date'] = "2026-01-21" # 也可以用 datetime
                data.insert(0, res)
                with open("data/knowledge.json", "w") as f: json.dump(data, f)
                st.success("同步完成！")
                st.rerun()
EOF
