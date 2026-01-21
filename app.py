import streamlit as st
import streamlit.components.v1 as components
import json, os, requests
from datetime import datetime

# --- 1. 页面配置与 Coach 悬浮球 ---
st.set_page_config(page_title="Read & Rise | Executive Insight", layout="wide", page_icon="🏹")

# 你的 Bot ID: 7597670461476421647
components.html(f"""
<script src="https://lf-cdn.coze.cn/obj/unpkg/flow-platform/chat-app-sdk/1.1.0-beta.3/libs/cn/index.js"></script>
<script>
  new CozeWebSDK.WebChatClient({{
    config: {{ bot_id: '7597670461476421647' }},
    componentProps: {{ title: 'Mentor Rize Coach' }},
    ui: {{ base: {{ zIndex: 1000 }} }}
  }});
</script>
""", height=0)

# --- 2. 身份认证与 API 配置 ---
API_KEY = "pat_DNy8zk5DxAsNDzVEIxkzweVaXo9hic4fDPagIAUjoepgLK2zL3bub16Mp3RxvsRY" # 👈 填入 pat_ 开头的 Token
WORKFLOW_ID = "7597720250343424040" # 👈 填入工作流 ID

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

# --- 3. 高管级视觉 UI 设计 ---
st.markdown("""
<style>
    .stApp { background-color: #F4F7F9; }
    [data-testid="stSidebar"] { background-color: #0F172A; color: white; }
    .main-title { font-size: 32px; font-weight: 800; color: #1E293B; margin-bottom: 5px; }
    .quote-card { background: white; padding: 25px; border-radius: 15px; border-left: 5px solid #3B82F6; box-shadow: 0 4px 6px rgba(0,0,0,0.05); margin-bottom: 20px; }
    .metric-box { background: #E2E8F0; padding: 10px 20px; border-radius: 10px; font-weight: bold; display: inline-block; margin-right: 10px; }
    .executive-summary { line-height: 1.8; color: #334155; font-size: 16px; }
</style>
""", unsafe_allow_html=True)

items = load_data()

# --- 4. 侧边栏导航 ---
with st.sidebar:
    st.markdown("<h1 style='color:white;'>🏹 Read & Rise</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color:#94A3B8;'>探索全球视野，重塑管理心智</p>", unsafe_allow_html=True)
    page = st.radio("导航菜单", ["🏠 每日简报", "🚀 深度外刊", "📚 决策书库", "⚙️ 内容管理"])
    st.divider()
    st.caption("版本: V2.0 High-End Edition")

# --- 5. 页面逻辑 ---

# A. 首页 Dashboard: 去掉文字堆砌，强调“关键模型”
if page == "🏠 每日简报":
    st.markdown('<p class="main-title">Morning, Leader! 👋</p>', unsafe_allow_html=True)
    st.caption(f"今天是 {datetime.now().strftime('%Y-%m-%d')} | 建议阅读时间: 5分钟")
    
    if items:
        latest = items[0]
        st.markdown(f"""
        <div class="quote-card">
            <div style="color:#64748B; font-size:12px; margin-bottom:10px;">今日核心思维模型</div>
            <div style="font-size:24px; font-weight:bold; color:#1E40AF;">{latest.get('mental_model', '第一性原理')}</div>
            <p style="margin-top:10px; color:#475569;">建议应用场景：处理复杂决策或战略转折期。</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.subheader("📌 历史简报库 (按日期)")
        for it in items:
            with st.expander(f"📅 {it.get('date', '2026-01-21')} | {it.get('cn_title')}"):
                st.write(it.get('cn_analysis', '')[:150] + "...")
                if st.button("进入研读", key=it.get('cn_title')):
                    st.info("请前往「深度外刊」页面查看完整版")

# B. 外刊页面: 仿《经济学人》排版，左Read右Rise
elif page == "🚀 深度外刊":
    if items:
        sel = st.selectbox("选择要审阅的文章", [i.get('cn_title') for i in items])
        it = next(i for i in items if i.get('cn_title') == sel)
        
        st.markdown(f"## {it.get('cn_title')}")
        
        col1, col2 = st.columns([1, 1], gap="large")
        with col1:
            st.markdown("#### 📖 READ | 事实洞察")
            # 自动生成摘要卡片，避免文字密集
            st.success(f"**核心摘要 (Executive Summary):**\n\n{it.get('en_summary', '')[:200]}...")
            if it.get('audio_file'): st.audio(it['audio_file'])
            st.divider()
            st.markdown(f'<div class="executive-summary">{it.get("cn_analysis")}</div>', unsafe_allow_html=True)
            
        with col2:
            st.markdown("#### 📈 RISE | 决策启发")
            st.warning(f"**底层逻辑：{it.get('mental_model')}**")
            # 这里可以放你工作流里的“教练点评”部分
            st.markdown("""
            **管理者挑战：**
            * 如何在信息不对称时做决定？
            * 此模型如何应用于本周的团队会议？
            """)
            st.markdown("---")
            st.button("🧠 呼叫 Mentor Rize 深度对谈")
    else:
        st.warning("暂无内容，请先在管理后台更新。")

# C. 决策书库: 书架
elif page == "📚 决策书库":
    st.markdown('<p class="main-title">📚 决策书库</p>', unsafe_allow_html=True)
    st.info("专为中高层定制的「场景化书单」正在加载...")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        <div class="quote-card">
            <h4>《反脆弱》</h4>
            <p>管理者必读：如何在波动中获益？</p>
            <small>关联模型：反脆弱思维</small>
        </div>
        """, unsafe_allow_html=True)
    with col2:
         st.markdown("""
        <div class="quote-card">
            <h4>《有限与无限的游戏》</h4>
            <p>战略眼光：重新定义你的竞争格局。</p>
            <small>关联模型：博弈论</small>
        </div>
        """, unsafe_allow_html=True)

# D. 内容管理: 自动化抓取
elif page == "⚙️ 内容管理":
    st.title("🛠 系统后台")
    topic = st.text_input("请输入今日研究课题（例如：全球半导体格局、马斯克的人才观）")
    if st.button("🚀 启动 AI 自动写稿任务"):
        headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
        payload = {"workflow_id": WORKFLOW_ID, "parameters": {"input": topic}}
        
        with st.spinner("AI 正在扫描全球动态并拆解思维模型..."):
            res = requests.post("https://api.coze.cn/v1/workflow/run", headers=headers, json=payload)
            if res.status_code == 200:
                try:
                    raw_data = res.json().get('data')
                    new_article = json.loads(raw_data)
                    new_article['date'] = datetime.now().strftime('%Y-%m-%d')
                    items.insert(0, new_article)
                    save_data(items)
                    st.success("✨ 今日简报已生成，请前往 Dashboard 查看！")
                except Exception as e:
                    st.error(f"解析失败：{str(e)}")
            else:
                st.error("连接扣子失败，请检查 API Token。")
