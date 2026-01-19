import streamlit as st
import json, os, requests
import plotly.graph_objects as go

st.set_page_config(page_title="Read & Rise AI Coach", layout="wide")

# ================= 1. 数据管理 =================
def load_data():
    if not os.path.exists("data.json"): return {"briefs":[], "books":[], "weekly_question":{}}
    with open("data.json", "r", encoding="utf-8") as f:
        d = json.load(f)
        if "books" not in d: d["books"] = []
        return d

def save_data(d):
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False, indent=4)

data = load_data()

# ================= 2. 可视化工具 =================
def draw_radar(scores):
    categories = list(scores.keys())
    values = list(scores.values())
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(r=values + [values[0]], theta=categories + [categories[0]], fill='toself'))
    fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])), showlegend=False, height=300)
    return fig

# ================= 3. 导航逻辑 =================
menu = st.sidebar.radio("导航", ["🏠 Dashboard", "📚 经典书库", "🚀 全球快报", "⚙️ 后台管理"])

# --- 🏠 Dashboard ---
if menu == "🏠 Dashboard":
    st.markdown(f"""<div style="background:linear-gradient(135deg,#0F172A,#1E293B);padding:30px;border-radius:20px;color:white;border-left:10px solid #38BDF8;">
        <h4 style="color:#38BDF8;margin:0;">🎙️ WEEKLY INQUIRY / 每周提问</h4>
        <p style="font-size:1.5rem;font-weight:bold;margin-top:10px;">“{data.get('weekly_question',{}).get('cn','')}”</p>
    </div>""", unsafe_allow_html=True)
    
    if data.get("briefs"):
        st.subheader("🧩 思维建模：今日洞察象限")
        st.plotly_chart(draw_radar(data["briefs"][0].get("model_scores", {"维度":0})))
        

# --- 📚 经典书库 ---
elif menu == "📚 经典书库":
    st.header("📚 Educator's Bookshelf")
    for b in data.get("books", []):
        with st.container(border=True):
            col1, col2 = st.columns([1, 5])
            col1.image("https://cdn-icons-png.flaticon.com/512/330/330731.png", width=80) # 默认书皮
            col2.subheader(b['title'])
            col2.write(f"**核心模型:** {b['concept']} | **启发:** {b['insight']}")

# --- 🚀 全球快报 (左读右聊) ---
elif menu == "🚀 全球快报":
    col_l, col_r = st.columns([0.6, 0.4])
    with col_l:
        for i, art in enumerate(data.get("briefs", [])):
            with st.expander(f"📌 {art['title']}"):
                st.write("**摘要:**")
                for s in art.get('cn_summary', []): st.write(f"• {s}")
                if st.button("🎙️ 开启对话", key=f"btn_{i}"):
                    st.session_state.active_art = art
                    st.session_state.history = []
    with col_r:
        if "active_art" in st.session_state:
            st.info(f"正在陪读: {st.session_state.active_art['title']}")
            # ... 对话逻辑保持之前版本 ...

# --- ⚙️ 后台管理 (新增书籍录入) ---
elif menu == "⚙️ 后台管理":
    st.header("⚙️ 内容录入中心")
    with st.form("book_form"):
        st.subheader("📖 录入新书籍/经典模型")
        new_title = st.text_input("书籍名称")
        new_concept = st.text_input("核心模型 (如: 第一性原理)")
        new_insight = st.text_area("深度洞察/反思点")
        if st.form_submit_button("入库书籍资产"):
            data["books"].append({"title": new_title, "concept": new_concept, "insight": new_insight})
            save_data(data)
            st.success(f"《{new_title}》已成功存入数字大脑。")
