import streamlit as st
from backend import engine

st.set_page_config(page_title="Read & Rise | 高管内参", layout="wide")

st.title("🏹 Read & Rise: Global Insight for Educators")
st.markdown("---")

# 侧边栏：操作区
with st.sidebar:
    st.header("控制台")
    if st.button("🔄 同步全球外刊最新内参"):
        with st.spinner("DeepSeek 正在解析全球商业动察..."):
            st.session_state.articles = engine.sync_global_publications()
            st.success("同步完成！")

# 主界面显示
if "articles" in st.session_state:
    for art in st.session_state.articles:
        # 使用 Container 美化每一篇推文
        with st.container():
            # 1. 顶部爆点区
            st.subheader(f"🎯 {art.get('title', 'Loading...')}")
            
            # 2. 三段式布局
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown("#### 📘 [Read] 深度精读 (Bilingual Case)")
                # 这里展示中英双语和案例
                st.info(art.get('content', '解析生成中...'))
            
            with col2:
                st.markdown("#### 🚀 [Rise] 管理跃迁 (Action)")
                # 侧边栏展示思维模型和指令，用 code 块增强视觉感
                st.warning("🧠 核心思维模型\n\n**反脆弱 (Antifragility)**") 
                st.success("✅ 行动清单\n1. 停止过度避险\n2. 开启压力测试\n3. 布局冗余资源")

            st.markdown("---")
else:
    st.info("点击左侧按钮，开启今日的高管决策同步。")
