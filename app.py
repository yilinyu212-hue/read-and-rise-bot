import streamlit as st
import json, os

st.set_page_config(page_title="Read & Rise", layout="wide", page_icon="🏹")

# UI 视觉样式
st.markdown("""
<style>
    [data-testid="stSidebar"] { background-color: #0F172A !important; }
    [data-testid="stSidebar"] * { color: white !important; }
    .stApp { background-color: #F8FAFC; }
    .hero-section { background: white; padding: 40px; border-radius: 20px; text-align: center; border: 1px solid #E2E8F0; }
</style>
""", unsafe_allow_html=True)

def load_data():
    if os.path.exists("data.json"):
        with open("data.json", "r", encoding="utf-8") as f:
            try:
                content = json.load(f)
                # 兼容不同的数据格式
                if isinstance(content, dict): return content.get("items", [])
                if isinstance(content, list): return content
            except: return []
    return []

items = load_data()

st.sidebar.title("🏹 Read & Rise")
menu = st.sidebar.radio("导航菜单", ["🏠 决策看板 Dashboard", "🚀 全球内参 Intelligence", "🧠 AI Coach"])

if menu == "🏠 决策看板 Dashboard":
    st.markdown('<div class="hero-section">', unsafe_allow_html=True)
    st.title("Hi, Leaders! 👋")
    if items:
        top = items[0]
        st.subheader(f"🔥 今日首荐：{top.get('cn_title')}")
        st.write(f"**核心思想预览：** {top.get('cn_analysis', '')[:120]}...")
        if st.button("查看完整外刊案例"):
            st.info("请切换至左侧菜单『🚀 全球内参』")
    else:
        st.warning("智库内容正在从全球同步中，请稍后再试。")
    st.markdown('</div>', unsafe_allow_html=True)

elif menu == "🚀 全球内参 Intelligence":
    st.header("Global Intelligence Hub")
    if not items:
        st.info("暂无数据，请运行抓取程序。")
    for item in items:
        with st.expander(f"📍 {item.get('cn_title', '新洞察')}", expanded=True):
            if os.path.exists(item.get('audio_file', '')):
                st.audio(item['audio_file'])
            
            tab1, tab2, tab3 = st.tabs(["💡 深度解析", "📖 行业案例", "🧠 反思流"])
            with tab1:
                st.success(item.get('cn_analysis', '内容生成中...'))
                st.caption(f"Original Title: {item.get('en_title')}")
            with tab2:
                st.write("**针对管理者的实际应用案例：**")
                st.info(item.get('case_study', '正在匹配行业案例...'))
            with tab3:
                st.warning(f"**推荐思维模型：** {item.get('mental_model', 'N/A')}")
                for q in item.get('reflection_flow', []):
                    st.write(f"❓ {q}")
