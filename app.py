import streamlit as st
import json
import os
from datetime import datetime

from backend.crawler import crawl_one
from backend.engine import analyze_article

# ---------------------------
# 基础配置
# ---------------------------
st.set_page_config(
    page_title="Read & Rise | 管理者每日一思",
    page_icon="🏹",
    layout="wide"
)

DATA_PATH = "data/knowledge.json"

# ---------------------------
# 数据层
# ---------------------------
def load_knowledge():
    if not os.path.exists(DATA_PATH):
        return []
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except:
            return []


def save_knowledge(items):
    with open(DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, indent=2)


# ---------------------------
# UI 样式（克制 + 高端）
# ---------------------------
st.markdown("""
<style>
body {
    background-color: #F8FAFC;
}
.section-title {
    font-size: 22px;
    font-weight: 700;
    margin-bottom: 12px;
}
.card {
    background: white;
    padding: 24px;
    border-radius: 12px;
    border: 1px solid #E5E7EB;
    margin-bottom: 20px;
}
.meta {
    color: #64748B;
    font-size: 13px;
}
</style>
""", unsafe_allow_html=True)

# ---------------------------
# 侧边栏
# ---------------------------
with st.sidebar:
    st.markdown("## 🏹 Read & Rise")
    st.caption("为创业者与管理者打造的每日一思")
    st.divider()

    page = st.radio(
        "导航",
        ["🏠 今日洞察", "📚 知识库", "⚙️ 内容引擎"]
    )

# ---------------------------
# 页面一：今日洞察（主页）
# ---------------------------
if page == "🏠 今日洞察":

    st.markdown("## 今日的一次深度思考")

    knowledge = load_knowledge()

    if knowledge:
        today = knowledge[0]

        st.markdown(f"""
        <div class="card">
            <div class="meta">{today.get("date")} · {today.get("source")}</div>
            <h2>{today.get("cn_title")}</h2>
            <p><b>核心思维模型：</b>{today.get("mental_model")}</p>
        </div>
        """, unsafe_allow_html=True)

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("<div class='section-title'>READ｜外刊要义</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='card'>{today.get('cn_analysis')}</div>", unsafe_allow_html=True)

        with col2:
            st.markdown("<div class='section-title'>RISE｜管理启发</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='card'>{today.get('case_study')}</div>", unsafe_allow_html=True)

    else:
        st.info("今天还没有生成内容，请前往【内容引擎】。")

# ---------------------------
# 页面二：知识库
# ---------------------------
elif page == "📚 知识库":

    st.markdown("## 历史思维沉淀")

    knowledge = load_knowledge()

    if not knowledge:
        st.warning("暂无历史内容。")
    else:
        for item in knowledge:
            with st.expander(f"{item.get('date')} ｜ {item.get('cn_title')}"):
                st.markdown(f"**思维模型：** {item.get('mental_model')}")
                st.markdown(item.get("cn_analysis"))

# ---------------------------
# 页面三：内容引擎（后台）
# ---------------------------
elif page == "⚙️ 内容引擎":

    st.markdown("## 内容生成引擎（后台）")
    st.caption("抓取 → 思考 → 入库")

    if st.button("🚀 抓取并生成今日内容"):

        with st.spinner("正在抓取外刊并进行深度思考…"):
            article = crawl_one()

            if not article:
                st.error("未抓取到有效外刊内容。")
            else:
                result = analyze_article(
                    title=article["title"],
                    summary=article["summary"]
                )

                if not result:
                    st.error("分析失败，请检查 engine 配置。")
                else:
                    knowledge = load_knowledge()

                    item = {
                        "date": datetime.now().strftime("%Y-%m-%d"),
                        "source": article["source"],
                        "cn_title": result["cn_title"],
                        "cn_analysis": result["cn_analysis"],
                        "mental_model": result["mental_model"],
                        "case_study": result.get("case_study", "")
                    }

                    knowledge.insert(0, item)
                    save_knowledge(knowledge)

                    st.success("✅ 今日内容已生成，请返回【今日洞察】查看。")
