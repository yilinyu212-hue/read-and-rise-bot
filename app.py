import streamlit as st
import streamlit.components.v1 as components
import json, os, requests
from datetime import datetime

# --- 1. 基础配置与 Coach 植入 ---
st.set_page_config(page_title="Read & Rise", layout="wide", page_icon="🏹")

# 使用你提供的 Bot ID 植入 Coach
components.html(f"""
<script src="https://lf-cdn.coze.cn/obj/unpkg/flow-platform/chat-app-sdk/1.1.0-beta.3/libs/cn/index.js"></script>
<script>
  new CozeWebSDK.WebChatClient({{
    config: {{ bot_id: '7597670461476421647' }},
    componentProps: {{ title: 'Mentor Rize' }},
    ui: {{ base: {{ zIndex: 1000 }} }}
  }});
</script>
""", height=0)

# --- 2. 自动化配置 ---
API_KEY = "pat_DNy8zk5DxAsNDzVEIxkzweVaXo9hic4fDPagIAUjoepgLK2zL3bub16Mp3RxvsRY" # 👈 唯一需要你填的地方！在个人中心-令牌生成的那个 pat_ 开头的字符串
WORKFLOW_ID = "7462153549221150772" # 预设你的工作流ID

def load_data():
    if os.path.exists("data.json"):
        with open("data.json", "r", encoding="utf-8") as f:
            try:
                res = json.load(f)
                return res.get("items", []) if isinstance(res, dict) else res
            except: return []
    return []

def save_data(items):
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump({"items": items}, f, ensure_ascii=False, indent=4)

# --- 3. 侧边栏与导航 ---
items = load_data()
with st.sidebar:
    st.title("🏹 Read & Rise")
    page = st.radio("导航", ["🏠 Dashboard", "🚀 Intelligence Hub", "📚 Bookshelf", "🛠 Admin"])
    st.divider()
    st.info("AI Coach 已在右下角就绪")

# --- 4. 页面逻辑 ---

# A. 首页：展示今日重点和历史回顾
if page == "🏠 Dashboard":
    st.markdown(f"""<div style="background:#0F172A;padding:40px;border-radius:20px;color:white;">
        <h1>Hi, Leader! 👋</h1>
        <p>今天是 {datetime.now().strftime('%Y年%m月%d日')}</p>
    </div>""", unsafe_allow_html=True)
    
    if items:
        st.subheader("📍 今日更新")
        latest = items[0]
        st.info(f"**今日模型：{latest.get('mental_model', '加载中...')}**")
        
        st.subheader("📅 历史外刊回顾 (按日期存储)")
        for it in items:
            date_str = it.get('date', datetime.now().strftime('%Y-%m-%d'))
            with st.expander(f"【{date_str}】{it.get('cn_title')}"):
                st.write(it.get('cn_analysis')[:200] + "...")
                if st.button(f"详情", key=it.get('cn_title')):
                    st.session_state.current_article = it.get('cn_title')
                    # 可以在这里跳转页面

# B. 外刊详情页：左 Read 右 Rise
elif page == "🚀 Intelligence Hub":
    if items:
        sel = st.selectbox("选择要研读的文章", [i.get('cn_title') for i in items])
        it = next(i for i in items if i.get('cn_title') == sel)
        
        col_read, col_rise = st.columns(2)
        with col_read:
            st.markdown("### 📖 Read (中英总结)")
            st.info(f"**English:**\n\n{it.get('en_summary')}")
            st.success(f"**中文解析:**\n\n{it.get('cn_analysis')}")
            # 恢复音频功能
            if it.get('audio_file') and os.path.exists(it['audio_file']):
                st.audio(it['audio_file'])
        with col_rise:
            st.markdown("### 📈 Rise (深度拆解)")
            st.warning(f"**思维模型：{it.get('mental_model')}**")
            st.write(it.get('cn_analysis'))
    else:
        st.warning("暂无文章，请前往 Admin 运行抓取。")

# C. 后台管理：解决“自动存储”问题
elif page == "🛠 Admin":
    st.title("🛠 内容自动化中心")
    topic = st.text_input("输入今日关注的商业动态/主题")
    if st.button("🚀 启动扣子生成并永久存入网页"):
        headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
        payload = {"workflow_id": WORKFLOW_ID, "parameters": {"input": topic}}
        
        with st.spinner("AI 正在写稿并存入数据库..."):
            res = requests.post("https://api.coze.cn/v1/workflow/run", headers=headers, json=payload)
            if res.status_code == 200:
                new_article = json.loads(res.json().get('data'))
                # 自动增加日期字段，实现按日存储
                new_article['date'] = datetime.now().strftime('%Y-%m-%d')
                items.insert(0, new_article)
                save_data(items) # 写入 data.json，实现永久存储
                st.success("文章已存入历史库，首页已更新！")
            else:
                st.error(f"连接失败：{res.text}")
