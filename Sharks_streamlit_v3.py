#Importer les packages nécessaires
import random
import numpy as np
import pandas as pd
import seaborn as sns
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date
import matplotlib.pyplot as plt

from backend.Sharks_streamlit_utils_v1 import get_session_state, order_and_hide_pages
from backend.Sharks_utils_v1 import compute_maritime_route, define_clusters, clean_clusters_centerpoints

sharks = get_session_state(['transformed_data/sharks'])[0]

#Initialize Streamlit
st.set_page_config(page_title="Sharky cruise builder", layout = "wide") # must happen before any streamlit code /!\
st.markdown('<style>div.block-container{padding-top:3rem;}</style>', unsafe_allow_html=True) # remove blank top space

order_and_hide_pages()
