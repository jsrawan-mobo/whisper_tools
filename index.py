import os

import streamlit as st
#from st import Page, Section, show_pages, add_page_title


st.set_page_config(
    page_title="Reporter Tools",
    page_icon="👋",
)


st.write("# Reporter Tools App")

pages = [
    st.Page("./pages/transcribe_video_page.py", title="Transcribe Video"),
    st.Page("./pages/transcribe_video_page_2.py", title="TBD")
]



pg = st.navigation(pages)
st.set_page_config(page_title="Data manager", page_icon=":material/edit:")
pg.run()

st.sidebar.success("Select a demo above.")
transcribe_model_desc = '''::blue[_Transcribe and Translate_]'''

st.markdown(
    f"""
    **👈 Select a demo from the sidebar**
    
    **Recommendations use anonymized user data, please do not share**    
"""
)
