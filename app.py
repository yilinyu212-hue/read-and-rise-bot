import streamlit as st
import json, os

st.set_page_config(page_title="Read & Rise", layout="wide")

# --- 极简商务 UI 修复 ---
st.markdown("""
<style>
    [data-testid="stSidebar"] { background-color: #0F172A !important; }
    [data-testid="stSidebar"] * { color: white !important; }
    .stApp { background-color: #F8FAFC; }
    .card { background: white; padding: 20px; border-radius: 10px; border: 1px solid #E2E8F0; margin-bottom: 15px; }
</style>
""", unsafe_allow_html=True)

def load_all_data():
    # 尝试加载所有可能的数据文件
    files = ["data.json", "library_data.json"]
    all_items = []
    update_time = "Unknown"
    for f_name in files:
        if os.path.exists(f_name):
            try:
                with open(f_name, "r", encoding="utf-8") as f:
                    d = json.load(f)
                    if isinstance(d, dict):
                        # 兼容新老格式：items, books, articles
                        all_items.extend(d.get("items", []) + d.get("books", []) + d.get("articles", []))
                        update_time = d.get("update_time", update_time)
            except: pass
    return {"items": all_items, "time": update_time}

data = load_all_data()

st.sidebar.title("🏹 Read & Rise")
menu = st.sidebar.radio("Navigation", ["Dashboard", "Intelligence", "AI Coach"])

if menu == "Dashboard":
    st.header("Hi, Leaders! 👋")
    if data["items"]:
        top = data["items"][0]
        # 使用 .get() 绝对防止 KeyError
        st.subheader(f"🔥 Today's Pick: {top.get('cn_title', top.get('title', 'New Strategy'))}")
        audio = top.get('audio_file', '')
        if os.path.exists(audio): st.audio(audio)
        st.info(top.get('cn_analysis', top.get('insight', 'Analysis is being generated...')))
    else:
        st.warning("Data sync in progress. Please run 'python3 crawler.py' in the terminal.")

elif menu == "Intelligence":
    st.header("Global Strategy Hub")
    for item in data["items"]:
        with st.container():
            # 这里的字段名通过 .get 兼容所有版本
            title = item.get('cn_title', item.get('title', 'Untitled'))
            st.markdown(f'<div class="card"><h3>📍 {title}</h3></div>', unsafe_allow_html=True)
            with st.expander("Explore Details"):
                st.write(f"**Original:** {item.get('en_title', 'N/A')}")
                st.success(f"**Insight:**\n{item.get('cn_analysis', item.get('insight', 'Processing...'))}")
                audio = item.get('audio_file', '')
                if os.path.exists(audio): st.audio(audio)

elif menu == "AI Coach":
    st.header("🧠 AI Executive Coach")
    st.write("I am your strategic advisor. How can I help you today?")
    if p := st.chat_input("Ask me anything..."):
        st.write(f"Analysing your query: {p}...")
