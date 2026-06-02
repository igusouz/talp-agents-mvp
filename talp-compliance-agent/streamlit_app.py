"""
Interface Streamlit
"""

import streamlit as st

st.set_page_config(
    page_title="TALP Compliance Agent",
    page_icon="🔍",
    layout="wide",
)

st.title("🔍 TALP Compliance Agent")
st.markdown(
    """
Esta é a interface de demonstração do Compliance Agent.
A implementação completa virá em breve.
"""
)

col1, col2 = st.columns(2)

with col1:
    st.subheader("📊 Status")
    st.info("Sistema em desenvolvimento")

with col2:
    st.subheader("📝 Documentação")
    st.markdown("[API Docs](http://localhost:8000/docs)")
