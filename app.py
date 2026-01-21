import streamlit as st
from backend.engine import run_rize_insight
from datetime import datetime
import json, os

# --- 核心配置 ---
API_KEY = "pat_jGg7SBGnKdh5oSsb9WoByDhSTEuCYzreP4xQSPJjym27HE11vnFpyv7zQfweC4dp"
WORKFLOW_ID = "7597720250343424040"
DB_PATH = "data/knowledge.json"

st.set_page_config(page_title="Read & Rise | 行政简报", layout="wide")

def load_db():
    if os.path.exists(DB_PATH) and os.path.getsize(DB_PATH) > 0:
        with open(DB_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_to_db(new_item):
    db = load_db()
    new_item['date'] = datetime.now().strftime("%Y-%m-%d")
    db.insert(0, new_item)
    with open(DB_PATH, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=4)

# --- UI 渲染 ---
with st.sidebar:
    st.title("🏹 Read & Rise")
    st.markdown("---")
    menu = st.radio("功能导航", ["🏠 决策仪表盘", "⚙️ 自动化同步"])

if menu == "🏠 决策仪表盘":
    st.header("Executive Insight Dashboard")
    items = load_db()
    if not items:
        st.info("库中尚无内容。请前往“自动化同步”开启今日抓取。")
    else:
        for it in items:
            with st.expander(f"📅 {it['date']} | {it['title']}"):
                st.info(f"💡 核心模型：{it['model']}")
                st.markdown(it['content'])

elif menu == "⚙️ 自动化同步":
    st.title("🛠 认知引擎后台")
    topic = st.text_input("输入今日研究主题（如：AI对高管决策的影响）")
    if st.button("🚀 启动全球抓取任务"):
        with st.spinner("Mentor Rize 正在调取全球数据库并进行模型拆解..."):
            result = run_rize_insight(topic, API_KEY, WORKFLOW_ID)
            if result:
                save_to_db(result)
                st.success(f"同步成功！《{result['title']}》已入库。")
            else:
                st.error("同步失败。原因：API连接或工作流返回异常。")
