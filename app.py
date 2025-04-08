
import streamlit as st

# Exemplo simples com st.rerun()
if "contagem" not in st.session_state:
    st.session_state.contagem = 0

st.write(f"Contagem atual: {st.session_state.contagem}")

if st.button("Aumentar"):
    st.session_state.contagem += 1
    st.rerun()
