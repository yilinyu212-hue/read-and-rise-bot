import streamlit as st
import json, os

st.set_page_config(page_title="Read & Rise", layout="wide")

# 视觉优化
st.markdown("""
<style>
    [data-testid="stSidebar"] { background-color: #0F172A !important; }
    [data-testid="stSidebar"] * { color: white !important; }
    .stApp { background-color: #F8FAFC; }
    .main-card { background: white; padding: 30px; border-radius: 20px; box-shadow: 0 4px 12px rgba(0,0,0,0.05); }
</style>
""", unsafe_allow_html=True)

def load_data():
    if not os.path.exists("data.json"): return {"items": []}
    with open("data.json", "r", encoding="utf-8") as f:
        return json.load(f)

data = load_data()
items = data.get("items", [])

st.sidebar.title("🏹 Read & Rise")
menu = st.sidebar.radio("菜单", ["🏠 首页 Dashboard", "🚀 全球内参 Intelligence", "🧠 AI 教练"])

if menu == "🏠 首页 Dashboard":
    st.title("Hi, Leaders! 👋")
    if items:
        top = items[0]
        st.markdown(f"""<div class="main-card">
            <h2>今日头条：{top.get('cn_title')}</h2>
            <p><b>摘要：</b>{top.get('cn_analysis')[:150]}...</p>
        </div>""", unsafe_allow_html=True)
        if st.button("查看完整案例与反思"):
            st.info("请点击左侧『全球内参』进入研读。")
    else:
        st.info("正在获取全球智库数据...")

elif menu == "🚀 全球内参 Intelligence":
    for item in items:
        with st.expander(f"📍 {item.get('cn_title')}"):
            if os.path.exists(item.get('audio_file','')): st.audio(item['audio_file'])
            t1, t2, t3 = st.tabs(["💡 摘要", "📖 案例", "❓ 反思"])
            with t1: st.success(item.get('cn_analysis'))
            with t2: st.write(item.get('case_study'))
            with t3:
                st.info(f"思维模型：{item.get('mental_model')}")
                for q in item.get('reflection_flow', []): st.warning(f"反思：{q}")
