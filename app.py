import streamlit as st
import json, os, requests

st.set_page_config(page_title="Read & Rise", layout="wide", page_icon="🏹")

# --- UI 视觉：修复侧边栏颜色对比 ---
st.markdown("""
<style>
    [data-testid="stSidebar"] { background-color: #0F172A !important; }
    [data-testid="stSidebar"] * { color: #FFFFFF !important; }
    .stApp { background-color: #F8FAFC; }
    .content-card { background: white; padding: 20px; border-radius: 12px; border: 1px solid #E2E8F0; margin-bottom: 20px; }
</style>
""", unsafe_allow_html=True)

def load_data():
    # 增加对 library_data.json 的兼容
    path = "data.json" if os.path.exists("data.json") else "library_data.json"
    if not os.path.exists(path): return {"items": []}
    with open(path, "r", encoding="utf-8") as f:
        try:
            d = json.load(f)
            # 容错：如果数据是旧格式，自动转为新列表
            if isinstance(d, dict) and "items" not in d:
                return {"items": d.get("books", []) + d.get("articles", [])}
            return d
        except: return {"items": []}

data = load_data()

# --- 导航 ---
st.sidebar.markdown("## 🏹 READ & RISE")
menu = st.sidebar.radio("Navigation", ["🏠 Dashboard", "🚀 Intelligence Hub", "🧠 AI Coach"])

if menu == "🏠 Dashboard":
    st.title("Hi, Leaders! 👋")
    # 修复截图中的 KeyError: 'en_title'，增加 get() 默认值
    if data["items"]:
        top = data["items"][0]
        st.subheader(f"🔥 今日首荐：{top.get('cn_title', '新内容加载中')}")
        if os.path.exists(top.get('audio_file', '')): st.audio(top['audio_file'])
        st.info(top.get('cn_analysis', '暂无深度解析'))
    else:
        st.warning("数据正在同步中，请运行生产程序...")

elif menu == "🚀 Intelligence Hub":
    st.header("Intelligence Hub")
    for item in data.get("items", []):
        with st.container():
            st.markdown(f'<div class="content-card"><h3>{item.get("cn_title", "Untitled")}</h3></div>', unsafe_allow_html=True)
            with st.expander("查看详情"):
                # 兼容所有可能的键名，防止 KeyError
                st.write(f"**EN Title:** {item.get('en_title', item.get('title', 'N/A'))}")
                st.success(item.get('cn_analysis', item.get('insight', '解析生成中...')))

elif menu == "🧠 AI Coach":
    st.header("🧠 AI Executive Coach")
    st.write("我是你的专属教练。")
    # 简单的对话占位
    if p := st.chat_input("向我提问..."):
        st.write(f"正在分析您关于 '{p}' 的问题...")
