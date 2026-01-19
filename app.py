import streamlit as st
import json, os, requests, plotly.graph_objects as go
from datetime import datetime

st.set_page_config(page_title="Read & Rise", layout="wide", page_icon="🏹")

# --- 高端 UI 视觉设计 ---
st.markdown("""
<style>
    .main { background-color: #F1F5F9; }
    .stApp { background-color: #F1F5F9; }
    [data-testid="stSidebar"] { background: #0F172A; }
    .brief-card { background: white; padding: 25px; border-radius: 15px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); margin-bottom: 25px; border-top: 5px solid #38BDF8; }
    .audio-section { background: #1E293B; color: white; padding: 20px; border-radius: 15px; margin-bottom: 30px; }
    .stButton>button { width: 100%; background-color: #38BDF8; color: white; border: none; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

def load_data():
    if not os.path.exists("data.json"): return {"briefs": [], "books": []}
    with open("data.json", "r", encoding="utf-8") as f:
        d = json.load(f)
        if "books" not in d: d["books"] = []
        return d

data = load_data()

# --- 侧边导航 ---
st.sidebar.markdown("<h1 style='color:white; text-align:center;'>🏹 Read & Rise</h1>", unsafe_allow_html=True)
menu = st.sidebar.radio("", ["🏠 决策仪表盘", "🚀 全球商业内参", "📚 资产智库", "⚙️ 资产录入"])

if menu == "🏠 决策仪表盘":
    st.markdown("### Executive Dashboard")
    
    # 🎙️ 语音播报模块
    st.markdown('<div class="audio-section"><h4>🎙️ 每日全球商业播报 (BBC Style)</h4><p style="opacity:0.8;">基于最新的 6 大商业信源自动生成</p></div>', unsafe_allow_html=True)
    if os.path.exists("daily_briefing.mp3"):
        st.audio("daily_briefing.mp3")
    else:
        st.info("🕒 音频正在通过 GitHub 后台生成中...")

    # 雷达图分析
    if data['briefs']:
        scores = data['briefs'][0].get('model_scores', {"Strategy":50, "Innovation":50, "Execution":50, "Insight":50})
        fig = go.Figure(data=go.Scatterpolar(
            r=list(scores.values())+[list(scores.values())[0]],
            theta=list(scores.keys())+[list(scores.keys())[0]],
            fill='toself', line=dict(color='#38BDF8')
        ))
        fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])), height=400)
        st.plotly_chart(fig, use_container_width=True)

elif menu == "🚀 全球商业内参":
    st.markdown("### 🚀 Global Market Intelligence")
    for i, art in enumerate(data.get("briefs", [])):
        st.markdown(f'<div class="brief-card">', unsafe_allow_html=True)
        st.subheader(f"📍 {art['source']} | {art['title']}")
        
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("**🇬🇧 Executive Summary (EN)**")
            st.write(art.get('en_summary'))
        with c2:
            st.markdown("**🇨🇳 深度策略分析 (CN)**")
            st.write(art.get('cn_analysis'))
        
        st.divider()
        if st.button(f"📥 存入 Read & Rise 数字资产库", key=f"btn_{i}"):
            data["books"].append({"title": art['title'], "concept": art['source'], "insight": art['cn_analysis']})
            with open("data.json", "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            st.toast(f"《{art['title']}》已永久入库")
        st.markdown('</div>', unsafe_allow_html=True)

elif menu == "📚 资产智库":
    st.header("📚 已数字化的知识资产")
    for b in data.get("books", []):
        with st.container(border=True):
            st.subheader(b['title'])
            st.caption(f"来源/模型: {b.get('concept', 'Manual')}")
            st.write(b.get('insight'))

elif menu == "⚙️ 资产录入":
    with st.form("add_asset"):
        t = st.text_input("资产/书名/模型名称")
        c = st.text_input("所属分类/核心逻辑")
        i = st.text_area("深度洞察与应用建议")
        if st.form_submit_button("同步至智库"):
            data["books"].append({"title":t, "concept":c, "insight":i})
            with open("data.json", "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            st.success("资产入库成功！")
