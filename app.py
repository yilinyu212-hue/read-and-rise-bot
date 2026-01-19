import streamlit as st
import json, os

st.set_page_config(page_title="Read & Rise", layout="wide")

# --- 极简明亮 UI 样式 ---
st.markdown("""
<style>
    .stApp { background-color: #F8FAFC; }
    .welcome-card { background: white; padding: 40px; border-radius: 24px; border-left: 10px solid #2563EB; box-shadow: 0 10px 30px rgba(0,0,0,0.05); }
    .content-card { background: white; padding: 25px; border-radius: 16px; border: 1px solid #E2E8F0; margin-bottom: 20px; }
    .vocab-card { background: #F1F5F9; padding: 12px; border-radius: 10px; border-left: 4px solid #64748B; margin: 5px 0; }
    .type-tag { background: #DBEAFE; color: #1E40AF; padding: 2px 10px; border-radius: 20px; font-size: 0.75rem; font-weight: bold; }
    h1, h2, h3 { color: #1E293B !important; }
</style>
""", unsafe_allow_html=True)

def load_data():
    if not os.path.exists("data.json"): return {"items": []}
    with open("data.json", "r", encoding="utf-8") as f:
        return json.load(f)

data = load_data()

# --- 侧边栏 ---
st.sidebar.markdown("# 🏹 Read & Rise")
menu = st.sidebar.radio("模块导航", ["🏠 首页 Dashboard", "📚 智库详情 (包含音频)"])

if menu == "🏠 首页 Dashboard":
    st.markdown('<div class="welcome-card"><h1>Hi, Leaders! 👋</h1><p>今天为您准备了来自全球 10 大信源的简报及 5 本必读名著精华。</p></div>', unsafe_allow_html=True)
    
    st.write("")
    st.subheader("🔥 今日重点推荐 (Top Picks)")
    
    # 采用 2x2 网格展示推荐
    cols = st.columns(2)
    for idx, item in enumerate(data.get("items", [])[:4]):
        with cols[idx % 2]:
            st.markdown(f"""
            <div class="content-card">
                <span class="type-tag">{item.get('type')}</span>
                <h3 style="margin-top:10px;">{item.get('cn_title')}</h3>
                <p style="font-size:0.9rem; color:#64748B;">{item.get('en_title')}</p>
            </div>
            """, unsafe_allow_html=True)
            if st.button(f"查看详情与收听音频 #{idx}", key=f"goto_{idx}"):
                st.session_state.selected_item = item
                st.info("已在侧边栏选中，请点击『智库详情』查看")

elif menu == "📚 智库详情 (包含音频)":
    st.header("Intelligence & Audio Hub")
    
    items = data.get("items", [])
    if not items:
        st.warning("暂无同步数据，请检查 GitHub Actions 运行状态。")
    else:
        for i, item in enumerate(items):
            with st.expander(f"📍 [{item.get('type')}] {item.get('cn_title')} | {item.get('en_title')}"):
                
                # 🎙️ 独立音频播放
                if os.path.exists(item.get("audio_file", "")):
                    st.write("🎧 **AI 朗读播报 (听力练习):**")
                    st.audio(item.get("audio_file"))
                
                t1, t2, t3, t4 = st.tabs(["💡 深度解析", "📖 案例拆解", "❓ 反思流", "🔤 词汇卡"])
                
                with t1:
                    c1, c2 = st.columns(2)
                    c1.markdown("**Executive Summary (EN)**")
                    c1.info(item.get('en_summary'))
                    c2.markdown("**战略决策建议 (CN)**")
                    c2.success(item.get('cn_analysis'))
                
                with t2:
                    st.markdown("#### 🔍 相关案例应用")
                    st.write(item.get('case_study', '正在生成案例...'))
                
                with t3:
                    st.markdown("#### 🧠 领导力反思问题")
                    for q in item.get('reflection_flow', []):
                        st.info(f"❓ {q}")
                
                with t4:
                    st.markdown("#### 🔤 核心词汇卡片 (English Focus)")
                    for v in item.get('vocab_cards', []):
                        st.markdown(f"""<div class="vocab-card">
                            <strong>{v['word']}</strong> <small>{v.get('phonetic','')}</small><br>
                            <em>{v['meaning']}</em><br>
                            <small>Ex: {v['example']}</small>
                        </div>""", unsafe_allow_html=True)
