import streamlit as st
import json, os, requests, plotly.graph_objects as go

# ================= 1. 初始化 =================
st.set_page_config(page_title="Read & Rise", layout="wide", page_icon="🏹")

# 引入样式
st.markdown("""
    <style>
    .stApp { background-color: #F8FAFC; }
    .coach-card { background: linear-gradient(135deg, #0F172A 0%, #1E293B 100%); padding: 30px; border-radius: 20px; color: white; border-left: 10px solid #38BDF8; margin-bottom: 25px; }
    .card { background: white; padding: 20px; border-radius: 15px; border: 1px solid #E2E8F0; margin-bottom: 15px; }
    .vocab-card { background: #F1F5F9; border-left: 4px solid #0369A1; padding: 12px; border-radius: 8px; margin-bottom: 10px; }
    .quote { font-style: italic; color: #475569; border-left: 3px solid #CBD5E1; padding-left: 15px; margin: 10px 0; }
    .tag { background: #E0F2FE; color: #0369A1; padding: 3px 10px; border-radius: 12px; font-size: 0.75rem; font-weight: bold; margin-right: 5px; }
    </style>
""", unsafe_allow_html=True)

def load_data():
    default = {"briefs": [], "deep_articles": [], "weekly_question": {"cn": "加载中...", "en": "Loading..."}}
    if not os.path.exists("data.json"): return default
    try:
        with open("data.json", "r", encoding="utf-8") as f:
            d = json.load(f)
            return d if "weekly_question" in d else default
    except: return default

data = load_data()

def draw_radar(scores):
    categories = list(scores.keys())
    values = list(scores.values())
    fig = go.Figure(data=go.Scatterpolar(r=values + [values[0]], theta=categories + [categories[0]], fill='toself', line_color='#38BDF8'))
    fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])), showlegend=False, height=300, margin=dict(l=30, r=30, t=30, b=30))
    return fig

# ================= 2. 侧边栏 =================
with st.sidebar:
    st.title("🏹 Read & Rise")
    menu = st.radio("导航", ["🏠 Dashboard", "🚀 今日内参", "✍️ 深度精读上传", "🎙️ AI 教练对话"])
    st.divider()
    if st.checkbox("🛠️ 管理员权限"):
        new_q_cn = st.text_input("本周提问(中)", data.get('weekly_question', {}).get('cn', ""))
        new_q_en = st.text_input("本周提问(英)", data.get('weekly_question', {}).get('en', ""))
        if st.button("更新提问"):
            data['weekly_question'] = {"cn": new_q_cn, "en": new_q_en}
            with open("data.json", "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            st.success("已更新")

# ================= 3. 页面实现 =================

if menu == "🏠 Dashboard":
    st.markdown(f"""<div class="coach-card">
        <h4 style="color: #38BDF8; margin:0; letter-spacing:1px;">🎙️ WEEKLY INQUIRY / 每周提问</h4>
        <p style="color: #94A3B8; font-style: italic; margin-top:15px;">"{data['weekly_question'].get('en')}"</p>
        <p style="font-size: 1.5rem; font-weight: bold; margin-top:5px;">“{data['weekly_question'].get('cn')}”</p>
    </div>""", unsafe_allow_html=True)
    
    col1, col2 = st.columns([1.5, 1])
    with col1:
        st.subheader("💡 核心联动建议")
        all_arts = data.get('deep_articles', []) + data.get('briefs', [])
        if all_arts:
            top = all_arts[0]
            st.markdown(f"""<div class="card">
                <b>最新研读：</b>{top['title']}<br><br>
                <span class="tag">🧠 模型: {top.get('related_model','N/A')}</span>
                <span class="tag">📚 推荐: {top.get('related_book','《原则》')}</span>
            </div>""", unsafe_allow_html=True)
        else:
            st.info("数据解析中，请稍后刷新...")
    with col2:
        st.subheader("📊 领导力维度")
        if all_arts:
            st.plotly_chart(draw_radar(all_arts[0].get('scores', {"Strategy":80, "Insight":80})), use_container_width=True)

elif menu == "🚀 今日内参":
    st.header("🚀 深度智库解析")
    all_arts = data.get('deep_articles', []) + data.get('briefs', [])
    for art in all_arts:
        with st.expander(f"📌 [{art.get('source','智库')}] {art['title']}"):
            tab1, tab2, tab3 = st.tabs(["📑 深度摘要", "🎙️ 词汇金句", "🔍 案例反思"])
            with tab1:
                st.write("**English Summary:**")
                st.info(art.get('en_summary', "Processing..."))
                st.write("**中文深度解析:**")
                st.write(art.get('cn_summary', "解析中..."))
                st.link_button("阅读原文", art['link'])
            with tab2:
                st.write("**核心金句:**")
                for gs in art.get('golden_sentences', []):
                    st.markdown(f"<div class='quote'>{gs['en']}<br><b>{gs['cn']}</b></div>", unsafe_allow_html=True)
                st.divider()
                st.write("**管理词汇库:**")
                for v in art.get('vocab_bank', []):
                    st.markdown(f"<div class='vocab-card'><b>{v['word']}</b>: {v['meaning']}<br><small>例句: {v['example']}</small></div>", unsafe_allow_html=True)
            with tab3:
                st.markdown(f"**🔍 案例分析:** \n {art.get('case_study','暂无案例数据')}")
                st.divider()
                st.write("**🌊 反思流:**")
                for rf in art.get('reflection_flow', []):
                    st.warning(rf)

elif menu == "✍️ 深度精读上传":
    st.header("✍️ 投喂深度长文")
    text = st.text_area("在此粘贴文章全文...", height=400)
    if st.button("开始 AI 联动解析"):
        if text:
            with st.spinner("AI 首席教练正在深度研读并匹配模型..."):
                # 这里调用 AI 解析逻辑，并将结果 append 到 data['deep_articles']
                st.info("解析功能已连接，正在处理...")
        else:
            st.warning("内容为空")

elif menu == "🎙️ AI 教练对话":
    st.header("🎙️ Read & Rise AI Coach")
    st.info("我是您的 AI 商业教练。我会基于智库内容助您解决管理困境。")
    # 对话逻辑实现...
