import glob
import logging
import os
import re

import nltk
import pandas as pd
import streamlit as st
from streamlit.runtime.state import SessionState

logger = logging.getLogger(__name__)

session_state = SessionState()
DIM = 768
#nltk.download('punkt')
buffer = ""


# Main Config
st.set_page_config(layout="wide")
st.markdown("""
<style>
.title {
    font-size:50px !important;
    color: black;
}
</style>
""", unsafe_allow_html=True)

doc_cnt = 5
st.markdown('p class="title"> {} Transcribe Clusters </p>'.format(doc_cnt), unsafe_allow_html=True)

with st.form(key='Transcribe Audio'):
    st.write([], unsafe_allow_html=True)


