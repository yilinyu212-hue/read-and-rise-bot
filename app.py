import streamlit as st
import json, os, requests
import plotly.graph_objects as go

st.set_page_config(page_title="Read & Rise AI Coach", layout="wide", page_icon="🏹")

# 1. 数据加解密逻辑
def load_data():
    if not os.path.exists("data.json"):
        return {"briefs":[], "books":[], "weekly_question":{"cn":"加载中","en":"Loading"}}
    with open("data.json", "r", encoding="utf-8") as f:
        try:
            d = json.load(f)
            if "books" not in d: d["books"] = []
            return d
        except:
            return {"briefs":[], "books":[], "weekly_question":{"cn":"格式错误","en":"Error"}}

def save_data(d):
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False, indent=4)

data = load_data()

# 2. 雷达图绘制组件
def draw_radar(scores):
    if not scores: scores = {"战略":50, "组织":50, "创新":50, "洞察":50, "执行":50}
    categories = list(scores.keys())
    values = list(scores.values())
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(r=values + [values[0]], theta=categories + [categories[0]], fill='toself', name='模型评分'))
    fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])), showlegend=False, height=350, margin=dict(l=40, r=40, t=40, b=40))
    return fig

# 3. AI Coach 对话函数
def call_coach(user_input, art_context):
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        return "⚠️ Coach 离线：请在系统环境变量中配置 DEEPSEEK_API_KEY。"
    
    ctx = f"背景文章: {art_context['title']}\n模型: {art_context.get('related_model')}\n摘要: {art_context.get('cn_summary')}"
    try:
        res = requests.post("https://api.deepseek.com/chat/completions", 
            headers={"Authorization": f"Bearer {api_key}"},
            json={
                "model": "deepseek-chat",
                "messages": [
                    {"role": "system", "content": f"你是针对文章的专业私教 Coach。背景内容如下：\n{ctx}"},
                    {"role": "user", "content": user_input}
                ], "temperature": 0.5
            }, timeout=30)
        return res.json()['choices'][0]['message']['content']
    except:
        return "⚠️ 连接超时，请稍后重试。"

# 4. 侧边导航
menu = st.sidebar.radio("Read & Rise 导航", ["🏠 Dashboard", "📚 经典书库", "🚀 全球快报", "⚙️ 后台管理"])

# --- 🏠 主页 ---
if menu == "🏠 Dashboard":
    st.markdown(f"""<div style="background:linear-gradient(135deg,#0F172A,#1E293B);padding:30px;border-radius:20px;color:white;border-left:10px solid #38BDF8;">
        <h4 style="color:#38BDF8;margin:0;">🎙️ WEEKLY INQUIRY / 每周提问</h4>
        <p style="font-size:1.5rem;font-weight:bold;margin-top:10px;">“{data.get('weekly_question',{}).get('cn','')}”</p>
    </div>""", unsafe_allow_html=True)
    
    st.divider()
    col1, col2 = st.columns([1, 1])
    with col1:
        st.subheader("🧩 今日思维建模")
        if data.get("briefs"):
            st.plotly_chart(draw_radar(data["briefs"][0].get("model_scores")))
        else:
            st.info("同步数据后显示雷达图")
    with col2:
        st.subheader("📊 平台状态")
        st.metric("已入库书籍/模型", len(data.get("books", [])))
        st.metric("今日快报数量", len(data.get("briefs", [])))

# --- 📚 书籍库 ---
elif menu == "📚 经典书库":
    st.header("📚 Educator's Bookshelf")
    if not data.get("books"):
        st.info("暂无书籍，请前往【后台管理】录入您的第一本书籍。")
    for b in data.get("books", []):
        with st.container(border=True):
            col_img, col_txt = st.columns([1, 5])
            col_img.image("https://cdn-icons-png.flaticon.com/512/330/330731.png", width=80)
            col_txt.subheader(f"《{b['title']}》")
            col_txt.markdown(f"**核心模型:** `{b['concept']}`")
            col_txt.write(f"**深度洞察:** {b['insight']}")

# --- 🚀 全球快报 (左读右聊) ---
elif menu == "🚀 全球快报":
    col_l, col_r = st.columns([0.6, 0.4])
    with col_l:
        st.header("🌍 今日智库内参")
        for i, art in enumerate(data.get("briefs", [])):
            with st.expander(f"📌 {art['source']} | {art['title']}", expanded=(i==0)):
                st.write("**核心摘要:**")
                for s in art.get('cn_summary', []): st.write(f"• {s}")
                if st.button("🎙️ 针对此文开启对话", key=f"btn_{i}"):
                    st.session_state.active_art = art
                    st.session_state.history = []
    with col_r:
        st.header("🎙️ Coach Session")
        if "active_art" in st.session_state:
            curr = st.session_state.active_art
            st.info(f"正在对话：《{curr['title']}》")
            chat_container = st.container(height=500)
            if "history" not in st.session_state: st.session_state.history = []
            for m in st.session_state.history:
                with chat_container.chat_message(m["role"]): st.write(m["content"])
            
            if p := st.chat_input("向教练提问..."):
                st.session_state.history.append({"role": "user", "content": p})
                with chat_container.chat_message("user"): st.write(p)
                with chat_container.chat_message("assistant"):
                    r = call_coach(p, curr)
                    st.write(r)
                    st.session_state.history.append({"role": "assistant", "content": r})
        else:
            st.info("请在左侧选择一篇文章并点击【开启对话】按钮。")

# --- ⚙️ 后台管理 ---
elif menu == "⚙️ 后台管理":
    st.header("⚙️ 资产管理中心")
    with st.form("add_book_form"):
        st.subheader("📖 录入新书籍/经典模型")
        b_title = st.text_input("书籍名称")
        b_concept = st.text_input("核心模型 (如: 第一性原理)")
        b_insight = st.text_area("深度反思/洞察")
        if st.form_submit_button("入库书籍资产"):
            if b_title:
                data["books"].append({"title": b_title, "concept": b_concept, "insight": b_insight})
                save_data(data)
                st.success(f"《{b_title}》已成功入库！")
            else:
                st.error("请输入书名")
