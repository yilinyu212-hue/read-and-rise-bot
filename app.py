import streamlit as st
import json, os, requests
import plotly.graph_objects as go

st.set_page_config(page_title="Read & Rise AI Coach", layout="wide")

# 环境变量检查（修复 Coach 离线）
API_KEY = os.getenv("DEEPSEEK_API_KEY")

def load_data():
    if not os.path.exists("data.json"): return {"briefs":[], "books":[]}
    with open("data.json", "r", encoding="utf-8") as f: return json.load(f)

data = load_data()

# 侧边栏
menu = st.sidebar.radio("导航", ["🏠 Dashboard", "📚 经典书库", "🚀 全球快报", "⚙️ 后台管理"])

if menu == "🚀 全球快报":
    col_l, col_r = st.columns([0.6, 0.4])
    with col_l:
        st.header("🌍 今日智库内参")
        for i, art in enumerate(data.get("briefs", [])):
            with st.expander(f"📌 {art['source']} | {art['title']}", expanded=(i==0)):
                tab1, tab2, tab3, tab4 = st.tabs(["💡 摘要与金句", "📖 词汇与表达", "🔍 案例解析", "🧠 反思与教学"])
                
                with tab1:
                    st.write("**EN Summary:**")
                    for s in art.get('en_summary', []): st.write(f"• {s}")
                    st.write("**中文摘要:**")
                    for s in art.get('cn_summary', []): st.write(f"• {s}")
                
                with tab2:
                    for v in art.get('vocab_bank', []):
                        st.markdown(f"**{v['word']}** ({v['meaning']})  \n*Ex: {v['example']}*")
                
                with tab3:
                    st.write(art.get('case_study', '暂无案例'))
                
                with tab4:
                    st.write("**反思流:**")
                    for r in art.get('reflection_flow', []): st.write(f"❓ {r}")
                    st.info(f"🎓 **教学迁移建议:** {art.get('teaching_tips', '暂无')}")

                if st.button("🎙️ 对话 Coach", key=f"btn_{i}"):
                    st.session_state.active_art = art
    
    with col_r:
        if "active_art" in st.session_state:
            st.subheader("🎙️ Coach Session")
            # 这里插入之前的对话逻辑代码...
        else:
            st.info("请在左侧选择文章开启对话")
