import streamlit as st
import streamlit.components.v1 as components
from backend.Sharks_streamlit_utils_v1 import order_and_hide_pages

#Initialize Streamlit
st.set_page_config(page_title="Sharky cruise builder", layout = "wide") # must happen before any streamlit code /!\
st.markdown('<style>div.block-container{padding-top:3rem;}</style>', unsafe_allow_html=True) # remove blank top space
order_and_hide_pages()


with  open('landing_embedded.html','r', encoding='utf8') as HtmlFile:
    source_code = HtmlFile.read()
    components.html(source_code, scrolling= True, height = 800)######