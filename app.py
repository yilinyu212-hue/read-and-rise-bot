import streamlit as st
import streamlit.components.v1 as components
import json, os, requests
from datetime import datetime

# --- 1. 配置与全局 AI Coach ---
st.set_page_config(page_title="Read & Rise", layout="wide", page_icon="🏹")

# 你的 Mentor Rize 会以右下角悬浮球形式出现
components.html("""
<script src="https://lf-cdn.coze.cn/obj/unpkg/flow-platform/chat-app-sdk/1.1.0-beta.3/libs/cn/index.js"></script>
<script>
  new CozeWebSDK.WebChatClient({ config: { bot_id: '7597670461476421647' } }); # 👈 填入BotID
</script>
""", height=0)

# --- 2. 数据处理 (修复数据丢失问题) ---
def load_data():
    if os.path.exists("data.json"):
        with open("data.json", "r", encoding="utf-8") as f:
            try:
                res = json.load(f)
                # 兼容不同格式，确保音频和内容都能读到
                return res.get("items", []) if isinstance(res, dict) else res
            except: return []
    return []

def call_coze(topic):
    # 解决 "auth type (unauth)" 报错的关键
    API_KEY = "pat_DNy8zk5DxAsNDzVEIxkzweVaXo9hic4fDPagIAUjoepgLK2zL3bub16Mp3RxvsRY" # 👈 填入你在截图 c5d627cd 生成的 pat_...
    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
    payload = {"workflow_id": "7597720250343424040", "parameters": {"input": topic}}
    try:
        res = requests.post("https://api.coze.cn/v1/workflow/run", headers=headers, json=payload)
        return res.json().get('data')
    except: return None

# --- 3. 页面样式 ---
st.markdown("""
<style>
    .hero { background: #0F172A; padding: 40px; border-radius: 20px; color: white; margin-bottom: 20px; }
    .card { background: white; padding: 20px; border-radius: 15px; border: 1px solid #E2E8F0; margin-bottom: 15px; }
</style>
""", unsafe_allow_html=True)

# --- 4. 导航控制 ---
items = load_data()
with st.sidebar:
    st.title("🏹 Read & Rise")
    page = st.radio("前往", ["🏠 Dashboard", "🚀 Intelligence Hub", "📚 Bookshelf", "🛠 Admin"])

# --- 5. 页面逻辑实现 ---

# A. 首页：Hi, Leader!
if page == "🏠 Dashboard":
    st.markdown(f'<div class="hero"><h1>Hi, Leader! 👋</h1><p>Today: {datetime.now().strftime("%Y-%m-%d")}</p></div>', unsafe_allow_html=True)
    if items:
        st.subheader("今日重点思维模型")
        st.success(f"核心推荐：{items[0].get('mental_model', '第一性原理')}")
        st.divider()
        st.subheader("今日必读外刊")
        for it in items[:2]: # 首页展示前两篇
            st.markdown(f'<div class="card"><h3>{it.get("cn_title")}</h3><p>{it.get("cn_analysis")[:150]}...</p></div>', unsafe_allow_html=True)

# B. 外刊详情页：左 Read 右 Rise
elif page == "🚀 Intelligence Hub":
    if items:
        sel = st.selectbox("选择文章", [i.get('cn_title') for i in items])
        it = next(i for i in items if i.get('cn_title') == sel)
        
        col_read, col_rise = st.columns(2)
        with col_read:
            st.markdown("### 📖 Read (总结)")
            st.info(f"**English:**\n\n{it.get('en_summary')}")
            st.success(f"**中文总结:**\n\n{it.get('cn_analysis')}")
            if it.get('audio_file'): st.audio(it['audio_file']) # 恢复音频功能
        with col_rise:
            st.markdown("### 📈 Rise (深度拆解)")
            st.warning(f"**思维模型：{it.get('mental_model')}**")
            st.write(it.get('cn_analysis'))
            st.button("🧠 针对此文咨询 Coach")

# C. 书籍推荐栏目
elif page == "📚 Bookshelf":
    st.title("📚 Bookshelf")
    st.info("书籍推荐模块正在同步中，即将推出领导力必读书单...")

# D. 后台自动化
elif page == "🛠 Admin":
    st.title("🛠 自动化内容更新")
    topic = st.text_input("输入今日主题")
    if st.button("运行扣子自动写稿"):
        # 这里会去运行工作流并更新 data.json
        res_text = call_coze(topic)
        if res_text:
            st.success("抓取成功！请检查 data.json")
