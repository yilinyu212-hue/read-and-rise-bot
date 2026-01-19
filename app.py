import streamlit as st
import json, os, requests, plotly.graph_objects as go
from datetime import datetime

# ================= 1. 配置与样式 =================
st.set_page_config(page_title="Read & Rise Coach", layout="wide", page_icon="🏹")

st.markdown("""
    <style>
    .stApp { background-color: #F8FAFC; }
    .coach-card { background: linear-gradient(135deg, #0F172A 0%, #1E293B 100%); padding: 30px; border-radius: 20px; color: white; margin-bottom: 30px; border-left: 10px solid #38BDF8; }
    .card { background: white; padding: 20px; border-radius: 15px; border: 1px solid #E2E8F0; margin-bottom: 15px; }
    .tag { background: #F0F9FF; color: #0369A1; padding: 4px 12px; border-radius: 20px; font-size: 0.75rem; font-weight: 700; }
    </style>
""", unsafe_allow_html=True)

# ================= 2. 数据处理 =================
def load_data():
    default = {"briefs": [], "deep_articles": [], "weekly_question": {"cn": "请运行爬虫更新数据", "en": "Please run crawler"}, "update_time": ""}
    if not os.path.exists("data.json"): return default
    try:
        with open("data.json", "r", encoding="utf-8") as f:
            d = json.load(f)
            # 补全可能缺失的字段，防止 KeyError
            for key in default:
                if key not in d: d[key] = default[key]
            return d
    except: return default

def save_data(d):
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False, indent=4)

data = load_data()

# ================= 3. 导航栏 =================
with st.sidebar:
    st.title("🏹 Read & Rise")
    menu = st.radio("Navigation", ["🏠 教练仪表盘", "🚀 爬虫快报", "✍️ 深度精读上传", "🎙️ 私人教练对话"])
    st.divider()
    if st.checkbox("🛠️ 管理员模式"):
        st.subheader("手动修正提问")
        q_cn = st.text_input("中文提问", data['weekly_question'].get('cn', ""))
        q_en = st.text_input("英文提问", data['weekly_question'].get('en', ""))
        if st.button("保存提问"):
            data['weekly_question'] = {"cn": q_cn, "en": q_en}
            save_data(data)
            st.success("已更新")

# ================= 4. 各频道实现 =================

# --- 🏠 教练仪表盘 ---
if menu == "🏠 教练仪表盘":
    st.markdown(f"""
    <div class="coach-card">
        <h4 style="color: #38BDF8; margin:0; letter-spacing:1px;">🎙️ WEEKLY INQUIRY / 每周提问</h4>
        <p style="font-size: 1.1rem; color: #94A3B8; font-style: italic; margin-top:15px;">"{data['weekly_question'].get('en')}"</p>
        <p style="font-size: 1.5rem; font-weight: bold; margin-top:5px;">“{data['weekly_question'].get('cn')}”</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 1])
    with col1:
        st.subheader("💡 最新深度精读")
        if data["deep_articles"]:
            top = data["deep_articles"][-1]
            st.markdown(f"<div class='card'><b>{top['title']}</b><br><br><span class='tag'>{top['related_model']}</span></div>", unsafe_allow_html=True)
        else:
            st.info("暂无深度文章，请前往上传页面。")
    with col2:
        st.subheader("📊 智库更新状态")
        st.write(f"快报数量: {len(data['briefs'])}")
        st.write(f"深度文章: {len(data['deep_articles'])}")
        st.write(f"最后同步: {data['update_time']}")

# --- 🚀 爬虫快报 ---
elif menu == "🚀 爬虫快报":
    st.header("🚀 全球智库实时快报")
    for b in data.get("briefs", []):
        st.markdown(f"""
        <div class="card">
            <small style="color:#64748B">{b['source']} | {b.get('time', '')}</small>
            <p style="margin: 5px 0;"><b>{b['title']}</b></p>
            <a href="{b['link']}" target="_blank" style="text-decoration:none; color:#38BDF8; font-size:0.8rem;">查看原文 →</a>
        </div>
        """, unsafe_allow_html=True)

# --- ✍️ 深度精读上传 ---
elif menu == "✍️ 深度精读上传":
    st.header("✍️ 投喂 AI 教练深度内容")
    content = st.text_area("粘贴外刊全文或核心内容...", height=350)
    if st.button("开始 AI 联动解析"):
        if not content:
            st.warning("请输入内容")
        else:
            with st.spinner("教练正在深度研读..."):
                prompt = f"请深度解析这篇文章：{content[:3000]}。必须返回JSON格式：{{'title':'标题', 'related_model':'匹配模型', 'analysis':'深度解析内容', 'q_cn':'生成的中文提问', 'q_en':'Generated English Question'}}"
                # 这里调用您的 API 逻辑 (简写)
                api_key = os.getenv("DEEPSEEK_API_KEY")
                res = requests.post("https://api.deepseek.com/chat/completions", 
                                   headers={"Authorization": f"Bearer {api_key}"},
                                   json={"model":"deepseek-chat", "messages":[{"role":"user","content":prompt}], "response_format":{"type":"json_object"}})
                new_art = res.json()['choices'][0]['message']['content']
                new_art = json.loads(new_art)
                
                # 更新数据
                data["deep_articles"].append(new_art)
                data["weekly_question"] = {"cn": new_art['q_cn'], "en": new_art['q_en']}
                save_data(data)
                st.success("深度文章已录入，教练提win已同步更新！")

# --- 🎙️ 私人教练对话 ---
elif menu == "🎙️ 私人教练对话":
    st.header("🎙️ AI Coach Session")
    if "messages" not in st.session_state: st.session_state.messages = []
    
    for m in st.session_state.messages:
        with st.chat_message(m["role"]): st.markdown(m["content"])

    if p := st.chat_input("输入你的经营难题..."):
        st.session_state.messages.append({"role": "user", "content": p})
        with st.chat_message("user"): st.markdown(p)
        
        with st.chat_message("assistant"):
            # 这里的对话逻辑可以加入 data["deep_articles"] 作为背景
            st.markdown("收到。基于您上传的智库文章，我建议...")
