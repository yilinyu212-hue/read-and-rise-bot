import streamlit as st
import json
import os
import requests
import plotly.graph_objects as go
from datetime import datetime

# --- 1. 基础配置与样式 ---
st.set_page_config(page_title="Read & Rise | Executive Brain", layout="wide", page_icon="🏹")

st.markdown("""
    <style>
    .main-card { background: #0F172A; padding: 25px; border-radius: 15px; color: white; border-left: 10px solid #38BDF8; margin-bottom: 20px; }
    .stChatFloatingInputContainer { bottom: 20px; }
    .asset-card { background: #F8FAFC; padding: 15px; border-radius: 10px; border: 1px solid #E2E8F0; margin-bottom: 10px; }
    </style>
""", unsafe_allow_html=True)

# --- 2. 数据加载与持久化 ---
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

# --- 3. AI Coach 决策引擎 (资产库驱动) ---
def call_coach(user_input, active_art):
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        return "❌ Coach 离线：服务器环境变量 DEEPSEEK_API_KEY 未配置。请联系主理人配置终端环境。"
    
    # 自动加载资产库作为 AI 的底层逻辑
    books = data.get("books", [])
    asset_context = "\n".join([f"【资产/模型】:{b['title']} - 【核心逻辑】:{b['concept']} - 【深度洞察】:{b['insight']}" for b in books])
    
    system_prompt = f"""
    你是 Read & Rise 专属 AI 教练。你的任务是协助高管进行战略思考。
    
    [你的底层逻辑资产库]:
    {asset_context if asset_context else "暂无特定资产，请基于通用商业逻辑回答"}
    
    [当前讨论的文章]:
    标题: {active_art['title']}
    摘要: {active_art.get('cn_summary')}
    
    [要求]:
    1. 请务必尝试将“资产库”里的模型应用到这篇文章的分析中。
    2. 语气专业、犀利、决策导向，不要说废话。
    """
    
    try:
        res = requests.post("https://api.deepseek.com/chat/completions",
            headers={"Authorization": f"Bearer {api_key}"},
            json={
                "model": "deepseek-chat",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_input}
                ],
                "temperature": 0.5
            }, timeout=30)
        return res.json()['choices'][0]['message']['content']
    except Exception as e:
        return f"⚠️ 决策引擎响应超时，请检查网络或稍后再试。错误: {str(e)}"

# --- 4. UI 侧边栏 ---
st.sidebar.title("🏹 Read & Rise")
st.sidebar.caption("Executive Digital Brain v2.0")
menu = st.sidebar.radio("决策中心", ["🏠 Dashboard", "🚀 全球快报", "📚 资产智库", "⚙️ 资产入库"])

# --- 🏠 Dashboard (首页) ---
if menu == "🏠 Dashboard":
    st.markdown('<p style="font-size: 2.5rem; font-weight: 800; color: #1E293B; margin-bottom: 0px;">Hi, Leaders! 👋</p>', unsafe_allow_html=True)
    st.write(f"今天是 {datetime.now().strftime('%Y年%m月%d日')}。全球顶级智库数据已为您同步。")

    # 🎙️ 语音播报
    st.markdown("""
        <div class="main-card">
            <p style="color:#38BDF8; font-size:0.8rem; font-weight:bold; margin-bottom:5px;">STRATEGIC AUDIO BRIEFING</p>
            <h3 style="margin:0; color:white;">每日商业决策简报 (BBC Style)</h3>
            <p style="opacity:0.8; font-size:0.9rem; margin-top:5px;">3分钟为您梳理今日核心决策点，由 Read & Rise AI 自动提炼。</p>
        </div>
    """, unsafe_allow_html=True)
    
    if os.path.exists("daily_briefing.mp3"):
        st.audio("daily_briefing.mp3")
    else:
        st.info("🕒 今日语音播报正在通过 GitHub Actions 生成中，请稍后刷新...")

    st.divider()

    col1, col2 = st.columns([0.6, 0.4])
    with col1:
        st.subheader("🧩 今日决策维度建模")
        if data.get("briefs"):
            scores = data["briefs"][0].get("model_scores", {"战略":50,"创新":50,"洞察":50,"组织":50,"执行":50})
            fig = go.Figure(data=go.Scatterpolar(
                r=list(scores.values()) + [list(scores.values())[0]],
                theta=list(scores.keys()) + [list(scores.keys())[0]],
                fill='toself', line=dict(color='#38BDF8')
            ))
            fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])), showlegend=False, height=350)
            st.plotly_chart(fig, use_container_width=True)
    with col2:
        st.subheader("📊 智库资产统计")
        c1, c2 = st.columns(2)
        c1.metric("入库模型/书籍", len(data.get("books", [])))
        c2.metric("今日快报", len(data.get("briefs", [])))
        st.info("**AI 状态：** Coach 在线 | 语音引擎就绪")

# --- 🚀 全球快报 (左读右聊) ---
elif menu == "🚀 全球快报":
    col_l, col_r = st.columns([0.55, 0.45])
    
    with col_l:
        st.header("🌍 Global Intelligence")
        for i, art in enumerate(data.get("briefs", [])):
            with st.expander(f"📍 {art['source']} | {art['title']}", expanded=(i==0)):
                t1, t2, t3, t4 = st.tabs(["💡 摘要", "🔎 案例解析", "🧠 决策反思", "📖 商业词汇"])
                with t1:
                    for s in art.get('cn_summary', []): st.write(f"• {s}")
                with t2:
                    st.write(art.get('case_study', '正在生成实战案例解析...'))
                with t3:
                    for r in art.get('reflection_flow', []): st.write(f"❓ {r}")
                with t4:
                    for v in art.get('vocab_bank', []):
                        st.markdown(f"**{v['word']}**: {v['meaning']}  \n*Ex: {v['example']}*")
                
                if st.button("🎙️ 开启 Coach 深度对话", key=f"chat_{i}"):
                    st.session_state.active_art = art
                    st.session_state.chat_history = []

    with col_r:
        st.header("🎙️ AI Coach Session")
        if "active_art" in st.session_state:
            active_art = st.session_state.active_art
            st.success(f"正在基于《{active_art['title']}》进行战略拆解")
            
            chat_container = st.container(height=550, border=True)
            if "chat_history" not in st.session_state: st.session_state.chat_history = []
            
            for m in st.session_state.chat_history:
                with chat_container.chat_message(m["role"]): st.write(m["content"])
            
            if p := st.chat_input("询问 Coach 关于本文的落地策略..."):
                st.session_state.chat_history.append({"role": "user", "content": p})
                with chat_container.chat_message("user"): st.write(p)
                
                with chat_container.chat_message("assistant"):
                    response = call_coach(p, active_art)
                    st.write(response)
                    st.session_state.chat_history.append({"role": "assistant", "content": response})
        else:
            st.info("请从左侧选择一篇文章，点击【开启 Coach 深度对话】。")

# --- 📚 资产智库 ---
elif menu == "📚 资产智库":
    st.header("📚 数字智库资产")
    st.write("这是您的底层决策引擎。AI Coach 会在对话中自动引用这些模型。")
    if not data.get("books"):
        st.info("智库目前为空。请前往【资产入库】添加您的第一个思维模型。")
    for b in data.get("books", []):
        st.markdown(f"""
            <div class="asset-card">
                <h4 style="margin:0;">📖 {b['title']}</h4>
                <p style="color:#64748B; font-size:0.9rem;"><b>核心模型:</b> {b['concept']}</p>
                <p style="margin-bottom:0;"><b>深度洞察:</b> {b['insight']}</p>
            </div>
        """, unsafe_allow_html=True)

# --- ⚙️ 资产入库 ---
elif menu == "⚙️ 资产入库":
    st.header("⚙️ 数字化您的商业思想")
    st.info("输入书籍或思维模型后，AI Coach 会通过“知识补偿”技术，在未来的对话中运用这些逻辑。")
    
    with st.form("add_asset"):
        title = st.text_input("模型/书籍名称", placeholder="例如：第一性原理")
        concept = st.text_input("核心管理逻辑", placeholder="例如：打破所有经验，从物理原点出发重新推导")
        insight = st.text_area("您的个人洞察/应用建议", placeholder="在做2026年年度预算时，应用此逻辑剔除冗余项目")
        
        if st.form_submit_button("存入数字资产库"):
            if title and concept:
                data["books"].append({"title": title, "concept": concept, "insight": insight})
                save_data(data)
                st.success(f"资产《{title}》已成功入库。")
            else:
                st.error("名称和核心逻辑为必填项。")
