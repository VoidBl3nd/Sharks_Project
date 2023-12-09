import time
import streamlit as st
from streamlit_extras.switch_page_button import switch_page 
from backend.Sharks_streamlit_utils_v1 import order_and_hide_pages

#Initialize Streamlit
st.set_page_config(page_title="Sharky cruise builder", layout = "centered", page_icon= '🦈') # must happen before any streamlit code /!\
st.markdown('<style>div.block-container{padding-top:3rem;}</style>', unsafe_allow_html=True) # remove blank top space
order_and_hide_pages()

#Name the bookmark
save_name = st.text_input('Bookmark_name','',placeholder='Save this cruise',label_visibility='hidden')         

if save_name == '':
    st.error('Please enter a name for your bookmark')
else:
    #Save the bookmark
    st.session_state['_cruise_bookmarks_'][save_name] = dict()
    st.session_state['_cruise_bookmarks_'][save_name]['departure_country'] = st.session_state['_cruise_bookmarks_']['temp_save']['departure_country']
    st.session_state['_cruise_bookmarks_'][save_name]['departure_port'] = st.session_state['_cruise_bookmarks_']['temp_save']['departure_port']
    st.session_state['_cruise_bookmarks_'][save_name]['period_start'] = st.session_state['_cruise_bookmarks_']['temp_save']['period_start']
    st.session_state['_cruise_bookmarks_'][save_name]['period_end'] = st.session_state['_cruise_bookmarks_']['temp_save']['period_end']
    st.session_state['_cruise_bookmarks_'][save_name]['cruise_stages'] = st.session_state['_cruise_bookmarks_']['temp_save']['cruise_stages']
    st.session_state['_cruise_bookmarks_'][save_name]['waypoints'] = st.session_state['_cruise_bookmarks_']['temp_save']['waypoints']
    st.session_state['_cruise_bookmarks_'][save_name]['dfActivities_locations'] = st.session_state['_cruise_bookmarks_']['temp_save']['dfActivities_locations']
    st.success('Cruise saved !')
    time.sleep(1)
    switch_page('Bookmarks')