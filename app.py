import streamlit as st
import json, os, plotly.graph_objects as go
from datetime import datetime

st.set_page_config(page_title="Read & Rise", layout="wide")

# --- 焕新 UI 样式：明亮、高级、易读 ---
st.markdown("""
<style>
    .stApp { background-color: #F8FAFC; }
    [data-testid="stSidebar"] { background-color: #0F172A; }
    .executive-card { 
        background-color: white; 
        padding: 30px; 
        border-radius: 20px; 
        box-shadow: 0 10px 25px rgba(0,0,0,0.05);
        margin-bottom: 25px;
        border-left: 6px solid #3B82F6;
    }
    h1, h2, h3 { color: #1E293B !important; font-family: 'Inter', sans-serif; }
    p, li { color: #475569 !important; font-size: 1.05rem; line-height: 1.6; }
    .level-tag { 
        background: #EFF6FF; color: #1D4ED8; padding: 4px 12px; border-radius: 20px; 
        font-size: 0.8rem; font-weight: bold; border: 1px solid #DBEAFE;
    }
    .topic-tag { 
        background: #F1F5F9; color: #64748B; padding: 4px 12px; border-radius: 20px; 
        font-size: 0.8rem; margin-right: 5px;
    }
</style>
""", unsafe_allow_html=True)

# 数据加载辅助（修复了 KeyError 问题）
def load_all():
    default = {"briefs": [], "books": []}
    if not os.path.exists("data.json"): return default
    with open("data.json", "r", encoding="utf-8") as f:
        try:
            d = json.load(f)
            if "books" not in d: d["books"] = []
            if "briefs" not in d: d["briefs"] = []
            return d
        except: return default

data = load_all()

# --- 侧边导航 ---
st.sidebar.markdown("<h2 style='color:white; text-align:center;'>🏹 Read & Rise</h2>", unsafe_allow_html=True)
menu = st.sidebar.radio("", ["🏠 决策面板", "🚀 全球内参", "📚 资产智库"])

if menu == "🏠 决策面板":
    st.markdown("<h1>Executive Dashboard</h1>", unsafe_allow_html=True)
    st.write(f"更新时间：{data.get('update_time', 'Syncing...')}")
    
    if os.path.exists("daily_briefing.mp3"):
        st.audio("daily_briefing.mp3")
    
    st.divider()
    # 雷达图数据可视化
    if data['briefs']:
        art = data['briefs'][0]
        scores = art.get('model_scores', {"Strategy":80, "Innovation":70, "Execution":75})
        fig = go.Figure(data=go.Scatterpolar(
            r=list(scores.values())+[list(scores.values())[0]],
            theta=list(scores.keys())+[list(scores.keys())[0]],
            fill='toself', line=dict(color='#3B82F6')
        ))
        fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])), height=400, margin=dict(t=30, b=30))
        st.plotly_chart(fig, use_container_width=True)

elif menu == "🚀 全球内参":
    st.markdown("<h1>Global Intelligence</h1>", unsafe_allow_html=True)
    
    for i, art in enumerate(data.get("briefs", [])):
        with st.container():
            st.markdown(f"""
            <div class="executive-card">
                <span class="level-tag">{art.get('reading_level', 'General')}</span>
                <h2 style="margin-top:10px;">{art['title']}</h2>
                <p style="color:#94A3B8;">Source: {art['source']}</p>
                <div style="margin-bottom:20px;">
                    {" ".join([f'<span class="topic-tag">#{t}</span>' for t in art.get('tags', [])])}
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            t1, t2, t3 = st.tabs(["💡 中英深度解析", "🧠 反思流 (Reflections)", "🛠️ 行动建议"])
            with t1:
                col_en, col_cn = st.columns(2)
                with col_en:
                    st.markdown("**Executive Summary**")
                    st.write(art.get('en_summary', 'Generating...'))
                with col_cn:
                    st.markdown("**深度决策分析**")
                    st.write(art.get('cn_analysis', '解析生成中...'))
            with t2:
                for q in art.get('reflection_flow', []):
                    st.info(f"❓ {q}")
            with t3:
                for act in art.get('action_points', []):
                    st.success(f"✅ {act}")
            
            if st.button("📥 存入 Read & Rise 数字资产库", key=f"save_{i}"):
                data["books"].append({"title": art['title'], "insight": art['cn_analysis']})
                with open("data.json", "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=4)
                st.balloons()
