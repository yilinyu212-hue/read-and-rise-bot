# app.py
import streamlit as st
from backend.engine import run_rize_insight
from datetime import datetime
import json, os

# 导入配置
API_KEY = "pat_jGg7SBGnKdh5oSsb9WoByDhSTEuCYzreP4xQSPJjym27HE11vnFpyv7zQfweC4dp"
WORKFLOW_ID = "7597720250343424040"

st.set_page_config(page_title="Read & Rise", layout="wide")

# 加载历史数据逻辑
def load_db():
    if os.path.exists("data/knowledge.json"):
        with open("data/knowledge.json", "r") as f: return json.load(f)
    return []

# --- 界面排版 ---
st.sidebar.title("🏹 Read & Rise")
menu = st.sidebar.radio("专区", ["🏠 每日简报", "⚙️ 同步后台"])

if menu == "🏠 每日简报":
    st.header("Morning, Leader! 👋")
    db = load_db()
    if not db:
        st.info("尚未同步内容，请先前往后台。")
    for item in db:
        with st.expander(f"📅 {item['date']} | {item['title']}"):
            # 采用卡片式排版，避免文字拥挤
            st.markdown(f"### {item['model']}")
            st.write(item['content'])

elif menu == "⚙️ 同步后台":
    st.title("🛠 认知引擎管理")
    topic = st.text_input("输入今日研究主题")
    if st.button("开始同步"):
        with st.spinner("正在链接扣子并生成内容..."):
            result = run_rize_insight(topic, API_KEY, WORKFLOW_ID)
            if result:
                # 存入数据库
                current_db = load_db()
                result['date'] = datetime.now().strftime("%Y-%m-%d")
                current_db.insert(0, result)
                with open("data/knowledge.json", "w") as f: json.dump(current_db, f)
                st.success("同步成功！")
            else:
                st.error("同步失败，请检查 API Token 权限。")
