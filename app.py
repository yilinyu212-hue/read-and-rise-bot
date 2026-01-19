import streamlit as st
import json
import os
import requests
import plotly.graph_objects as go
from datetime import datetime

# --- 页面基础配置 ---
st.set_page_config(
    page_title="Read & Rise | Executive Decision Support",
    layout="wide",
    page_icon="🏹",
    initial_sidebar_state="expanded"
)

# --- 样式定制 (高管深邃蓝风格) ---
st.markdown("""
    <style>
    .main-card { background: #0F172A; padding: 25px; border-radius: 15px; color: white; border-left: 10px solid #38BDF8; margin-bottom: 20px; }
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] { background-color: #F8FAFC; border-radius: 5px; padding: 10px; border: 1px solid #E2E8F0; }
    .stTabs [aria-selected="true"] { background-color: #38BDF8 !important; color: white !important; }
    .stat-box { background: #F8FAFC; padding: 15px; border-radius: 10px; border: 1px solid #E2E8F0; text-align: center; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# --- 1. 数据持久化逻辑 ---
def load_data():
    if not os.path.exists("data.json"):
        return {"briefs": [], "books": [], "update_time": ""}
    with open("data.json", "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except:
            return {"briefs": [], "books": [], "update_time": ""}

def save_data(d):
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False, indent=4)

data = load_data()

# --- 2. AI Coach 核心逻辑 (联动智库资产) ---
def call_coach(user_input, active_art):
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        return "⚠️ Coach 离线：API Key 未配置。请联系管理员。"
    
    # 提取智库资产作为 AI 背景背景
    assets_context = "\n".join([f"模型:{b['concept']} - 洞察:{b['insight']}" for b in data.get("books", [])])
    
    prompt = f"""
    你是 Read & Rise 专属 AI 战略教练。
    [背景文章]: {active_art['title']} | 摘要: {active_art.get('cn_summary')}
    [用户智库资产]: {assets_context}
    
    请结合上述文章内容以及用户的智库资产，给出具有实战意义的回复。不要说废话，直接给管理建议或决策逻辑。
    """
    
    try:
        res = requests.post("https://api.deepseek.com/chat/completions", 
            headers={"Authorization": f"Bearer {api_key}"},
            json={
                "model": "deepseek-chat",
                "messages": [
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": user_input}
                ], "temperature": 0.5
            }, timeout=30)
        return res.json()['choices'][0]['message']['content']
    except:
        return "⚠️ 连接超时，AI 教练正在思考，请稍后再试。"

# --- 3. 雷达图组件 ---
def draw_radar(scores):
    if not scores: scores = {"战略":50,"创新":50,"洞察":50,"组织":50,"执行":50}
    fig = go.Figure(data=go.Scatterpolar(
        r=list(scores.values()) + [list(scores.values())[0]],
        theta=list(scores.keys()) + [list(scores.keys())[0]],
        fill='toself',
        line=dict(color='#38BDF8')
    ))
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
        showlegend=False, height=350, margin=dict(l=40, r=40, t=40, b=40)
    )
    return fig

# --- 4. 侧边导航栏 ---
st.sidebar.title("🏹 Read & Rise")
st.sidebar.caption("Executive Digital Brain v2.0")
menu = st.sidebar.radio("菜单导航", ["🏠 Dashboard", "🚀 全球快报", "📚 资产智库", "⚙️ 资产入库"])

# --- 🏠 Dashboard (首页) ---
if menu == "🏠 Dashboard":
    st.markdown('<p style="font-size: 2.5rem; font-weight: 800; color: #1E293B; margin-bottom: 0px;">Hi, Leaders! 👋</p>', unsafe_allow_html=True)
    st.write(f"今天是 {datetime.now().strftime('%Y年%m月%d日')}。今日全球商业内参已为您提炼完成。")

    # 🎙️ 音频播报区域
    st.markdown("""
        <div class="main-card">
            <p style="color:#38BDF8; font-size:0.8rem; font-weight:bold; margin-bottom:5px;">STRATEGIC AUDIO SESSION</p>
            <h3 style="margin:0; color:white;">每日商业简报 (BBC Style)</h3>
            <p style="opacity:0.8; font-size:0.9rem; margin-top:5px;">3分钟为您梳理今日麦肯锡、HBR、经济学人核心决策点。</p>
        </div>
    """, unsafe_allow_html=True)
    
    if os.path.exists("daily_briefing.mp3"):
        st.audio("daily_briefing.mp3")
    else:
        st.info("🕒 今日音频简报正在由 AI 合成，请稍后刷新...")

    st.divider()

    col1, col2 = st.columns([0.6, 0.4])
    with col1:
        st.subheader("🧩 今日决策维度建模")
        if data.get("briefs"):
            st.plotly_chart(draw_radar(data["briefs"][0].get("model_scores")), use_container_width=True)
        else:
            st.info("暂无今日数据，请运行同步任务。")
    with col2:
        st.subheader("📊 智库概览")
        c1, c2 = st.columns(2)
        c1.metric("已入库资产", len(data.get("books", [])))
        c2.metric("今日快报数", len(data.get("briefs", [])))
        st.divider()
        st.write("**管理者必读建议：**")
        st.success("1. 重点关注 AI 导致的成本结构优化\n2. 评估离岸供应链的韧性风险")

# --- 🚀 全球快报 (核心：左读右聊) ---
elif menu == "🚀 全球快报":
    col_l, col_r = st.columns([0.55, 0.45])
    
    with col_l:
        st.header("🌍 Global Intelligence")
        if not data.get("briefs"):
            st.warning("暂无快报数据，请检查爬虫运行状态。")
        for i, art in enumerate(data.get("briefs", [])):
            with st.expander(f"📍 {art['source']} | {art['title']}", expanded=(i==0)):
                tab1, tab2, tab3, tab4 = st.tabs(["💡 摘要", "🔎 案例", "🧠 反思", "📖 词汇"])
                with tab1:
                    for s in art.get('cn_summary', []): st.write(f"• {s}")
                with tab2:
                    st.write(art.get('case_study', '暂无案例解析'))
                with tab3:
                    for r in art.get('reflection_flow', []): st.write(f"❓ {r}")
                with tab4:
                    for v in art.get('vocab_bank', []):
                        st.markdown(f"**{v['word']}**: {v['meaning']}  \n*Ex: {v['example']}*")
                
                if st.button("🎙️ 呼叫 Coach 深度解析", key=f"coach_btn_{i}"):
                    st.session_state.active_art = art
                    st.session_state.chat_history = []

    with col_r:
        st.header("🎙️ AI Coach Session")
        if "active_art" in st.session_state:
            active_art = st.session_state.active_art
            st.info(f"正在对话：《{active_art['title']}》")
            
            chat_container = st.container(height=550, border=True)
            if "chat_history" not in st.session_state: st.session_state.chat_history = []
            
            for m in st.session_state.chat_history:
                with chat_container.chat_message(m["role"]): st.write(m["content"])
            
            if p := st.chat_input("针对此文，您有什么管理上的疑问？"):
                st.session_state.chat_history.append({"role": "user", "content": p})
                with chat_container.chat_message("user"): st.write(p)
                
                with chat_container.chat_message("assistant"):
                    response = call_coach(p, active_art)
                    st.write(response)
                    st.session_state.chat_history.append({"role": "assistant", "content": response})
        else:
            st.info("请从左侧选择文章并点击【呼叫 Coach】开始实战对话。")

# --- 📚 资产智库 ---
elif menu == "📚 资产智库":
    st.header("📚 数字智库资产")
    st.write("这些是您录入的底层管理逻辑，AI 会将其应用在每一次对话中。")
    if not data.get("books"):
        st.info("目前智库为空，请前往录入。")
    for b in data.get("books", []):
        with st.container(border=True):
            st.subheader(f"📖 {b['title']}")
            st.markdown(f"**管理逻辑**: `{b['concept']}`")
            st.write(f"**深度洞察**: {b['insight']}")

# --- ⚙️ 资产入库 ---
elif menu == "⚙️ 资产入库":
    st.header("⚙️ 资产数字化中心")
    st.write("将您读过的经典书籍、学过的管理课或建立的个人思维模型输入此处。")
    
    with st.form("add_asset"):
        t = st.text_input("资产名称 (如:《高效能人士的七个习惯》/ 第一性原理)")
        c = st.text_input("核心管理逻辑 (Short Summary)")
        i = st.text_area("个人洞察 (AI 在对话时应参考的知识点)")
        if st.form_submit_button("永久入库数据"):
            if t:
                data["books"].append({"title": t, "concept": c, "insight": i})
                save_data(data)
                st.success(f"资产《{t}》已成功数字化入库。")
