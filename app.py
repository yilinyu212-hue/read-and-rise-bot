import streamlit as st
import streamlit.components.v1 as components
import json, os, requests
from datetime import datetime

# --- 1. 基础配置 ---
st.set_page_config(page_title="Read & Rise", layout="wide", page_icon="🏹")

# --- 2. 傻瓜式植入 AI Coach (右下角悬浮球) ---
# 请将下方的 '你的_BOT_ID' 替换为你浏览器地址栏 bot/ 后面的数字
components.html("""
<script src="https://lf-cdn.coze.cn/obj/unpkg/flow-platform/chat-app-sdk/1.1.0-beta.3/libs/cn/index.js"></script>
<script>
  new CozeWebSDK.WebChatClient({
    config: {
      bot_id: '7597670461476421647', # 👈 1. 这里填入你的 Bot ID
    },
    componentProps: {
      title: 'Mentor Rize Coach',
    },
  });
</script>
""", height=0)

# --- 3. 核心功能函数 ---
def call_coze_workflow(query):
    """调用扣子工作流获取深度拆解内容"""
    API_KEY = "pat_DNy8zk5DxAsNDzVEIxkzweVaXo9hic4fDPagIAUjoepgLK2zL3bub16Mp3RxvsRY" # 👈 2. 这里填入你刚才生成的长令牌
    WORKFLOW_ID = "pat_eaOALk7CRZrn8psvXRZ3erf7hiwnrgHoFmoq4erzqVg7sCVloqAU1ov5G7fb9Xar" # 👈 3. 这里填入工作流 ID
    
    url = "https://api.coze.cn/v1/workflow/run"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    # 注意：'input' 必须和你工作流开始节点的变量名一致
    payload = {"workflow_id": WORKFLOW_ID, "parameters": {"input": query}}
    
    try:
        res = requests.post(url, headers=headers, json=payload)
        # 假设工作流直接输出 JSON 字符串结果
        return res.json().get('data')
    except:
        return None

def load_data():
    if os.path.exists("data.json"):
        with open("data.json", "r", encoding="utf-8") as f:
            try:
                res = json.load(f)
                return res.get("items", []) if isinstance(res, dict) else res
            except: return []
    return []

# --- 4. 初始化状态 ---
if "messages" not in st.session_state: st.session_state.messages = []
if "page" not in st.session_state: st.session_state.page = "🏠 Dashboard"
if "authenticated" not in st.session_state: st.session_state.authenticated = False

ADMIN_PASSWORD = "your_password"
items = load_data()

# --- 5. 视觉样式 ---
st.markdown("""
<style>
    .stApp { background-color: #F8FAFC; }
    .podcast-card {
        background: linear-gradient(135deg, #0F172A 0%, #1E293B 100%);
        padding: 30px; border-radius: 20px; color: white; margin-bottom: 25px;
        box-shadow: 0 10px 20px rgba(0,0,0,0.15); border: 1px solid #334155;
    }
    .chip { padding: 4px 12px; border-radius: 8px; font-weight: 700; font-size: 0.75rem; display: inline-block; margin-right: 8px; }
    .chip-rise { background: #DCFCE7; color: #166534; }
    .content-card { background: white; padding: 25px; border-radius: 20px; border: 1px solid #E2E8F0; margin-bottom: 20px; }
</style>
""", unsafe_allow_html=True)

# --- 6. 侧边栏导航 ---
with st.sidebar:
    st.markdown("## 🏹 Read & Rise")
    if st.button("🏠 Dashboard", use_container_width=True): st.session_state.page = "🏠 Dashboard"
    if st.button("🚀 Intelligence Hub", use_container_width=True): st.session_state.page = "🚀 Intelligence Hub"
    st.divider()
    with st.expander("🔐 Admin Access"):
        pwd = st.text_input("Key", type="password")
        if pwd == ADMIN_PASSWORD:
            st.session_state.authenticated = True
            if st.button("Open CMS"): st.session_state.page = "🛠 Admin"

# --- 7. 页面逻辑 ---

# A. 管理员后台：一键自动化更新
if st.session_state.page == "🛠 Admin" and st.session_state.authenticated:
    st.title("🛠 CMS - 自动化内容中心")
    
    topic = st.text_input("输入今日抓取主题 (如: 马斯克最新动向)", "Elon Musk")
    if st.button("🚀 运行 AI 智库并更新网页"):
        with st.spinner("Mentor Rize 正在调阅全球数据并进行模型拆解..."):
            raw_res = call_coze_workflow(topic)
            if raw_res:
                try:
                    # 尝试将返回的字符串转为字典
                    new_item = json.loads(raw_res)
                    items.insert(0, new_item) # 置顶新内容
                    with open("data.json", "w", encoding="utf-8") as f:
                        json.dump({"items": items}, f, ensure_ascii=False)
                    st.success("文章已自动生成并推送到首页！")
                except:
                    st.error("工作流返回格式错误，请确保输出为标准 JSON。")
            else:
                st.error("抓取失败，请检查 API Token 和 Workflow ID。")

# B. 研读中心
elif st.session_state.page == "🚀 Intelligence Hub":
    if items:
        with st.sidebar:
            sel = st.radio("文章列表", [i.get('cn_title', '未命名') for i in items])
        it = next(i for i in items if i.get('cn_title') == sel)
        
        st.markdown(f'<div class="podcast-card">🎙️ <small>INTELLIGENCE HUB</small><h2>{it["cn_title"]}</h2></div>', unsafe_allow_html=True)
        
        t1, t2 = st.tabs(["💡 AI 洞察", "🌐 中英对照"])
        with t1:
            st.markdown(f'<div class="content-card"><h4>核心深度解析</h4>{it.get("cn_analysis")}</div>', unsafe_allow_html=True)
        with t2:
            col_en, col_cn = st.columns(2)
            col_en.info(f"**English Summary:**\n\n{it.get('en_summary')}")
            col_cn.success(f"**中文解析:**\n\n{it.get('cn_analysis')}")

# C. 首页 Dashboard
elif st.session_state.page == "🏠 Dashboard":
    st.title("Hi, Leader! 👋")
    st.caption(f"Today is {datetime.now().strftime('%Y-%m-%d')}")
    for it in items:
        st.markdown(f"""<div class="content-card">
            <span class="chip chip-rise">Model: {it.get('mental_model', 'Mental Model')}</span>
            <h3 style="margin:10px 0;">{it.get('cn_title')}</h3>
            <p style="color:#64748B;">{it.get('cn_analysis', '')[:150]}...</p>
        </div>""", unsafe_allow_html=True)
