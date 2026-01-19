import streamlit as st
import json, os, requests
import plotly.graph_objects as go

st.set_page_config(page_title="Read & Rise AI Coach", layout="wide", page_icon="🏹")

# 1. 加载数据
def load_data():
    if not os.path.exists("data.json"): return {"briefs":[], "books":[]}
    with open("data.json", "r", encoding="utf-8") as f: return json.load(f)

def save_data(d):
    with open("data.json", "w", encoding="utf-8") as f: json.dump(d, f, ensure_ascii=False, indent=4)

data = load_data()

# 2. 雷达图
def draw_radar(scores):
    if not scores: scores = {"战略":50,"组织":50,"创新":50,"洞察":50,"执行":50}
    categories = list(scores.keys())
    values = list(scores.values())
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(r=values + [values[0]], theta=categories + [categories[0]], fill='toself'))
    fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])), showlegend=False, height=350)
    return fig

# 3. 侧边栏导航
menu = st.sidebar.radio("导航", ["🏠 Dashboard", "📚 经典书库", "🚀 全球快报", "⚙️ 后台管理"])

if menu == "🏠 Dashboard":
    st.title("🏹 决策仪表盘")
    if data.get("briefs"):
        col1, col2 = st.columns([1, 1])
        with col1:
            st.subheader("🧩 核心思维建模")
            st.plotly_chart(draw_radar(data["briefs"][0].get("model_scores")))
        with col2:
            st.subheader("📜 专家金句")
            for gs in data["briefs"][0].get("golden_sentences", []):
                st.info(f"“{gs['cn']}”\n\n— {gs['en']}")

elif menu == "📚 经典书库":
    st.header("📚 教育者书架")
    if not data.get("books"): st.info("请在后台管理录入书籍")
    for b in data.get("books", []):
        with st.container(border=True):
            st.subheader(f"📖 {b['title']}")
            st.write(f"**核心模型**: `{b['concept']}`")
            st.write(f"**深度洞察**: {b['insight']}")

elif menu == "🚀 全球快报":
    col_l, col_r = st.columns([0.6, 0.4])
    with col_l:
        st.header("🌍 全球智库内参")
        for i, art in enumerate(data.get("briefs", [])):
            with st.expander(f"📌 {art['source']} | {art['title']}", expanded=(i==0)):
                # 找回所有丢失模块
                t1, t2, t3, t4 = st.tabs(["💡 摘要", "📖 词汇银行", "🔎 案例解析", "🧠 反思教学"])
                with t1:
                    st.write("**EN Summary:**")
                    for s in art.get('en_summary', []): st.write(f"• {s}")
                    st.write("**中文摘要:**")
                    for s in art.get('cn_summary', []): st.write(f"• {s}")
                with t2:
                    for v in art.get('vocab_bank', []):
                        st.markdown(f"**{v['word']}**: {v['meaning']}  \n*Ex: {v['example']}*")
                with t3:
                    st.write(art.get('case_study', '暂无深度案例'))
                with t4:
                    st.write("**本周反思流:**")
                    for r in art.get('reflection_flow', []): st.write(f"❓ {r}")
                    st.success(f"🎓 **教学迁移建议**: {art.get('teaching_tips', '暂无')}")
                
                if st.button("🎙️ 开启 Coach 对话", key=f"btn_{i}"):
                    st.session_state.active_art = art
                    st.session_state.chat_history = []

    with col_r:
        st.header("🎙️ Coach Session")
        if "active_art" in st.session_state:
            curr = st.session_state.active_art
            st.info(f"正在对话: {curr['title']}")
            # 这里的对话逻辑中，API_KEY = os.getenv("DEEPSEEK_API_KEY") 
            # 务必在服务器启动命令中加入该变量
        else:
            st.info("请先点击左侧文章下的开启按钮")

elif menu == "⚙️ 后台管理":
    st.header("⚙️ 资产管理")
    with st.form("add_book_form"):
        title = st.text_input("书名")
        concept = st.text_input("核心模型")
        insight = st.text_area("反思洞察")
        if st.form_submit_button("入库书籍资产"):
            data["books"].append({"title": title, "concept": concept, "insight": insight})
            save_data(data)
            st.success("书籍已成功入库！")
