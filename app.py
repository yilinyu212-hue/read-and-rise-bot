import streamlit as st
from backend.crawler import fetch_from_rss
from backend.engine import analyze_article
import json

st.title("📚 Read & Rise")

rss = st.text_input(
    "输入外刊 RSS（如 NYT / FT / Economist）",
    "https://rss.nytimes.com/services/xml/rss/nyt/World.xml"
)

if st.button("抓取并分析"):
    with st.spinner("分析中..."):
        title, content = fetch_from_rss(rss)
        result = analyze_article(title, content)

        st.subheader(title)
        st.json(result)

        with open("data/knowledge.json", "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
