import streamlit as st
import json, os, requests, plotly.graph_objects as go

# ================= 1. 样式与数据 =================
st.set_page_config(page_title="Read & Rise", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #F1F5F9; }
    .coach-card { background: linear-gradient(135deg, #0F172A 0%, #1E293B 100%); padding: 30px; border-radius: 20px; color: white; border-left: 10px solid #38BDF8; margin-bottom: 25px; }
    .card { background: white; padding: 20px; border-radius: 15px; border: 1px solid #E2E8F0; margin-bottom: 15px; }
    .vocab-card { background: #F8FAFC; border-left: 4px solid #0369A1; padding: 12px; border-radius: 8px; margin-bottom: 10px; }
    .quote { font-style: italic; color: #475569; border-left: 3px solid #CBD5E1; padding-left: 15px; margin: 10px 0; }
    .tag { background: #E0F2FE; color: #0369A1; padding: 3px 10px; border-radius: 12px; font-size: 0.75rem; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

def load_data():
    if os.path.exists("data.json"):
        with open("data.json", "r", encoding="utf-8") as f: return json.load(f)
    return {"briefs": [], "deep_articles": [], "weekly_question": {"cn":"加载中", "en":"Loading"}}

data = load_data()

def draw_radar(scores):
    fig = go.Figure(data=go.Scatterpolar(r=list(scores.values())+[list(scores.values())[0]], theta=list(scores.keys())+[list(scores.keys())[0]], fill='toself', line_color='#38BDF8'))
    fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])), showlegend=False, height=300, margin=dict(l=30, r=30, t=30, b=30))
    return fig

# ================= 2. 侧边栏 =================
with st.sidebar:
    st.title("🏹 Read & Rise")
    menu = st.radio("频道", ["🏠 Dashboard", "🚀 今日智库", "✍️ 深度精读上传", "🎙️ AI 教练对话"])
    if st.checkbox("🛠️ 管理员权限"):
        new_q_cn = st.text_input("本周提问(中)", data['weekly_question']['cn'])
        new_q_en = st.text_input("本周提问(英)", data['weekly_question']['en'])
        if st.button("保存提问"):
            data['weekly_question'] = {"cn": new_q_cn, "en": new_q_en}
            with open("data.json", "w", encoding="utf-8") as f: json.dump(data, f, ensure_ascii=False, indent=4)
            st.success("已更新")

# ================= 3. 频道实现 =================

if menu == "🏠 Dashboard":
    st.markdown(f"""<div class="coach-card">
        <h4 style="color: #38BDF8; margin:0;">🎙️ WEEKLY INQUIRY / 每周提问</h4>
        <p style="color: #94A3B8; font-style: italic; margin-top:10px;">"{data['weekly_question']['en']}"</p>
        <p style="font-size: 1.4rem; font-weight: bold;">“{data['weekly_question']['cn']}”</p>
    </div>""", unsafe_allow_html=True)
    
    col1, col2 = st.columns([1.5, 1])
    with col1:
        st.subheader("💡 核心联动建议")
        all_arts = data['deep_articles'] + data['briefs']
        if all_arts:
            top = all_arts[0]
            st.markdown(f"""<div class="card">
                <b>最新研读：</b>{top['title']}<br><br>
                <span class="tag">🧠 模型: {top.get('related_model','N/A')}</span>
                <span class="tag">📚 推荐: {top.get('related_book','《原则》')}</span>
            </div>""", unsafe_allow_html=True)
    with col2:
        st.subheader("📊 领导力维度")
        if all_arts: st.plotly_chart(draw_radar(all_arts[0]['scores']), use_container_width=True)

elif menu == "🚀 今日智库":
    all_arts = data['deep_articles'] + data['briefs']
    for art in all_arts:
        with st.expander(f"📌 [{art.get('source','智库')}] {art['title']}"):
            tab1, tab2, tab3 = st.tabs(["📑 摘要与案例", "🎙️ 词汇与金句", "🌊 反思流"])
            with tab1:
                st.write("**English Summary:**"); st.info(art['en_summary'])
                st.write("**中文深度解析:**"); st.write(art['cn_summary'])
                st.markdown(f"**🔍 案例分析:** {art.get('case_study','暂无案例')}")
            with tab2:
                for gs in art.get('golden_sentences', []):
                    st.markdown(f"<div class='quote'>{gs['en']}<br><b>{gs['cn']}</b></div>", unsafe_allow_html=True)
                st.divider()
                st.write("**高管词汇库:**")
                for v in art.get('vocab_bank', []):
                    st.markdown(f"<div class='vocab-card'><b>{v['word']}</b>: {v['meaning']}<br><small>Ex: {v['example']}</small></div>", unsafe_allow_html=True)
            with tab3:
                for rf in art.get('reflection_flow', []): st.warning(rf)
            st.link_button("阅读原文", art['link'])

elif menu == "✍️ 深度精读上传":
    st.header("✍️ 投喂深度长文")
    text = st.text_area("在此粘贴文章全文...", height=400)
    if st.button("开始 AI 联动解析"):
        # 调用 AI 解析逻辑（略，同 crawler.py）
        st.success("文章已解析并加入智库库！")

elif menu == "🎙️ AI 教练对话":
    st.header("🎙️ Read & Rise AI Coach")
    if "messages" not in st.session_state: st.session_state.messages = []
    for m in st.session_state.messages:
        with st.chat_message(m["role"]): st.markdown(m["content"])
    if p := st.chat_input("向教练提问..."):
        st.session_state.messages.append({"role": "user", "content": p})
        with st.chat_message("user"): st.markdown(p)
        with st.chat_message("assistant"):
            kb = str(data['deep_articles'][-2:])
            st.write(f"基于您的智库文章分析，我认为...") 
            # 此处调用 DeepSeek 对话接口
