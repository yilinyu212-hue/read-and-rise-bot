import streamlit as st
import json, os, requests
import plotly.graph_objects as go

st.set_page_config(page_title="Read & Rise AI Coach", layout="wide", page_icon="🏹")

# --- 数据处理 ---
def load_data():
    if not os.path.exists("data.json"): return {"briefs":[], "books":[]}
    with open("data.json", "r", encoding="utf-8") as f: return json.load(f)

def save_data(d):
    with open("data.json", "w", encoding="utf-8") as f: json.dump(d, f, ensure_ascii=False, indent=4)

data = load_data()

# --- 雷达图绘制 ---
def draw_radar(scores):
    if not scores: scores = {"认知":50,"战略":50,"逻辑":50,"洞察":50,"创新":50}
    categories = list(scores.keys())
    values = list(scores.values())
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(r=values + [values[0]], theta=categories + [categories[0]], fill='toself'))
    fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])), showlegend=False, height=350)
    return fig

# --- 导航 ---
menu = st.sidebar.radio("Read & Rise 导航", ["🏠 Dashboard", "📚 经典书库", "🚀 全球快报", "⚙️ 后台管理"])

if menu == "🏠 Dashboard":
    st.title("🏹 决策仪表盘")
    if data.get("briefs"):
        col1, col2 = st.columns([1, 1])
        with col1:
            st.subheader("🧩 最新思维建模")
            st.plotly_chart(draw_radar(data["briefs"][0].get("model_scores")))
        with col2:
            st.subheader("📜 核心金句")
            for gs in data["briefs"][0].get("golden_sentences", []):
                st.info(f"“{gs['cn']}”\n\n— {gs['en']}")

elif menu == "📚 经典书库":
    st.header("📚 书籍资产库")
    for b in data.get("books", []):
        with st.container(border=True):
            st.subheader(f"📖 {b['title']}")
            st.markdown(f"**核心模型**: `{b['concept']}`")
            st.write(b['insight'])

elif menu == "🚀 全球快报":
    col_l, col_r = st.columns([0.6, 0.4])
    with col_l:
        st.header("🌍 今日智库内参")
        for i, art in enumerate(data.get("briefs", [])):
            with st.expander(f"📌 {art['source']} | {art['title']}", expanded=(i==0)):
                # 找回丢失的四个维度
                t1, t2, t3, t4 = st.tabs(["💡 摘要", "📖 词汇", "🔎 案例", "🧠 反思"])
                with t1:
                    st.write("**EN:**")
                    for s in art.get('en_summary', []): st.write(f"• {s}")
                    st.write("**中文:**")
                    for s in art.get('cn_summary', []): st.write(f"• {s}")
                with t2:
                    for v in art.get('vocab_bank', []):
                        st.markdown(f"**{v['word']}**: {v['meaning']}  \n*Ex: {v['example']}*")
                with t3:
                    st.write(art.get('case_study', '暂无案例'))
                with t4:
                    st.write("**反思提问:**")
                    for r in art.get('reflection_flow', []): st.write(f"❓ {r}")
                    st.success(f"🎓 **教学建议**: {art.get('teaching_tips', '暂无')}")
                
                if st.button("🎙️ 对话 Coach", key=f"btn_{i}"):
                    st.session_state.active_art = art

    with col_r:
        st.header("🎙️ Coach Session")
        if "active_art" in st.session_state:
            st.info(f"正在深度研读: {st.session_state.active_art['title']}")
            # 对话逻辑同之前，确保使用 API_KEY = os.getenv("DEEPSEEK_API_KEY")

elif menu == "⚙️ 后台管理":
    st.header("⚙️ 资产录入")
    with st.form("add_book"):
        title = st.text_input("书名")
        concept = st.text_input("模型")
        insight = st.text_area("洞察")
        if st.form_submit_button("入库书籍"):
            data["books"].append({"title":title, "concept":concept, "insight":insight})
            save_data(data)
            st.success("入库成功")
