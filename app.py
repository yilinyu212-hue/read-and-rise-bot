import streamlit as st
import json, os, plotly.graph_objects as go

st.set_page_config(page_title="Read & Rise", layout="wide")

# --- 极简明亮 UI 样式 ---
st.markdown("""
<style>
    .stApp { background-color: #F8FAFC; }
    [data-testid="stSidebar"] { background-color: #0F172A; }
    .main-welcome { background: white; padding: 30px; border-radius: 20px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); border-left: 8px solid #3B82F6; }
    .tag-level { background: #DBEAFE; color: #1E40AF; padding: 4px 12px; border-radius: 15px; font-weight: bold; font-size: 0.8rem; }
    .tag-topic { background: #F1F5F9; color: #475569; padding: 4px 12px; border-radius: 15px; font-size: 0.8rem; margin-right: 5px; }
    h1, h2, h3 { color: #1E293B !important; }
</style>
""", unsafe_allow_html=True)

def load_data():
    if not os.path.exists("data.json"): return {"briefs": [], "books": []}
    with open("data.json", "r", encoding="utf-8") as f:
        try:
            d = json.load(f)
            if "books" not in d: d["books"] = []
            if "briefs" not in d: d["briefs"] = []
            return d
        except: return {"briefs": [], "books": []}

data = load_data()

# --- 侧边栏 ---
st.sidebar.markdown("<h2 style='color:white; text-align:center;'>🏹 Read & Rise</h2>", unsafe_allow_html=True)
menu = st.sidebar.radio("", ["🏠 主页 Dashboard", "🚀 全球内参", "📚 资产智库"])

if menu == "🏠 主页 Dashboard":
    # 1. 欢迎区
    st.markdown("""
    <div class="main-welcome">
        <h1>Hi, Leaders! 👋</h1>
        <p style="color:#64748B;">今天是 2026年01月19日。Read & Rise AI 已为您同步全球顶级智库数据。</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.write("")
    
    # 2. 语音播报区
    st.subheader("🎙️ 每日商业简报 (BBC Style)")
    if os.path.exists("daily_briefing.mp3"):
        st.audio("daily_briefing.mp3")
    else:
        st.info("🕒 音频正在通过 GitHub Actions 生成中，请稍后刷新...")

    st.divider()

    # 3. 今日重点推荐 (标签化)
    if data['briefs']:
        top = data['briefs'][0]
        st.subheader("🔥 今日重点推荐")
        c1, c2 = st.columns([0.6, 0.4])
        with c1:
            st.markdown(f"### {top['title']}")
            st.markdown(f"<span class='tag-level'>{top.get('reading_level','High')}</span>", unsafe_allow_html=True)
            st.write("")
            # 话题标签
            tags_html = "".join([f"<span class='tag-topic'>#{t}</span>" for t in top.get('tags', [])])
            st.markdown(tags_html, unsafe_allow_html=True)
            st.write("")
            st.success(f"**💡 核心洞察 (CN):**\n{top.get('cn_analysis')}")
        with c2:
            # 维度雷达图
            scores = top.get('model_scores', {"战略":80, "创新":70, "执行":75})
            fig = go.Figure(data=go.Scatterpolar(
                r=list(scores.values())+[list(scores.values())[0]],
                theta=list(scores.keys())+[list(scores.keys())[0]],
                fill='toself', line=dict(color='#3B82F6')
            ))
            fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])), height=350, margin=dict(t=30, b=30))
            st.plotly_chart(fig, use_container_width=True)

elif menu == "🚀 全球内参":
    st.header("Global Strategic Insights")
    for i, art in enumerate(data.get("briefs", [])):
        with st.expander(f"📍 {art['source']} | {art['title']}", expanded=(i==0)):
            tab1, tab2, tab3 = st.tabs(["中英解析", "反思流", "行动项"])
            with tab1:
                col_en, col_cn = st.columns(2)
                col_en.info(f"**English Summary**\n{art['en_summary']}")
                col_cn.success(f"**中文解析**\n{art['cn_analysis']}")
            with tab2:
                for q in art.get('reflection_flow', []): st.write(f"❓ {q}")
            with tab3:
                for act in art.get('action_points', []): st.write(f"✅ {act}")
            
            if st.button("📥 存入智库资产", key=f"s_{i}"):
                data["books"].append({"title": art['title'], "insight": art['cn_analysis']})
                with open("data.json", "w", encoding="utf-8") as f: json.dump(data, f, ensure_ascii=False)
                st.toast("资产入库成功！")

elif menu == "📚 资产智库":
    st.header("📚 已数字化的知识资产")
    for b in data.get("books", []):
        with st.container(border=True):
            st.subheader(b['title'])
            st.write(b.get('insight'))
