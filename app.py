import streamlit as st
import json, os, requests
import plotly.graph_objects as go

st.set_page_config(page_title="Read & Rise AI Coach", layout="wide")

# ================= 1. 数据处理 =================
def load_data():
    if not os.path.exists("data.json"): return {"briefs":[], "books":[], "weekly_question":{}}
    with open("data.json", "r", encoding="utf-8") as f:
        try:
            d = json.load(f)
            if "books" not in d: d["books"] = []
            return d
        except: return {"briefs":[], "books":[], "weekly_question":{}}

def save_data(d):
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False, indent=4)

data = load_data()

# ================= 2. 雷达图 =================
def draw_radar(scores):
    if not scores: scores = {"维度": 0}
    categories = list(scores.keys())
    values = list(scores.values())
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(r=values + [values[0]], theta=categories + [categories[0]], fill='toself'))
    fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])), showlegend=False, height=350)
    return fig

# ================= 3. AI 对话 =================
def call_coach(user_input, art):
    api_key = os.getenv("DEEPSEEK_API_KEY")
    ctx = f"文章:{art['title']}\n模型:{art.get('related_model')}\n摘要:{art.get('cn_summary')}"
    try:
        res = requests.post("https://api.deepseek.com/chat/completions", 
            headers={"Authorization": f"Bearer {api_key}"},
            json={
                "model": "deepseek-chat",
                "messages": [
                    {"role": "system", "content": f"你是针对此文的专业私教。背景：\n{ctx}"},
                    {"role": "user", "content": user_input}
                ], "temperature": 0.5
            })
        return res.json()['choices'][0]['message']['content']
    except: return "Coach 连接失败，请检查 API Key 配置。"

# ================= 4. 导航 =================
menu = st.sidebar.radio("导航", ["🏠 Dashboard", "📚 经典书库", "🚀 全球快报", "⚙️ 后台管理"])

if menu == "🏠 Dashboard":
    st.markdown(f"""<div style="background:linear-gradient(135deg,#0F172A,#1E293B);padding:30px;border-radius:20px;color:white;border-left:10px solid #38BDF8;">
        <h4 style="color:#38BDF8;margin:0;">🎙️ WEEKLY INQUIRY / 每周提问</h4>
        <p style="font-size:1.5rem;font-weight:bold;margin-top:10px;">“{data.get('weekly_question',{}).get('cn','加载中...')}”</p>
    </div>""", unsafe_allow_html=True)
    
    if data.get("briefs"):
        st.subheader("🧩 今日思维建模")
        st.plotly_chart(draw_radar(data["briefs"][0].get("model_scores")))

elif menu == "📚 经典书库":
    st.header("📚 Educator's Bookshelf")
    if not data.get("books"):
        st.info("书库空空如也，请前往【后台管理】录入。")
    else:
        for b in data["books"]:
            with st.container(border=True):
                st.subheader(f"📖 《{b['title']}》")
                st.write(f"**核心模型:** {b['concept']}")
                st.write(f"**深度洞察:** {b['insight']}")

elif menu == "🚀 全球快报":
    col_l, col_r = st.columns([0.6, 0.4])
    with col_l:
        for i, art in enumerate(data.get("briefs", [])):
            with st.expander(f"📌 {art['title']}", expanded=(i==0)):
                st.write("**EN Summary:**")
                for s in art.get('en_summary', []): st.write(f"• {s}")
                st.write("**中文摘要:**")
                for s in art.get('cn_summary', []): st.write(f"• {s}")
                if st.button("🎙️ 针对此文开启对话", key=f"btn_{i}"):
                    st.session_state.active_art = art
                    st.session_state.history = []
    with col_r:
        if "active_art" in st.session_state:
            st.info(f"正在对话: {st.session_state.active_art['title']}")
            chat_container = st.container(height=500)
            for m in st.session_state.get('history', []):
                with chat_container.chat_message(m["role"]): st.write(m["content"])
            if p := st.chat_input("向教练提问..."):
                st.session_state.history.append({"role": "user", "content": p})
                with chat_container.chat_message("user"): st.write(p)
                with chat_container.chat_message("assistant"):
                    r = call_coach(p, st.session_state.active_art)
                    st.write(r)
                    st.session_state.history.append({"role": "assistant", "content": r})
        else:
            st.info("请点击左侧文章下的【开启对话】")

elif menu == "⚙️ 后台管理":
    st.header("⚙️ 资产录入中心")
    with st.form("book_entry"):
        title = st.text_input("书名")
        concept = st.text_input("核心模型 (如: 第一性原理)")
        insight = st.text_area("深度洞察")
        if st.form_submit_button("入库书籍资产"):
            data["books"].append({"title": title, "concept": concept, "insight": insight})
            save_data(data)
            st.success("书籍已入库！")
