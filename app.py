import streamlit as st
import json, os

st.set_page_config(page_title="Read & Rise", layout="wide")

# --- 高级 UI 注入 ---
st.markdown("""
<style>
    .stApp { background-color: #F8FAFC; }
    .welcome-box { background: white; padding: 40px; border-radius: 24px; border-left: 10px solid #2563EB; box-shadow: 0 4px 20px rgba(0,0,0,0.05); }
    .vocab-card { background: #F1F5F9; padding: 10px; border-radius: 8px; margin: 5px 0; border-left: 3px solid #64748B; }
    .model-box { background: #EEF2FF; padding: 15px; border-radius: 12px; border: 1px dashed #6366F1; }
    .tag { background: #DBEAFE; color: #1E40AF; padding: 2px 8px; border-radius: 12px; font-size: 0.75rem; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

def load_data():
    if not os.path.exists("data.json"): return {"briefs": [], "books": []}
    with open("data.json", "r", encoding="utf-8") as f:
        return json.load(f)

data = load_data()

# --- 侧边栏 ---
st.sidebar.markdown("# 🏹 Read & Rise")
menu = st.sidebar.radio("Navigation", ["Dashboard", "Intelligent News", "Asset Bank"])

if menu == "Dashboard":
    st.markdown('<div class="welcome-box"><h1>Hi, Leaders! 👋</h1><p>Your strategic briefing is ready for today.</p></div>', unsafe_allow_html=True)
    st.write("")
    
    col1, col2 = st.columns([0.6, 0.4])
    with col1:
        st.subheader("🎙️ Global Briefing (BBC Accent)")
        if os.path.exists("daily_briefing.mp3"):
            st.audio("daily_briefing.mp3")
        
        st.divider()
        st.markdown("### 🔥 Top Strategic Pick")
        if data['briefs']:
            top = data['briefs'][0]
            st.markdown(f"**{top['en_title']}**")
            st.markdown(f"<span class='tag'>{top.get('reading_level')}</span>", unsafe_allow_html=True)
            st.write(top.get('cn_analysis'))
    
    with col2:
        st.subheader("🧠 Recommended Model")
        if data['briefs']:
            model = data['briefs'][0].get('mental_model', {})
            st.markdown(f"""<div class="model-box">
                <strong>{model.get('name')}</strong><br>
                <small>{model.get('logic')}</small>
            </div>""", unsafe_allow_html=True)

elif menu == "Intelligent News":
    for i, art in enumerate(data.get("briefs", [])):
        with st.container(border=True):
            st.markdown(f"### {art['en_title']}")
            st.caption(f"Source: {art['source']} | Level: {art['reading_level']}")
            
            tab1, tab2, tab3 = st.tabs(["Analysis", "Vocabulary", "Reflections"])
            with tab1:
                st.write(f"**CN Analysis:** {art['cn_analysis']}")
                st.info(f"**EN Summary:** {art['en_summary']}")
            with tab2:
                for v in art.get('vocabulary', []):
                    st.markdown(f"""<div class="vocab-card">
                        <strong>{v['word']}</strong> {v['phonetic']} <br>
                        <small>{v['meaning']} - <em>{v['example']}</em></small>
                    </div>""", unsafe_allow_html=True)
            with tab3:
                for r in art.get('reflection', []):
                    st.write(f"❓ {r}")
