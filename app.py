import streamlit as st
import streamlit.components.v1 as components
import json, os, requests
from datetime import datetime

# --- 1. 页面配置与 Coach 悬浮球 ---
st.set_page_config(page_title="Read & Rise | 管理者内参", layout="wide", page_icon="🏹")

# 悬浮球设置
components.html(f"""
<script src="https://lf-cdn.coze.cn/obj/unpkg/flow-platform/chat-app-sdk/1.1.0-beta.3/libs/cn/index.js"></script>
<script>
  new CozeWebSDK.WebChatClient({{
    config: {{ bot_id: '7597670461476421647' }},
    componentProps: {{ title: 'Mentor Rize Coach' }},
    ui: {{ base: {{ zIndex: 1000 }}, chatButton: {{ title: '咨询 Coach' }} }}
  }});
</script>
""", height=0)

# --- 2. 身份认证与 API 配置 ---
API_KEY = "pat_jGg7SBGnKdh5oSsb9WoByDhSTEuCYzreP4xQSPJjym27HE11vnFpyv7zQfweC4dp"
WORKFLOW_ID = "7597720250343424040"

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

# --- 3. UI 样式：高端灰蓝风格 ---
st.markdown("""
<style>
    .stApp { background-color: #F8FAFC; }
    [data-testid="stSidebar"] { background-color: #F1F5F9; border-right: 1px solid #E2E8F0; }
    .content-card { background: white; padding: 24px; border-radius: 12px; border: 1px solid #E2E8F0; box-shadow: 0 4px 12px rgba(0,0,0,0.03); margin-bottom: 20px; }
    .article-text { line-height: 1.8; font-size: 16px; color: #334155; }
    .section-header { font-weight: 800; color: #1E293B; border-left: 4px solid #3B82F6; padding-left: 12px; margin-bottom: 15px; }
</style>
""", unsafe_allow_html=True)

items = load_data()

# --- 4. 侧边栏 ---
with st.sidebar:
    st.markdown("<h2 style='color: #1E293B;'>🏹 Read & Rise</h2>", unsafe_allow_html=True)
    st.caption("专注领导力进阶与深度阅读")
    st.divider()
    page = st.radio("前往专区", ["🏠 Dashboard", "🚀 Intelligence Hub", "📚 决策书架", "⚙️ 后台同步"])

# --- 5. 页面实现 ---
if page == "🏠 Dashboard":
    st.markdown("<h1 style='color: #1E293B;'>Morning, Leader!</h1>", unsafe_allow_html=True)
    st.markdown(f"**{datetime.now().strftime('%m月%d日')}** · 开启你的全天候智囊团")
    
    if items:
        latest = items[0]
        st.markdown(f"""
        <div class="content-card">
            <p style='color:#64748B; font-size:12px;'>今日核心模型</p >
            <h2 style='color:#2563EB; margin:0;'>{latest.get('mental_model', '战略思考')}</h2>
            <p style='color:#475569;'>{latest.get('cn_title', '新文章已入库')}</p >
        </div>
        """, unsafe_allow_html=True)
        
        st.subheader("🗓 历史研读回顾")
        for it in items:
            with st.expander(f"📅 {it.get('date')} | {it.get('cn_title', '深度解析')}"):
                st.write(it.get('cn_analysis', '内容正在生成中...')[:150] + "...")
    else:
        st.info("暂无数据，请前往『后台同步』抓取今日外刊。")

elif page == "🚀 Intelligence Hub":
    if items:
        sel = st.selectbox("选择研读篇目", [i.get('cn_title') for i in items])
        it = next(i for i in items if i.get('cn_title') == sel)
        
        st.markdown(f"<h1 style='color: #1E293B;'>{it.get('cn_title')}</h1>", unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            st.markdown('<div class="section-header">READ | 精华提取</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="content-card article-text">{it.get("cn_analysis")}</div>', unsafe_allow_html=True)
        with col2:
            st.markdown('<div class="section-header">RISE | 管理启发</div>', unsafe_allow_html=True)
            st.success(f"思维模型：{it.get('mental_model')}")
            st.write("💡 **实战建议：**\n1. 评估该趋势对你所在行业的影响。\n2. 尝试在本周例会中使用该思维模型。")
    else:
        st.warning("暂无内容。")

elif page == "⚙️ 后台同步":
    st.title("🛠 系统自动化后台")
    topic = st.text_input("输入今日关注的主题", placeholder="例如：人工智能对零售业的重构")
    if st.button("🚀 启动抓取并同步"):
        headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
        payload = {"workflow_id": WORKFLOW_ID, "parameters": {"input": topic}}
        
        with st.spinner("Mentor Rize 正在穿透信息噪音..."):
            res = requests.post("https://api.coze.cn/v1/workflow/run", headers=headers, json=payload)
            if res.status_code == 200:
                try:
                    # 关键修复：同时兼容 'output' 变量和结构化变量
                    data_raw = json.loads(res.json().get('data'))
                    content = data_raw.get('output') or data_raw.get('cn_analysis') or "内容解析为空"
                    
                    new_item = {
                        "cn_title": data_raw.get('cn_title') or f"关于 {topic} 的深度分析",
                        "cn_analysis": content,
                        "mental_model": data_raw.get('mental_model') or "决策优化模型",
                        "date": datetime.now().strftime('%Y-%m-%d')
                    }
                    items.insert(0, new_item)
                    save_data(items)
                    st.success("同步成功！请返回 Dashboard 查看。")
                except Exception as e:
                    st.error(f"解析失败: {str(e)}")
            else:
                st.error(f"连接失败。状态码: {res.status_code}")
