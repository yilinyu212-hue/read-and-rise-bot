import streamlit as st
import json, os, requests

# 数据初始化逻辑
def load_all():
    if not os.path.exists("data.json"): return {"briefs":[], "books":[]}
    with open("data.json", "r", encoding="utf-8") as f:
        d = json.load(f)
        if "books" not in d: d["books"] = []
        return d

data = load_all()

# 页面布局
st.sidebar.title("🏹 Read & Rise")
menu = st.sidebar.radio("决策中心", ["🏠 Dashboard", "🚀 全球快报", "📚 资产智库"])

if menu == "🏠 Dashboard":
    st.title("Hi, Leaders! 👋")
    if os.path.exists("daily_briefing.mp3"):
        st.audio("daily_briefing.mp3")
    else:
        st.info("🕒 播报音频正在后台生成，请稍后...")

elif menu == "🚀 全球快报":
    for i, art in enumerate(data.get("briefs", [])):
        with st.expander(f"📍 {art['source']} | {art['title']}"):
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("🇬🇧 English Summary")
                st.write(art.get("en_summary"))
            with col2:
                st.subheader("🇨🇳 中文深度解析")
                st.write(art.get("cn_analysis"))
            
            # 【关键功能】一键存入智库
            if st.button("📥 将此深度解析存入资产智库", key=f"save_{i}"):
                new_asset = {
                    "title": art['title'],
                    "concept": art['source'],
                    "insight": art['cn_analysis']
                }
                data["books"].append(new_asset)
                with open("data.json", "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=4)
                st.success("已存入智库！Coach 未来将以此为决策依据。")

elif menu == "📚 资产智库":
    st.header("📚 Read & Rise 数字资产")
    for b in data.get("books", []):
        st.info(f"**{b['title']}**\n\n{b['insight']}")
