import streamlit as st
import streamlit.components.v1 as components
import json, os, requests
from datetime import datetime

# --- 1. 页面配置与 Coach 悬浮球 ---
st.set_page_config(page_title="Read & Rise | 管理者内参", layout="wide", page_icon="🏹")

components.html(f"""
<script src="https://lf-cdn.coze.cn/obj/unpkg/flow-platform/chat-app-sdk/1.1.0-beta.3/libs/cn/index.js"></script>
<script>
  new CozeWebSDK.WebChatClient({{
    config: {{ bot_id: '7597670461476421647' }},
    componentProps: {{ title: 'Mentor Rize Coach' }},
    ui: {{ base: {{ zIndex: 1000 }}, chatButton: {{ title: '咨询 Coach' }} }}
  }});
</script>
""", height=0)

# --- 2. 身份认证与 API 配置 ---
# 这里的 Token 和 Workflow ID 已根据你的提供填入
API_KEY = "pat_jGg7SBGnKdh5oSsb9WoByDhSTEuCYzreP4xQSPJjym27HE11vnFpyv7zQfweC4dp"
WORKFLOW_ID = "7597720250343424040"

def load_data():
    if os.path.exists("data.json"):
        with open("data.json", "r", encoding="utf-8") as f:
            try:
                res = json.load(f)
                return res.get("items", []) if isinstance(res, dict) else res
            except: return []
    return []

def save_data(items):
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump({"items": items}, f, ensure_ascii=False, indent=4)

# --- 3. UI 样式 ---
st.markdown("""
<style>
    .stApp { background-color: #F8FAFC; }
    [data-testid="stSidebar"] { background-color: #F1F5F9; border-right: 1px solid #E2E8F0; }
    .article-text { line-height: 1.8 !important; font-size: 16px; color: #334155; letter-spacing: 0.5px; }
    .content-card { background: white; padding: 24px; border-radius: 12px; border: 1px solid #E2E8F0; box-shadow: 0 4px 12px rgba(0,0,0,0.03); margin-bottom: 20px; }
    .section-header { font-weight: 800; color: #1E293B; border-left: 4px solid #3B82F6; padding-left: 12px; margin-bottom: 15px; }
</style>
""", unsafe_allow_html=True)

items = load_data()

# --- 4. 导航 ---
with st.sidebar:
    st.markdown("<h2 style='color: #1E293B;'>🏹 Read & Rise</h2>", unsafe_allow_html=True)
    st.caption("专注领导力进阶与外刊深度研读")
    st.divider()
    page = st.radio("前往专区", ["🏠 Dashboard", "🚀 Intelligence Hub", "📚 决策书架", "⚙️ 后台同步"])
    st.divider()
    if items:
        st.success(f"已收录: {len(items)} 篇深度拆解")

# --- 5. 页面实现 ---
if page == "🏠 Dashboard":
    st.markdown("<h1 style='color: #1E293B;'>Hi, Leader!</h1>", unsafe_allow_html=True)
    st.markdown(f"**{datetime.now().strftime('%m月%d日')}** · 开启你的全天候智囊团")
    if items:
        latest = items[0]
        st.markdown(f"""
        <div class="content-card">
            <p style='color:#64748B; font-size:13px; text-transform:uppercase;'>今日核心模型</p>
            <h2 style='color:#2563EB; margin:0;'>{latest.get('mental_model', '第一性原理')}</h2>
            <p style='color:#475569; margin-top:10px;'>{latest.get('cn_title')} · 深度解析已就绪</p>
        </div>
        """, unsafe_allow_html=True)
        st.subheader("🗓 历史研读回顾")
        for it in items:
            with st.expander(f"【{it.get('date', '2026-01-21')}】 {it.get('cn_title')}"):
                st.write(it.get('cn_analysis', '')[:120] + "...")
                if st.button("进入全文", key=it.get('cn_title')):
                    st.info("请切换到 Intelligence Hub 页面查看")

elif page == "🚀 Intelligence Hub":
    if items:
        sel = st.selectbox("浏览历史研读清单", [i.get('cn_title') for i in items])
        it = next(i for i in items if i.get('cn_title') == sel)
        st.markdown(f"<h1 style='color: #1E293B;'>{it.get('cn_title')}</h1>", unsafe_allow_html=True)
        col_read, col_rise = st.columns([1, 1], gap="large")
        with col_read:
            st.markdown('<div class="section-header">READ | 外刊精华</div>', unsafe_allow_html=True)
            if it.get('audio_file'): st.audio(it['audio_file'])
            st.markdown(f'<div class="content-card article-text"><b>Summary:</b><br>{it.get("en_summary")}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="article-text">{it.get("cn_analysis")}</div>', unsafe_allow_html=True)
        with col_rise:
            st.markdown('<div class="section-header">RISE | 管理启发</div>', unsafe_allow_html=True)
            st.info(f"**本篇思维模型：{it.get('mental_model')}**")
            st.markdown("💡 **管理挑战点**：\n1. 如何
