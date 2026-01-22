# app.py

import streamlit as st
from backend.crawler import run_crawler
import json

st.set_page_config(page_title="Read & Rise", layout="wide")

st.title("📖 Read & Rise")
st.subheader("Read better. Think deeper. Rise slowly.")

st.markdown("""
一个为 **长期思考者 / 创业者 / 管理者** 设计的阅读与反思系统  
""")

if st.button("🔍 抓取最新外刊"):
    with st.spinner("正在抓取外刊..."):
        articles = run_crawler()
        st.success(f"成功抓取 {len(articles)} 篇文章")

st.divider()

st.header("📚 已抓取内容")

try:
    with open("data/knowledge.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    for a in data:
        with st.expander(a["title"]):
            st.write(a["content"][:1500])
            st.markdown(f"[阅读全文]({a['link']})")
except:
    st.info("暂无内容，请先抓取。")
