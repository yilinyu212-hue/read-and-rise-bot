import streamlit as st
import streamlit.components.v1 as components
import json, os, requests
from datetime import datetime

# --- 1. 配置与 AI Coach 全局悬浮球 ---
st.set_page_config(page_title="Read & Rise", layout="wide", page_icon="🏹")

# 这里填入你的 Bot ID，网页右下角就会出现 Coach 悬浮球
components.html("""
<script src="https://lf-cdn.coze.cn/obj/unpkg/flow-platform/chat-app-sdk/1.1.0-beta.3/libs/cn/index.js"></script>
<script>
  new CozeWebSDK.WebChatClient({ config: { bot_id: '7597670461476421647' }, 
  componentProps: { title: 'Mentor Rize' } });
</script>
""", height=0)

# --- 2. 核心数据与 API 函数 ---
def load_data():
    if os.path.exists("data.json"):
        with open("data.json", "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
                return data.get("items", []) if isinstance(data, dict) else data
            except: return []
    return []

def call_coze_workflow(topic):
    # 这里填入你在“添加令牌”页面生成的 pat_... 令牌
    API_KEY = "pat_DNy8zk5DxAsNDzVEIxkzweVaXo9hic4fDPagIAUjoepgLK2zL3bub16Mp3RxvsRY" 
    WORKFLOW_ID = "pat_eaOALk7CRZrn8psvXRZ3erf7hiwnrgHoFmoq4erzqVg7sCVloqAU1ov5G7fb9Xar"
    url = "https://api.coze.cn/v1/workflow/run"
    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
    payload = {"workflow_id": WORKFLOW_ID, "parameters": {"input": topic}}
    try:
        res = requests.post(url, headers=headers, json=payload)
        return res.json().get('data')
    except: return None

# 初始化
if "page" not in st.session_state: st.session_state.page = "🏠 Dashboard"
items = load_data()

# --- 3. 样式定制 ---
st.markdown("""
<style>
    .main { background-color: #F8FAFC; }
    .hero-card { background: linear-gradient(135deg, #0F172A 0%, #1E293B 100%); padding: 40px; border-radius: 24px; color: white; margin-bottom: 30px; }
    .content-card { background: white; padding: 25px; border-radius: 20px; border: 1px solid #E2E8F0; margin-bottom: 20px; transition: 0.3s; }
    .content-card:hover { transform: translateY(-5px); box-shadow: 0 12px 20px rgba(0,0,0,0.05); }
    .chip { padding: 4px 12px; border-radius: 6px; font-weight: bold; font-size: 12px; }
</style>
""", unsafe_allow_html=True)

# --- 4. 侧边栏导航 ---
with st.sidebar:
    st.title("🏹 Read & Rise")
    if st.button("🏠 Dashboard (今日重点)", use_container_width=True): st.session_state.page = "🏠 Dashboard"
    if st.button("🚀 Intelligence Hub (外刊)", use_container_width=True): st.session_state.page = "🚀 Intelligence Hub"
    if st.button("📚 Bookshelf (书籍推荐)", use_container_width=True): st.session_state.page = "📚 Bookshelf"
    st.divider()
    if st.button("⚙️ Admin"): st.session_state.page = "Admin"

# --- 5. 页面内容 ---

# A. 首页 Dashboard
if st.session_state.page == "🏠 Dashboard":
    st.markdown(f'<div class="hero-card"><h1>Hi, Leader! 👋</h1><p>Today is {datetime.now().strftime("%Y-%m-%d")}</p><h3>今日核心模型：{items[0].get("mental_model") if items else "加载中..."}</h3></div>', unsafe_allow_html=True)
    st.subheader("📌 今日重点研读")
    cols = st.columns(2)
    for idx, it in enumerate(items[:2]):
        with cols[idx]:
            st.markdown(f'<div class="content-card"><h4>{it.get("cn_title")}</h4><p>{it.get("cn_analysis")[:100]}...</p></div>', unsafe_allow_html=True)

# B. 外刊页面 (Intelligence Hub)
elif st.session_state.page == "🚀 Intelligence Hub":
    if items:
        sel = st.selectbox("选择文章", [i.get('cn_title') for i in items])
        it = next(i for i in items if i.get('cn_title') == sel)
        
        st.title(it.get('cn_title'))
        col_read, col_rise = st.columns(2)
        with col_read:
            st.subheader("📖 Read (外刊总结)")
            st.info(f"**English:**\n{it.get('en_summary')}")
            st.success(f"**中文:**\n{it.get('cn_analysis')}")
            if it.get('audio_file'): st.audio(it['audio_file']) # 恢复你的音频功能
        with col_rise:
            st.subheader("📈 Rise (深度拆解)")
            st.warning(f"**思维模型：{it.get('mental_model')}**")
            st.write(it.get('cn_analysis'))
            if st.button("🧠 就此文咨询 Coach"):
                st.toast("请点击右下角悬浮球开始对话")

# C. 管理后台 (用于自动生成文章)
elif st.session_state.page == "Admin":
    st.title("🛠 后台管理")
    topic = st.text_input("输入今日主题")
    if st.button("🚀 运行扣子一键生成"):
        res = call_coze_workflow(topic)
        if res:
            new_item = json.loads(res)
            items.insert(0, new_item)
            with open("data.json", "w", encoding="utf-8") as f:
                json.dump({"items": items}, f, ensure_ascii=False)
            st.success("更新成功！")
